from django.shortcuts import render
# from django.http import HttpRequest, JsonResponse
# from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from authentication.models import Person
from medication.models import Medication, Take
from authentication.serializers import PersonSerializer
from medication.serializers import MedicationSerializer, TakeSerializer
from rest_framework import permissions, viewsets

# #add user, remove user, edit user, get user
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("person_id")
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        person, created = Person.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(person, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(user=request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def get_object(self):
        """Override get_object to enforce user isolation"""
        person = super().get_object()
        
        # Allow users to access only their own person data
        if person.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Você não pode acessar dados de outro usuário')
        
        return person
    
    def perform_update(self, serializer):
        """Only allow users to update their own person data"""
        person = self.get_object()
        if person.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Você não pode editar dados de outro usuário')
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only allow users to delete their own person data"""
        if instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Você não pode deletar dados de outro usuário')
        
        instance.delete()

# anvisa medications become read-only
class MedicationViewSet(viewsets.ReadOnlyModelViewSet):
    """ Determine Anvisa medications as read-only,
        Adition, edition and deletion are made with the command 'manage.py load_medications_data'
    """
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """filter medications"""
        queryset = Medication.objects.all()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(medication_id__icontains=search) |
                Q(name__name__icontains=search)
            ).distinct()
        return queryset

class TakeViewSet(viewsets.ModelViewSet):
    """ Create, edit, and delete user medications
    """
    queryset = Take.objects.all()
    serializer_class = TakeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas os Takes do usuário autenticado"""
        person = Person.objects.filter(user=self.request.user).first()
        if person:
            return Take.objects.filter(person_id=person).order_by("medication_id")
        return Take.objects.none()
    
    def create(self, request, *args, **kwargs):
        """duplicated medications"""
        person = Person.objects.filter(user=request.user).first()
        if not person:
            return Response(
                {'error': 'Usuário não tem registro de Person'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        medication_id = request.data.get('medication_id')
        
        # check if the medication already exists
        existing_take = Take.objects.filter(
            person_id=person,
            medication_id=medication_id
        ).exists()
        
        if existing_take:
            return Response(
                {'error': f'Você já está registrado como tomando este medicamento'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # check if the medication exist in the database
        if not Medication.objects.filter(medication_id=medication_id).exists():
            return Response(
                {'error': 'Medicamento não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Associates take and user"""
        person = Person.objects.filter(user=self.request.user).first()
        serializer.save(person_id=person)
    
    def perform_update(self, serializer):
        """edit only the user medication"""
        person = Person.objects.filter(user=self.request.user).first()
        take = self.get_object()
        
        if take.person_id != person:
            raise PermissionError('Você não pode editar medicamentos de outro usuário')
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """delete only the user medication"""
        person = Person.objects.filter(user=self.request.user).first()
        
        if instance.person_id != person:
            raise PermissionError('Você não pode deletar medicamentos de outro usuário')
        
        instance.delete()
      
    @action(detail=False, methods=['get'])
    def medications_with_leaflets(self, request):
        """return the user medications and their leaflet"""
        person = Person.objects.filter(user=request.user).first()
        if not person:
            return Response({'error': 'Usuário não tem registro de Person'}, status=status.HTTP_400_BAD_REQUEST)
        
        takes = Take.objects.filter(person_id=person).select_related('medication_id')
        medications = [take.medication_id for take in takes]
        
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data)

# @api_view(['GET'])
# def index(request):
#     return Response("OK")

# @api_view(["POST"])
# def create_user(request):
#     serializer = PersonSerializer(data = request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, 
#                         status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, 
#                     status = status.HTTP_400_BAD_REQUEST)