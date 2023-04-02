# Import statements
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .form import UserForm, BlogPostForm, CommentForm
from .models import BlogPost, CustomUser, Comment
from django.db.models import Count

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



def home(request):
    posts = BlogPost.objects.select_related('author').annotate(comment_count=Count('comments'))
    context = {'posts': posts}
    return render(request, 'main/index.html', context)
# def home(request):
#     posts = BlogPost.objects.select_related('author')
#     comment_posts = BlogPost.objects.select_related('author').annotate(comment_count=Count('comments'))

#     context = {'posts': posts, 'comment_counts':comment_posts}
#     return render(request, 'main/index.html', context)


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

# def UserProfile(request):
#     user = BlogPost.objects.select_related('author')

#     return render(request, 'main/userprofile.html', {'user':user})


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

# def UpdatePost(request, pk):
#     update_post = BlogPost.objects.get(id=pk)
#     updateform = BlogPostForm(instance=update_post)
#     context = {'update':update_post, 'form':updateform}

#     return render(request, 'main/create_post.html', context)

def update_post(request, pk):
    post = BlogPost.objects.get(id=pk)
    form = BlogPostForm(request.POST or None, instance=post)
    # if request.user != BlogPost.author:
    #     return HttpResponse('<h3>You are not allowed here</h3>')
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'main/create_post.html', {'form': form})

def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'main/delete_post.html', {'post': post})

def add_comment_to_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('home')
    else:
        form = CommentForm()
    return render(request, 'main/add_comment_to_post.html', {'form': form})

def ViewComment(request, pk):
    post = BlogPost.objects.get(pk=pk)
    # comment_count = post.comment_set.count()
    context ={}
    return render(request, 'main/index.html', context)
def logout_view(request):
    logout(request)
    return redirect('home')