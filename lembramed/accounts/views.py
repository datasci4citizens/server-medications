from django.shortcuts import render, redirect, redirect, get_object_or_404
from .models import New_Person
from .forms import NewPersonForm
from django.contrib.auth.hashers import check_password

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            person = New_Person.objects.get(email=email)
            if check_password(password, person.password):
                request.session['person_id'] = str(person.person_id)
                return redirect('medication_list')
            else:
                raise New_Person.DoesNotExist
        except New_Person.DoesNotExist:
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

