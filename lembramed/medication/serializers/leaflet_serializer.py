from rest_framework import serializers
from ..models import Leaflet, Medication

class LeafletSerializer(serializers.ModelSerializer):
    medication_id = serializers.PrimaryKeyRelatedField(
        queryset=Medication.objects.all(),
        source='medication',
        required=True
    )

    class Meta:
        model = Leaflet
        fields = [
            "medication_id",
            "indicacoes_para_uso",
            "funcionamento_medicamento",
            "quando_nao_usar",
            "conhecimento_previo_necessario",
            "como_guardar_medicamento",
            "como_usar_medicamento",
            "esqueceu_medicamento",
            "efeitos_colaterais",
            "quantidade_a_mais",
        ]
        extra_kwargs = {
            "indicacoes_para_uso": {'read_only':False, 'required':True},
            "funcionamento_medicamento": {'read_only':False, 'required':True},
            "quando_nao_usar": {'read_only':False, 'required':True},
            "conhecimento_previo_necessario": {'read_only':False, 'required':True},
            "como_guardar_medicamento": {'read_only':False, 'required':True},
            "como_usar_medicamento": {'read_only':False, 'required':True},
            "esqueceu_medicamento": {'read_only':False, 'required':True},
            "efeitos_colaterais": {'read_only':False, 'required':True},
            "quantidade_a_mais": {'read_only':False, 'required':False}
        }

    def to_internal_value(self, data):
        if hasattr(data, 'copy'):
            data = data.copy()
        else:
            data = dict(data)
        if 'medication' in data and 'medication_id' not in data:
            data['medication_id'] = data['medication']
        return super().to_internal_value(data)
