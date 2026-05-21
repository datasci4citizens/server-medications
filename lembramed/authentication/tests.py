from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
import uuid

from .models import Person



def create_user(email="user@example.com", password="StrongPass1!", first_name="João", last_name="Silva"):
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    return user


def auth_header(user):
    """Retorna o header Authorization com JWT access token."""
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {refresh.access_token}"}

# Model test

class PersonModelTest(TestCase):

    def test_person_created_automatically_on_user_creation(self):
        user = create_user()
        self.assertTrue(hasattr(user, "person"))
        self.assertIsInstance(user.person, Person)

    def test_person_primary_key_is_uuid(self):
        user = create_user()
        self.assertIsInstance(user.person.person_id, uuid.UUID)

    def test_person_str_returns_email(self):
        user = create_user()
        self.assertEqual(str(user.person), user.email)

    def test_person_birth_optional(self):
        user = create_user()
        self.assertIsNone(user.person.birth)

    def test_person_deleted_when_user_deleted(self):
        user = create_user()
        person_id = user.person.person_id
        user.delete()
        self.assertFalse(Person.objects.filter(person_id=person_id).exists())

# Register test

class RegisterViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("register")  

    def test_register_success(self):
        payload = {
            "email": "novo@example.com",
            "first_name": "Ana",
            "last_name": "Souza",
            "password": "StrongPass1!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn("tokens", data)
        self.assertIn("user", data)
        self.assertIn("access", data["tokens"])
        self.assertIn("refresh", data["tokens"])
        self.assertEqual(data["user"]["email"], payload["email"])

    def test_register_creates_user_and_person_in_db(self):
        payload = {
            "email": "db@example.com",
            "first_name": "Carlos",
            "last_name": "Lima",
            "password": "StrongPass1!",
        }
        self.client.post(self.url, payload, format="json")
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())
        user = User.objects.get(email=payload["email"])
        self.assertTrue(Person.objects.filter(user=user).exists())

    def test_register_with_birth(self):
        payload = {
            "email": "birth@example.com",
            "first_name": "Maria",
            "last_name": "Costa",
            "password": "StrongPass1!",
            "birth": "1990-05-20",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=payload["email"])
        self.assertEqual(str(user.person.birth), "1990-05-20")

    def test_register_duplicate_email_fails(self):
        create_user(email="dup@example.com")
        payload = {
            "email": "dup@example.com",
            "first_name": "X",
            "last_name": "Y",
            "password": "StrongPass1!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json())

    def test_register_missing_required_fields(self):
        response = self.client.post(self.url, {"email": "x@x.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password_fails(self):
        payload = {
            "email": "short@example.com",
            "first_name": "A",
            "last_name": "B",
            "password": "123",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email_fails(self):
        payload = {
            "email": "not-an-email",
            "first_name": "A",
            "last_name": "B",
            "password": "StrongPass1!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# Login test

class LoginViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("login") 
        self.user = create_user(email="login@example.com", password="StrongPass1!")

    def test_login_success(self):
        payload = {"email": "login@example.com", "password": "StrongPass1!"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("tokens", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], "login@example.com")

    def test_login_wrong_password(self):
        payload = {"email": "login@example.com", "password": "WrongPass!"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_email(self):
        payload = {"email": "ghost@example.com", "password": "AnyPass1!"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_password(self):
        payload = {"email": "login@example.com"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        payload = {"email": "login@example.com", "password": "StrongPass1!"}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# MeView tests  

class MeViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("me")  # ajuste o name da url se necessário
        self.user = create_user(email="me@example.com", password="StrongPass1!")
        self.client.credentials(**auth_header(self.user))

    def test_get_me_returns_user_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["email"], "me@example.com")
        self.assertEqual(data["first_name"], "João")

    def test_get_me_unauthenticated(self):
        self.client.credentials()  # remove token
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_me_updates_birth(self):
        payload = {"birth": "1995-08-15"}
        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.person.refresh_from_db()
        self.assertEqual(str(self.user.person.birth), "1995-08-15")

    def test_patch_me_invalid_birth_format(self):
        payload = {"birth": "not-a-date"}
        response = self.client.patch(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_me_unauthenticated(self):
        self.client.credentials()
        response = self.client.patch(self.url, {"birth": "2000-01-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# User deletion tests 

class UserDeletionTest(TestCase):

    def test_delete_user_also_deletes_person(self):
        user = create_user(email="del@example.com")
        person_id = user.person.person_id
        user.delete()
        self.assertFalse(User.objects.filter(email="del@example.com").exists())
        self.assertFalse(Person.objects.filter(person_id=person_id).exists())

    def test_delete_one_user_does_not_affect_others(self):
        user1 = create_user(email="keep@example.com")
        user2 = create_user(email="remove@example.com")
        user2.delete()
        self.assertTrue(User.objects.filter(email="keep@example.com").exists())
        self.assertTrue(Person.objects.filter(user=user1).exists())

# Google Auth test

class GoogleAuthViewTest(APITestCase):

    def setUp(self):
        self.url = reverse("google-auth")  

    @patch("authentication.views.id_token.verify_oauth2_token")
    def test_google_auth_new_user(self, mock_verify):
        mock_verify.return_value = {
            "sub": "google123",
            "email": "googleuser@gmail.com",
            "given_name": "Google",
            "family_name": "User",
        }
        response = self.client.post(self.url, {"token": "fake-google-token"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], "googleuser@gmail.com")
        self.assertTrue(User.objects.filter(email="googleuser@gmail.com").exists())

    @patch("authentication.views.id_token.verify_oauth2_token")
    def test_google_auth_existing_user(self, mock_verify):
        existing = create_user(email="googleuser@gmail.com")
        mock_verify.return_value = {
            "sub": "google456",
            "email": "googleuser@gmail.com",
            "given_name": "Google",
            "family_name": "User",
        }
        response = self.client.post(self.url, {"token": "fake-google-token"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        self.assertEqual(User.objects.filter(email="googleuser@gmail.com").count(), 1)

    @patch("authentication.views.id_token.verify_oauth2_token", side_effect=ValueError("bad token"))
    def test_google_auth_invalid_token(self, mock_verify):
        response = self.client.post(self.url, {"token": "invalid"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_google_auth_missing_token(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("authentication.views.id_token.verify_oauth2_token")
    def test_google_auth_saves_google_id(self, mock_verify):
        mock_verify.return_value = {
            "sub": "uniqueGoogleId",
            "email": "gid@gmail.com",
            "given_name": "G",
            "family_name": "ID",
        }
        self.client.post(self.url, {"token": "fake"}, format="json")
        user = User.objects.get(email="gid@gmail.com")
        self.assertEqual(user.person.google_id, "uniqueGoogleId")

# JWT token test

class JWTTokenTest(APITestCase):

    def setUp(self):
        self.user = create_user(email="jwt@example.com", password="StrongPass1!")

    def test_access_token_grants_access_to_protected_endpoint(self):
        me_url = reverse("me")
        self.client.credentials(**auth_header(self.user))
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_is_rejected(self):
        me_url = reverse("me")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalidtoken123")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_token_is_rejected(self):
        me_url = reverse("me")
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_returns_new_access_token(self):
        refresh_url = reverse("token_refresh")  
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(refresh_url, {"refresh": str(refresh)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())

# PersonViewSet

class PersonViewSetTest(APITestCase):
    """Testa o ViewSet exposto pelo router em /api/person/."""

    def setUp(self):
        from rest_framework.authtoken.models import Token
        self.user = create_user(email="vs@example.com", password="StrongPass1!")
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.list_url = "/api/users/"

    def test_list_persons_authenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_persons_unauthenticated(self):
        self.client.credentials()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_person(self):
        url = f"{self.list_url}{self.user.person.person_id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["email"], "vs@example.com")