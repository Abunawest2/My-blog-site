from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .form import UserForm
from .models import Blog

# def home(request):
#     form = UserForm()
#     if request.method == "POST":
#         form = UserForm(request.POST)
#         if form.is_valid():
#             try:
#                 form.save()
#             except Exception as e:
#                 print(e)
#     context = {'form':form}

#     return render(request, 'main/index.html', context)


def home(request):
    posts = Blog.objects.all()
    context = {'posts': posts}
    return render(request, 'main/index.html', context)

