from django import forms
from .models import Medication

class MedicationForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=Medication.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        label="Dias da semana"
    )
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'days', 'time', 'begin', 'end', 'format', 'quantity']
        widgets = {
            'begin': forms.DateInput(attrs={'type': 'date'}),
            'end': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
            'dosage': forms.TextInput(attrs={'placeholder': 'Enter the medication dosage'}),
            'format': forms.TextInput(attrs={'placeholder': 'Enter the type of medication (ex: pills)'}),
            'quantity': forms.TextInput(attrs={'placeholder': '(ex: number of pills, ml, etc.)'}),
        }
    
    def clean_days(self):
        days = self.cleaned_data['days']
        return ','.join(days)