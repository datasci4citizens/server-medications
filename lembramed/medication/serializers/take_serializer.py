from rest_framework import serializers
from ..models import Take, TakeRecord


class TakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Take
        fields = "__all__"
        read_only_fields = ["taken_id", "person_id"]


class TakeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TakeRecord
        fields = "__all__"
        read_only_fields = ["id"]