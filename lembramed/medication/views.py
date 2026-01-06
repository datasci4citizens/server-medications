from django.shortcuts import render, redirect
from .models import Medication
from .forms import MedicationForm

def medication_list(request):
    medications = Medication.objects.order_by('time') # order the medications by time of consumption
    return render(request, 'medication/list.html', {
        'medications': medications

    })

def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medication_list')
    else:
        form = MedicationForm()

    return render(request, 'medication/add.html',{
        'form': form

    })

