# views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .forms import UserForm, BlogPostForm
from .models import BlogPost, PostLike, CustomUser, Comment, CommentLike, Category


# Utility function to check if user is staff
def is_staff_user(user):
    return user.is_authenticated and user.is_staff


# Authentication Views
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


def SignIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next parameter if available
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            try:
                get_object_or_404(CustomUser, email=email)
                error_msg = "Incorrect password"
            except:
                error_msg = "Email does not exist"
            return render(request, 'main/login.html', {'error_msg': error_msg})
    else:
        return render(request, 'main/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# Home View
def home(request):
    """Display all blog posts with comments and search functionality"""
    posts_list = BlogPost.objects.select_related('author').prefetch_related(
        'comments__author',
        'comments__replies__author',
        'comments__likes'
    ).order_by('-date_updated', '-date_created')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) |
            Q(post__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        posts_list = posts_list.filter(category__name=category_filter)
    
    # Pagination
    paginator = Paginator(posts_list, 5)  # 5 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get categories
    categories = Category.objects.all()
    
    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.order_by('-date_created')[:5]
    
    context = {
        'posts': posts,
        'categories': categories,
        'recent_posts': recent_posts,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'main/index.html', context)


# Single Post View
def post_detail(request, pk):
    """Display a single blog post with all its comments"""
    post = get_object_or_404(
        BlogPost.objects.select_related('author').prefetch_related(
            'comments__author',
            'comments__replies__author',
            'comments__likes'
        ),
        pk=pk
    )
    
    # Get all top-level comments (not replies)
    comments = post.comments.filter(parent=None).order_by('-date_created')
    
    # Get related posts (same author or similar title)
    related_posts = BlogPost.objects.filter(
        author=post.author
    ).exclude(pk=post.pk).order_by('-date_created')[:3]
    liked_by_user = post.is_liked_by(request.user)
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'liked_by_user':liked_by_user
    }
    return render(request, 'main/post_detail.html', context)


# Search View
def search_posts(request):
    """Dedicated search page with advanced filtering"""
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    author_filter = request.GET.get('author', '')
    sort_by = request.GET.get('sort', '-date_created')
    
    posts_list = BlogPost.objects.select_related('author').prefetch_related('comments')
    
    # Apply search filter
    if search_query:
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) |
            Q(post__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        posts_list = posts_list.filter(category__name=category_filter)
    
    # Apply author filter
    if author_filter:
        posts_list = posts_list.filter(author__username=author_filter)
    
    # Apply sorting
    valid_sorts = ['-date_created', 'date_created', '-date_updated', 'title', '-title']
    if sort_by in valid_sorts:
        posts_list = posts_list.order_by(sort_by)
    else:
        posts_list = posts_list.order_by('-date_created')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get all categories and authors for filters
    categories = Category.objects.all()
    authors = CustomUser.objects.filter(blogpost__isnull=False).distinct()
    
    context = {
        'posts': posts,
        'categories': categories,
        'authors': authors,
        'search_query': search_query,
        'category_filter': category_filter,
        'author_filter': author_filter,
        'sort_by': sort_by,
        'total_results': posts_list.count(),
    }
    return render(request, 'main/search.html', context)


# Author Profile View
def author_profile(request, username):
    """Display author profile with their posts"""
    author = get_object_or_404(CustomUser, username=username)
    
    posts_list = BlogPost.objects.filter(author=author).order_by('-date_created')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get statistics
    total_posts = posts_list.count()
    total_comments = Comment.objects.filter(post__author=author).count()
    
    context = {
        'author': author,
        'posts': posts,
        'total_posts': total_posts,
        'total_comments': total_comments,
    }
    return render(request, 'main/author_profile.html', context)


# Category View
def category_posts(request, category_name):
    """Display all posts in a specific category"""
    category = get_object_or_404(Category, name=category_name)
    
    posts_list = BlogPost.objects.filter(
        category=category
    ).select_related('author').order_by('-date_created')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'main/category_posts.html', context)

@login_required
@require_POST
def toggle_post_like(request, post_pk):
    """Toggle like on a post (AJAX endpoint)"""
    post = get_object_or_404(BlogPost, pk=post_pk)
    
    try:
        # Check if user already liked the comment
        like = PostLike.objects.get(post=post, user=request.user)
        like.delete()
        liked = False
        message = 'Like removed'
    except PostLike.DoesNotExist:
        # Create new like
        PostLike.objects.create(post=post, user=request.user)
        liked = True
        message = 'Post liked'
    liked_by_user = post.is_liked_by(request.user)


    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': post.likes_count,
        'Liked_by_user':liked_by_user,
        'message': message
    })
# Blog Post Views
@login_required
@user_passes_test(is_staff_user, login_url='home')
def create_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(initial={'author': request.user})
    
    return render(request, 'main/create_post.html', {'form': form})


@login_required
@user_passes_test(is_staff_user, login_url='home')
def update_post(request, pk):
    post = get_object_or_404(BlogPost, id=pk)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'main/create_post.html', {'form': form})


@login_required
@user_passes_test(is_staff_user, login_url='home')
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" has been deleted successfully!')
        return redirect('home')
    
    return render(request, 'main/delete_post.html', {'post': post})


# Comment Views
@login_required
@require_POST
def add_comment_to_post(request, pk):
    """Add a top-level comment to a post"""
    post = get_object_or_404(BlogPost, pk=pk)
    comment_text = request.POST.get('comment_text', '').strip()
    
    if comment_text:
        Comment.objects.create(
            post=post,
            author=request.user,
            text=comment_text
        )
        messages.success(request, 'Your comment has been added!')
    else:
        messages.error(request, 'Comment cannot be empty.')
    
    # Redirect to the referring page or post detail
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'home'))
    return redirect(next_url)


@login_required
@require_POST
def add_reply_to_comment(request, comment_pk):
    """Add a reply to an existing comment"""
    parent_comment = get_object_or_404(Comment, pk=comment_pk)
    reply_text = request.POST.get('reply_text', '').strip()
    
    if reply_text:
        Comment.objects.create(
            post=parent_comment.post,
            author=request.user,
            text=reply_text,
            parent=parent_comment
        )
        messages.success(request, 'Your reply has been added!')
    else:
        messages.error(request, 'Reply cannot be empty.')
    
    # Redirect to the referring page
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'home'))
    return redirect(next_url)


@login_required
@require_POST
def delete_comment(request, comment_pk):
    """Delete a comment (only author or staff can delete)"""
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    # Check permissions
    if request.user == comment.author or request.user.is_staff:
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    else:
        messages.error(request, 'You do not have permission to delete this comment.')
    
    # Redirect to the referring page
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'home'))
    return redirect(next_url)


@login_required
@require_POST
def toggle_comment_like(request, comment_pk):
    """Toggle like on a comment (AJAX endpoint)"""
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    try:
        # Check if user already liked the comment
        like = CommentLike.objects.get(comment=comment, user=request.user)
        like.delete()
        liked = False
        message = 'Like removed'
    except CommentLike.DoesNotExist:
        # Create new like
        CommentLike.objects.create(comment=comment, user=request.user)
        liked = True
        message = 'Comment liked'
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': comment.likes_count,
        'message': message
    })


# User Dashboard (for logged-in users)
@login_required
def user_dashboard(request):
    """Display user's own posts and comments"""
    user_posts = BlogPost.objects.filter(author=request.user).order_by('-date_created')
    user_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-date_created')[:10]
    
    # Pagination for posts
    paginator = Paginator(user_posts, 5)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Statistics
    total_posts = user_posts.count()
    total_comments = Comment.objects.filter(author=request.user).count()
    total_comment_likes = CommentLike.objects.filter(comment__author=request.user).count()
    total_post_likes = CommentLike.objects.filter(comment__author=request.user).count()
    
    context = {
        'posts': posts,
        'recent_comments': user_comments,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_comment_likes': total_comment_likes,
        'total_post_likes': total_post_likes,
    }
    return render(request, 'main/dashboard.html', context)


# About Page
def about(request):
    """Display about page"""
    # Get some statistics
    total_posts = BlogPost.objects.count()
    total_authors = CustomUser.objects.filter(posts__isnull=False).distinct().count()
    total_comments = Comment.objects.count()
    
    context = {
        'total_posts': total_posts,
        'total_authors': total_authors,
        'total_comments': total_comments,
    }
    return render(request, 'main/about.html', context)


# Archive View
def archive(request):
    """Display posts by month/year"""
    from django.db.models.functions import TruncMonth
    
    # Get posts grouped by month
    posts_by_month = BlogPost.objects.annotate(
        month=TruncMonth('date_created')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')
    
    # Get selected month if provided
    selected_month = request.GET.get('month')
    posts_list = BlogPost.objects.all()
    
    if selected_month:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(selected_month, '%Y-%m')
            posts_list = posts_list.filter(
                date_created__year=date_obj.year,
                date_created__month=date_obj.month
            )
        except ValueError:
            pass
    
    posts_list = posts_list.order_by('-date_created')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'posts_by_month': posts_by_month,
        'selected_month': selected_month,
    }
    return render(request, 'main/archive.html', context)


# Legacy view - keeping for backwards compatibility
def ViewComment(request, pk):
    """View all comments for a specific post"""
    post = get_object_or_404(BlogPost, pk=pk)
    comments = post.comments.filter(parent=None).prefetch_related('replies')
    
    context = {
        'post': post,
        'comments': comments
    }
    return render(request, 'main/view_comments.html', context)