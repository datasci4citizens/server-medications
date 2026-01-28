from django import forms
from .models import New_Person

class NewPersonForm(forms.ModelForm):
    class Meta:
        model = New_Person
        fields = ['name', 'last_name', 'birth', 'email', 'password']
        widgets = {
            'birth': forms.DateInput(attrs={'type': 'date'}),
        }
