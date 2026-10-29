from rest_framework import serializers
from ..models import Presentation, AnvisaRegister, DosageIngredients, Formato
from ..serializers import ActiveIngredientSerializer
import re

FORMATO_RULES = (
    ("adesivo transdermico", re.compile(r"\bADES\s+TRANSD\b")),
    ("injetavel", re.compile(r"\b(?:SOL|SUS)\s+INJ\b")),
    ("inalatorio", re.compile(r"\b(?:P[ÓO]\s+)?INAL\b")),
    ("colirio", re.compile(r"\b(?:COL[ÍI]RIO|SOL\s+OFT)\b")),
    ("supositorio", re.compile(r"\bSUP(?:\s+RET)?\b")),
    ("capsula", re.compile(r"\bCAP\b")),
    ("comprimido", re.compile(r"\bCOM\b")),
    ("pomada", re.compile(r"\b(?:POM|UNG|CREM|GEL)\b")),
    ("liquido", re.compile(r"\b(?:XPE|SOL|SUS)\b")),
    ("granulado", re.compile(r"\bGRAN\b")),
)

class FormatoSerializer(serializers.ModelSerializer):
    formato = serializers.StringRelatedField()

    class Meta:
        model = Formato
        fields = ["formato"]

class AnvisaRegisterSerializer(serializers.ModelSerializer):
    expiration_date = serializers.DateField()

    class Meta:
        model = AnvisaRegister
        fields = [
            "register_num", "process_num", "expiration_date"
        ]
        extra_kwargs = {
            'register_num': {'read_only': False, 'required': True},
            'process_num': {'required': True},
        }

class DosageIngredientsSerializer(serializers.ModelSerializer):
    concentration_order = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="active_ingredient",
    )
    active_ingredient = ActiveIngredientSerializer()
    order = serializers.IntegerField()

    class Meta:
        model = DosageIngredients
        fields = [
            "active_ingredient","order"
        ]

class PresentationSerializer(serializers.ModelSerializer):
    register = serializers.PrimaryKeyRelatedField(
        queryset=AnvisaRegister.objects.all(),
        required=False,
        allow_null=True
    )
    formato = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    can_be_fractioned = serializers.BooleanField(default=False, required=False)
    embalagem = serializers.JSONField(required=False, default=dict)
    dosage = serializers.CharField(required=False, default="")
    administration = serializers.CharField(required=False, default="", allow_blank=True)
    conservation = serializers.CharField(required=False, default="", allow_blank=True)
    prescription_restriction = serializers.CharField(required=False, default="", allow_blank=True)
    usage_restriction = serializers.CharField(required=False, default="", allow_blank=True)
    label = serializers.CharField(required=False, default="", allow_blank=True)

    class Meta:
        model = Presentation
        fields = [
            "regulation_num", "register", "formato",
            "dosage", "embalagem", "administration",
            "conservation", "prescription_restriction",
            "usage_restriction", "label", "can_be_fractioned",
            "concentration_order"
        ]
        read_only_fields = ["concentration_order"]
        extra_kwargs = {
            'regulation_num': {'read_only': False, 'required': True},
        }

    def extract_formato(self, dosage: str) -> str | None:
        normalized = re.sub(r"\s+", " ", (dosage or "").upper()).strip()

        for formato, pattern in FORMATO_RULES:
            if pattern.search(normalized):
                return formato

        return None

    def to_internal_value(self, data):
        if hasattr(data, 'copy'):
            data = data.copy()
        else:
            data = dict(data)

        if isinstance(data.get('register'), dict):
            data['register'] = data['register'].get('register_num')

        if isinstance(data.get('formato'), dict):
            data['formato'] = data['formato'].get('formato')

        return super().to_internal_value(data)

    def create(self, validated_data):
        regulation_num_val = validated_data.pop('regulation_num')
        dosage_val = validated_data.get('dosage', '')

        # 1. Resolve register
        register_obj = validated_data.pop('register', None)
        if not register_obj and regulation_num_val:
            derived_num = int(regulation_num_val) // 10000
            register_obj = AnvisaRegister.objects.filter(register_num=derived_num).first()

        if not register_obj:
            raise serializers.ValidationError({
                "register": "Registro da ANVISA correspondente não encontrado. Informe um 'register' existente."
            })

        # 2. Resolve formato
        formato_str = validated_data.pop('formato', None)
        if not formato_str:
            formato_str = self.extract_formato(dosage_val) or "outros"

        formato_obj, _ = Formato.objects.get_or_create(formato=formato_str)

        presentation = Presentation.objects.create(
            regulation_num=regulation_num_val,
            register=register_obj,
            formato=formato_obj,
            **validated_data
        )

        return presentation

    def update(self, instance, validated_data):
        if 'register' in validated_data:
            instance.register = validated_data.pop('register')
        if 'formato' in validated_data:
            formato_val = validated_data.pop('formato') or "outros"
            formato_obj, _ = Formato.objects.get_or_create(formato=formato_val)
            instance.formato = formato_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['register'] = AnvisaRegisterSerializer(instance.register).data if instance.register else None
        data['formato'] = instance.formato.formato if instance.formato else None
        return data
