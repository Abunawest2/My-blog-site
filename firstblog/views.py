# Import statements
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .form import UserForm, BlogPostForm
from .models import BlogPost, CustomUser

# View functions
def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Registration is successful')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'Registration failed')
        else:
            context = {
                'form': form,
                'username_errors': form.errors.get('username', []),
                'email_errors': form.errors.get('email', []),
                'password1_errors': form.errors.get('password1', []),
                'password2_errors': form.errors.get('password2', []),
            }
            return render(request, 'main/forms.html', context)
    else:
        form = UserForm()
        context = {'form': form}
        return render(request, 'main/forms.html', context)


@login_required
def home(request):
    posts = BlogPost.objects.select_related('author')
    context = {'posts': posts}
    return render(request, 'main/index.html', context)


def SignIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            try:
                get_object_or_404(CustomUser, email=email)
                error_msg = "Incorrect password"
            except:
                error_msg = "Email does not exist"
            return render(request, 'main/login.html', {'error_msg': error_msg})
    else:
        return render(request, 'main/login.html')

@login_required
def create_post(request):
    form = BlogPostForm()
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = BlogPostForm(initial={'author': request.user})
    return render(request, 'main/create_post.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')