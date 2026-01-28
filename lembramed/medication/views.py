from django.shortcuts import render, redirect,get_object_or_404
from .models import Medication
from .forms import MedicationForm
from accounts.models import New_Person

def medication_list(request):
    person_id = request.session.get('person_id')

    if not person_id:
        return redirect('login_view')

    medications = Medication.objects.filter(
        person_id=person_id
    ).order_by('time')

    return render(request, 'medication/list.html', {
        'medications': medications
    })

def add_medication(request):
    person_id = request.session.get('person_id')

    if not person_id:
        return redirect('login_view')

    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            person_instance = get_object_or_404(New_Person, pk=person_id)
            medication.person_id = person_instance
            # medication.person_id = person_id # "Medication.person_id" must be a "New_Person" instance
            medication.save()
            return redirect('medication_list')
    else:
        form = MedicationForm()

    return render(request, 'medication/add.html', {
        'form': form
    })

def delete_medication(request,id):
    medication = get_object_or_404(Medication, pk=id)
    if request.method == 'POST':
        medication.delete()
        return redirect('medication_list')
    # return render(request, 'medications/confirm_delete.html', {'medication': medication})
    # put mechanic to delete the medication after the person takes the last dose]
