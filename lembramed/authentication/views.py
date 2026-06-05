from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, PersonSerializer

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from google.oauth2 import id_token
from google.auth.transport import requests
from .models import Person
from django.contrib.auth import logout
from django.shortcuts import redirect

import jwt
from jwt.algorithms import RSAAlgorithm
import requests as http_requests
from django.utils import timezone
from datetime import timedelta


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user':   PersonSerializer(user.person).data,
                'tokens': _tokens_for_user(user),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response({
                'user':   PersonSerializer(user.person).data,
                'tokens': _tokens_for_user(user),
            })

        if 'non_field_errors' in serializer.errors:
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MeView(APIView):
    """Return the loged users."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(PersonSerializer(request.user.person).data)

    def patch(self, request):
        person = request.user.person
        serializer = PersonSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        google_token = request.data.get('token')

        if not google_token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                google_token, 
                requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )

            # Get user information from the token
            google_id = idinfo['sub']
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            profile_picture = idinfo.get('picture', '')

            # Check if user exists, create if not
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create a new user
                username = email.split('@')[0]
                # Make sure username is unique
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{google_id[:8]}"

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )

            # Update or create person
            person, created = Person.objects.get_or_create(user=user)
            person.google_id = google_id
            person.save()

            # Create or get authentication token
            token = _tokens_for_user(user)

            # Return user data and token
            return Response({
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'picture': person.profile_picture.url if person.profile_picture else None
                }
            })

        except ValueError:
            # Invalid token
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Person.objects.all()

    def get(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'id': user.id,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}".strip(),
            'picture': user.person.profile_picture if hasattr(user, 'person') else None
        })


# apple login
class AppleAuthView(APIView):
    permission_classes = [AllowAny]
    def _get_apple_public_key(self, kid):
            """Busca dinamicamente a chave pública da Apple para validar a assinatura do token."""
            try:
                apple_keys_url = "https://appleid.apple.com/auth/keys"
                response = http_requests.get(apple_keys_url).json()
                for key in response.get("keys", []):
                    if key["kid"] == kid:
                        # Convert Apple's JWK in a publick Key
                        return RSAAlgorithm.from_jwk(key)
            except Exception:
                return None
            return None

    def post(self, request):
        apple_token = request.data.get('token')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not apple_token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            unverified_header = jwt.get_unverified_header(apple_token)
            kid = unverified_header.get('kid')

            public_key = self._get_apple_public_key(kid)
            if not public_key:
                return Response({'error': 'Unable to verify Apple public key'}, status=status.HTTP_400_BAD_REQUEST)

            idinfo = jwt.decode(
                apple_token,
                public_key,
                audience=settings.APPLE_CLIENT_ID,
                algorithms=['RS256']
            )

            apple_id = idinfo['sub']
            email = idinfo.get('email')

            if not email:
                email = f"{apple_id}@apple.relay"

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = f"apple_{apple_id[:10]}"
                if User.objects.filter(username=username).exists():
                    username = f"{username}_{timezone.now().strftime('%M%S')}"

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )

            person, created = Person.objects.get_or_create(user=user)

            if hasattr(person, 'apple_id'):
                person.apple_id = apple_id
            person.save()
            tokens = _tokens_for_user(user)

            return Response({
                'tokens': tokens,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip() or "Usuário Apple",
                    'picture': person.profile_picture if hasattr(person, 'profile_picture') else None
                }
            }, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Apple token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid Apple token'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)