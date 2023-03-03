from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .form import UserRegistrationForm

def home(request):
    form = UserRegistrationForm()
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                print(e)
    context = {'form':form}
    return render(request, 'main/index.html', context)

