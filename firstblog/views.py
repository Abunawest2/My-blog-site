from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .form import UserForm
from .models import BlogPost

def signup(request):
    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except Exception as e:
                print(e)
            user = form.cleaned_data.get('username')
            messages.success(request, 'Registerion is successful')
            return redirect('/')
        else:
            form = UserForm()
            messages.error(request, 'Registerion fails')

    context = {'form':form}

    return render(request, 'main/forms.html', context)


def home(request):
    posts = BlogPost.objects.all()
    context = {'posts': posts}
    return render(request, 'main/index.html', context)

