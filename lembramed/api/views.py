# from django.shortcuts import render
# # from django.http import HttpRequest, JsonResponse
# # from django.views.decorators.http import require_POST, require_GET
# from django.contrib.auth.models import Group, User
# from django.core.exceptions import ObjectDoesNotExist
# from rest_framework.decorators import api_view
# from rest_framework.response import Response

from authentication.models import Person
from medication.models import Leaflet,Medication
from authentication.serializers import PersonSerializer
from medication.serializers import LeafletSerializer,MedicationSerializer
from rest_framework import permissions,viewsets

# add user, remove user, edit user, get user
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("person_id")
    serializer_class = PersonSerializer
    permission_classes = [permissions.IsAuthenticated]

# add drug, remove drug, edit drug, get drug
class LeafletViewSet(viewsets.ModelViewSet):
    queryset = Leaflet.objects.all().order_by("medication_id")
    serializer_class = LeafletSerializer
    permission_classes = [permissions.IsAuthenticated]

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all().order_by("medication_id")
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]

# class TakeViewSet(viewsets.ModelViewSet):
#     queryset = Take.objects.all().order_by("medication_id")
#     serializer_class = TakeSerializer
#     permission_classes = [permissions.IsAuthenticated]

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