from django.db import transaction
from rest_framework import serializers
from ..models import Take, TakeRecord

class TakeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TakeRecord
        fields = ['id', 'cycle_type', 'begin', 'end', 'days', 'take_at', 'take_cycle']
        read_only_fields = ['id']

    def validate(self, attrs):
        if not attrs.get('begin') or not attrs.get('cycle_type'):
            raise serializers.ValidationError('Informe início e tipo de agendamento.')
        if attrs.get('end') and attrs['end'] < attrs['begin']:
            raise serializers.ValidationError('A data final deve ser posterior ao início.')
        if not attrs.get('take_at'):
            raise serializers.ValidationError('Informe o horário da dose.')
        if attrs.get('cycle_type') == 'interval' and (attrs.get('take_cycle') or 0) <= 0:
            raise serializers.ValidationError('Informe um intervalo positivo.')
        days = (attrs.get('days') or '').split(',')
        if any(day not in {'mon','tue','wed','thu','fri','sat','sun'} for day in days):
            raise serializers.ValidationError('Selecione dias válidos.')
        return attrs

class TakeSerializer(serializers.ModelSerializer):
    records = TakeRecordSerializer(many=True, required=True, allow_empty=False)
    medication_name = serializers.CharField(source='medication_id.name.name', read_only=True, default=None)
    medication_brand = serializers.CharField(source='medication_id.brand.brand', read_only=True, default=None)
    person_id = serializers.PrimaryKeyRelatedField(read_only=True)
    client_id = serializers.CharField(required=False, allow_blank=True, max_length=100)
    type = serializers.ChoiceField(choices=['tablet','capsule','liquid','injection'], required=False)

    class Meta:
        model = Take
        fields = ['taken_id','person_id','medication_id','medication_name','medication_brand',
                  'client_id','quantity','priority','records','dosage','brand','type',
                  'stock_reminder_enabled','stock_reminder_threshold','dose_status']
        read_only_fields = ['taken_id']
        validators = []  # Ownership and idempotency are handled against the authenticated person.

    def validate_dose_status(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('Histórico inválido.')
        for record in value.values():
            if not isinstance(record, dict) or record.get('status') not in {'taken','taken_late','skipped'}:
                raise serializers.ValidationError('Estado da dose inválido.')
            if record.get('takenAt'):
                serializers.DateTimeField().run_validation(record['takenAt'])
        return value

    @transaction.atomic
    def create(self, validated_data):
        records = validated_data.pop('records')
        client_id = validated_data.get('client_id')
        if client_id:
            existing = Take.objects.filter(person_id=validated_data['person_id'], client_id=client_id).first()
            if existing:
                return self.update(existing, validated_data | {'records': records})
        take = Take.objects.create(**validated_data)
        for record in records:
            TakeRecord.objects.create(taken_id=take, **record)
        return take

    @transaction.atomic
    def update(self, instance, validated_data):
        records = validated_data.pop('records', None)
        validated_data.pop('client_id', None)
        instance = super().update(instance, validated_data)
        if records is not None:
            instance.records.all().delete()
            for record in records:
                TakeRecord.objects.create(taken_id=instance, **record)
        return instance
