from authentication.models import Person
from medication.models import Medication, Leaflet, Presentation, AnvisaRegister, DosageIngredients
from authentication.serializers import PersonSerializer
from medication.serializers import (
    MedicationSerializer, LeafletSerializer,
    PresentationSerializer, DosageIngredientsSerializer
)
from rest_framework import permissions,viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from authentication.permissions import IsAdmin, IsPatient, IsPharmacist

class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by("person_id")
    serializer_class = PersonSerializer
    http_method_names = ["get", "delete"]

    def get_permissions(self):
        if self.action in ("destroy", "create", "list"):
            return [IsAdmin()]
        return [IsPatient or IsPharmacist] # partial_update or retrieve

class DrugView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        medication_id = request.data.get("medication_id")
        process_num = request.data.get("process_num")

        if not medication_id:
            return Response(
                {"error": 'Field "medication_id" is necessary'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not process_num:
            return Response(
                {"error": 'Field "process_num" is necessary'},
                status=status.HTTP_400_BAD_REQUEST
            )

        medication = Medication.objects.get(
            medication_id=medication_id
        )
        leaflet = Leaflet.objects.get(
            medication_id=medication_id
        )
        anvisa_register = AnvisaRegister.objects.get(
            process_num=process_num
        )

        # presentation = multiple presentation objects from the anvisa_register
        presentations = [
                p for p in Presentation.objects.filter(
                register=anvisa_register
        )]

        dosage_ingredients = []
        num_of_prescriptions = len(dosage_ingredients)
        while(num_of_prescriptions > 0):
            dosage_ingredients.append(
                DosageIngredients.objects.filter(
                    presentations=presentations[num_of_prescriptions]
                )
            )
            num_of_prescriptions -= 1

        # isnt presentations going to be a list of presentatinos objects?
        if not medication or not leaflet or not presentations:
            return Response(
                {"error": "Drug non existent."},
                status=status.HTTP_404_NOT_FOUND
        )

        # how to make so the dosage_ingredients field on output gets placed right beneath
        return Response({
            "medication": MedicationSerializer(medication).data,
            "leaflet": LeafletSerializer(leaflet).data,
            "presentations": PresentationSerializer(presentations, many=True).data,
        })
