from django.shortcuts import get_object_or_404
from django.http import Http404
import re
from drf_spectacular.utils import extend_schema
from rest_framework import permissions,viewsets,filters
from .serializers import (
    LeafletSerializer, MedicationSerializer,
    PresentationSerializer, AnvisaRegisterSerializer,
    TakeSerializer, TakeRecordSerializer,
    ingredientInteractionSerializer
)
from .models import (
    Leaflet, Medication, Presentation, Take, AnvisaRegister,
    TakeRecord, ingredient_Interaction
)

@extend_schema(tags=["leaflet"])
class LeafletViewSet(viewsets.ModelViewSet):
    queryset = Leaflet.objects.all().order_by("medication_id")
    serializer_class = LeafletSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all().order_by("medication_id")
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    filter_backends = [filters.SearchFilter]
    # search_fields = ['name', 'active_ingredient', 'register_number']
    search_fields = [
        'name__name',
        'active_ingredients__active_ingredient',
        'brand__brand',
        'company__company',
        'therapeutic_class__therapeutic_class',
    ]

@extend_schema(tags=["anvisa_register"])
class AnvisaRegisterViewSet(viewsets.ModelViewSet):
    queryset = AnvisaRegister.objects.all().order_by("process_num")
    serializer_class = AnvisaRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        qs = super().get_queryset()
        process_num = self.request.query_params.get("process_num")
        if process_num:
            clean_pn = re.sub(r"\D", "", str(process_num))
            if clean_pn:
                qs = qs.filter(process_num=int(clean_pn))
        return qs

    def get_object(self):
        lookup_val = self.kwargs[self.lookup_field]
        queryset = self.filter_queryset(self.get_queryset())

        clean_val = re.sub(r"\D", "", str(lookup_val))
        if not clean_val:
            raise Http404("Invalid ID format.")

        val_int = int(clean_val)

        obj = None
        if val_int <= 2147483647:
            obj = queryset.filter(register_num=val_int).first()

        # If not found or if it's a 17-digit process_num
        if not obj:
            obj = queryset.filter(process_num=val_int).first()

        if not obj:
            raise Http404("AnvisaRegister not found.")

        self.check_object_permissions(self.request, obj)
        return obj

@extend_schema(tags=["presentation"])
class PresentationViewSet(viewsets.ModelViewSet):
    queryset = Presentation.objects.all().order_by("regulation_num")
    serializer_class = PresentationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

@extend_schema(tags=["take"])
class TakeViewSet(viewsets.ModelViewSet):
    queryset = Take.objects.all().order_by("taken_id")
    serializer_class = TakeSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

@extend_schema(tags=["take_record"])
class TakeRecordViewSet(viewsets.ModelViewSet):
    queryset = TakeRecord.objects.all().order_by("taken_id")
    serializer_class = TakeRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

@extend_schema(tags=["ingredient_interaction"])
class ingredientInteractionViewSet(viewsets.ModelViewSet):
    queryset = ingredient_Interaction.objects.all().order_by("severity")
    serializer_class = ingredientInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"] # should it be able do edit?
    