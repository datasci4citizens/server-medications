from django.shortcuts import render, redirect, redirect, get_object_or_404
from .models import New_Person
from .forms import NewPersonForm


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_exists = New_Person.objects.filter(
            email=email,
            password=password
        ).exists()

        if user_exists:
            return redirect('medication_list')

        return render(request, 'accounts/loginpage.html', {
            'error': 'Email ou senha inválidos'
        })
    return render(request, 'accounts/loginpage.html')
    
    
def add_person(request):
    if request.method =='POST' :
        form = NewPersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_view') 
    else:
        form = NewPersonForm()
    
    return render(request, 'accounts/sing.html',{
        'form': form
    })

