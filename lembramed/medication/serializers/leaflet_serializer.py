from rest_framework import serializers
from ..models import Leaflet

class LeafletSerializer(serializers.ModelSerializer):
    # olhar campo
    class Meta:
        model = Leaflet
        fields = [
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