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
        fields = ['name', 'dosage', 'days', 'time', 'begin', 'end']
        widgets = {
            'begin': forms.DateInput(attrs={'type': 'date'}),
            'end': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            # 'name': forms.TextInput(attrs={'placeholder': 'Enter your name'}),
        }
    
    def clean_days(self):
        days = self.cleaned_data['days']
        return ','.join(days)