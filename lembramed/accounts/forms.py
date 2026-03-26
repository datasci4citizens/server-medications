from django import forms
from .models import New_Person

class NewPersonForm(forms.ModelForm):
    class Meta:
        model = New_Person
        fields = ['name', 'last_name', 'birth', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter your last name'}),
            'birth': forms.DateInput(attrs={'type': 'date'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter_you_email_here@gmail.com'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Enter your password here'}),
        }
