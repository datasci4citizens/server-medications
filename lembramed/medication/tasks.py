
from medication.models import TakeRecord  # ← topo do arquivo

def notify_user(take_record_id):
    rec = TakeRecord.objects.get(pk=take_record_id)
    medication = rec.taken_id.medication_id
    medication_name = medication.name.first()
    if medication_name:
        name = medication_name.name
    else:
        name = f"medicamento {medication.medication_id}"
    print(f"Hora de tomar: {name}")