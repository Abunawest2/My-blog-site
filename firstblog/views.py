# views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from blogproject import settings
from .forms import UserForm, BlogPostForm, ContactForm, UserSettingsForm, ChangePasswordForm, AuthorApplicationForm, NewCategoryForm, AuthorProfileForm

from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail, EmailMessage
from .models import BlogPost, PostLike, CustomUser, SuperCategory, SubCategory, UserPostView, Comment, CommentLike, Category, Notification
from django.db.models import F

def get_all_children(category):
    """Recursively get all children of a category."""
    children = [category]
    for child in category.children.all():
        children.extend(get_all_children(child))
    return children

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = f"Contact Form Submission from {name}"
            body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            
            email_message = EmailMessage(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL, # From
                [settings.CONTACT_FORM_RECIPIENT_EMAIL], # To
                reply_to=[email], # Set the Reply-To header
            )
            email_message.send(fail_silently=False)

            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'main/contact.html', {'form': form})


# Utility function to check if user is an author
def is_author(user):
    return user.is_authenticated and hasattr(user, 'author_profile')


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
            return render(request, 'main/signup.html', context)
    else:
        form = UserForm()
        context = {'form': form}
        return render(request, 'main/signup.html', context)


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
                error_msg = "Invalid Credentials!!"
            except:
                error_msg = "Invalid Credentials!!"
            return render(request, 'main/login.html', {'error_msg': error_msg})
    else:
        return render(request, 'main/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')
    return render(request, 'account/logout.html')


# Home View
def home(request):
    """Display all blog posts with comments and search functionality"""
    posts_list = BlogPost.objects.filter(status='published').select_related('author', 'category__sub_category__super_category').prefetch_related(
        'comments__author',
        'comments__replies__author',
        'comments__likes',
    ).order_by('-date_updated', '-date_created')

    # Build a mapping from post pk to whether the current user liked the post
    liked_by_user = {str(post.pk): post.is_liked_by(request.user) for post in posts_list}
    
    # Get all comments for the posts and check which ones are liked by the user
    if request.user.is_authenticated:
        comment_ids = [comment.id for post in posts_list for comment in post.comments.all()]
        liked_comment_ids = set(CommentLike.objects.filter(
            user=request.user, 
            comment_id__in=comment_ids
        ).values_list('comment_id', flat=True))
    else:
        liked_comment_ids = set()
    
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
        try:
            sub_category = SubCategory.objects.get(slug__iexact=category_filter)
            posts_list = posts_list.filter(category__sub_category=sub_category)
        except SubCategory.DoesNotExist:
            posts_list = posts_list.none()
    
    # Pagination
    paginator = Paginator(posts_list, 5)  # 5 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get categories for hierarchical display
    sub_categories_with_posts = SubCategory.objects.filter(
        categories__posts__status='published'
    ).distinct().select_related('super_category').annotate(
        post_count=Count('categories__posts')
    )
    
    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.filter(status='published').order_by('-date_created')[:5]

    # Get popular posts for sidebar
    popular_posts = BlogPost.objects.filter(status='published').annotate(like_count=Count('post_likes'),popularity_score=F('view_count') + Count('post_likes') * 10).order_by('-popularity_score')[:5]

    context = {
        'posts': posts,
        'sub_categories': sub_categories_with_posts,
        'recent_posts': recent_posts,
        'popular_posts': popular_posts,
        'search_query': search_query,
        'category_filter': category_filter,
        'liked_by_user': liked_by_user,
        'liked_comment_ids': liked_comment_ids,
    }
    return render(request, 'main/index.html', context)


# Single Post View
def post_detail(request, pk):
    """Display a single blog post with all its comments"""
    post = get_object_or_404(BlogPost, pk=pk)

    if (post.status == 'draft' and post.author != request.user and not request.user.is_staff) or \
       (post.status == 'archived' and not (request.user == post.author or request.user.is_superuser)):
        messages.error(request, "You do not have permission to view this post.")
        return redirect('home')

    # Increment view count and track user view
    post.increment_view_count(request.user)
    
    # Rest of your existing post_detail view code...
    comments = post.comments.filter(parent=None).order_by('-date_created')
    related_posts = BlogPost.objects.filter(
        author=post.author
    ).exclude(pk=post.pk).order_by('-date_created')[:3]
    
    liked_by_user = post.is_liked_by(request.user)
    
    if request.user.is_authenticated:
        liked_comment_ids = set(post.comments.filter(likes__user=request.user).values_list('id', flat=True))
    else:
        liked_comment_ids = set()
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'liked_by_user': liked_by_user,
        'liked_comment_ids': liked_comment_ids,
    }
    return render(request, 'main/post_detail.html', context)

# Search View
def search_posts(request):
    """Dedicated search page with advanced filtering"""
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    author_filter = request.GET.get('author', '')
    sort_by = request.GET.get('sort', '-date_created')
    
    posts_list = BlogPost.objects.filter(status='published').select_related('author', 'category__sub_category__super_category')
    
    # Apply search filter
    if search_query:
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) |
            Q(post__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        posts_list = posts_list.filter(
            Q(category__name__iexact=category_filter) |
            Q(category__sub_category__name__iexact=category_filter) |
            Q(category__sub_category__super_category__name__iexact=category_filter)
        )
    
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
    super_categories = SuperCategory.objects.prefetch_related('sub_categories__categories').all()
    authors = CustomUser.objects.filter(blogpost__isnull=False).distinct()
    
    context = {
        'posts': posts,
        'super_categories': super_categories,
        'authors': authors,
        'search_query': search_query,
        'category_filter': category_filter,
        'author_filter': author_filter,
        'sort_by': sort_by,
        'total_results': posts_list.count(),
    }
    return render(request, 'main/search.html', context)


@login_required
def create_category(request):
    if request.method == 'POST':
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            super_category = form.cleaned_data['super_category']
            sub_category_name = form.cleaned_data['sub_category_name']
            category_name = form.cleaned_data['category_name']
            
            sub_category, _ = SubCategory.objects.get_or_create(
                super_category=super_category,
                name=sub_category_name
            )
            category, _ = Category.objects.get_or_create(
                sub_category=sub_category,
                name=category_name
            )
            messages.success(request, 'New category created successfully!')
            return redirect('create_post')
    else:
        form = NewCategoryForm()
    
    return render(request, 'main/create_category.html', {'form': form})

@login_required
def author_profile(request, username):
    author = get_object_or_404(CustomUser, username=username)
    author_profile_instance = getattr(author, 'author_profile', None)

    if request.method == 'POST' and request.user == author:
        form_type = request.POST.get('form_type')
        if form_type == 'user_settings':
            user_form = UserSettingsForm(request.POST, instance=author)
            password_form = ChangePasswordForm(author)
            author_profile_form = AuthorProfileForm(instance=author_profile_instance) if author_profile_instance else None
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('author_profile', username=author.username)
        elif form_type == 'change_password':
            user_form = UserSettingsForm(instance=author)
            password_form = ChangePasswordForm(author, request.POST)
            author_profile_form = AuthorProfileForm(instance=author_profile_instance) if author_profile_instance else None
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('author_profile', username=author.username)
        elif form_type == 'author_profile' and author_profile_instance:
            user_form = UserSettingsForm(instance=author)
            password_form = ChangePasswordForm(author)
            author_profile_form = AuthorProfileForm(request.POST, request.FILES, instance=author_profile_instance)
            if author_profile_form.is_valid():
                author_profile_form.save()
                messages.success(request, 'Your author profile has been updated successfully!')
                return redirect('author_profile', username=author.username)
        else:
            # Fallback for GET or invalid form_type
            user_form = UserSettingsForm(instance=author)
            password_form = ChangePasswordForm(author)
            author_profile_form = AuthorProfileForm(instance=author_profile_instance) if author_profile_instance else None
    else:
        # GET request
        user_form = UserSettingsForm(instance=author)
        password_form = ChangePasswordForm(author)
        author_profile_form = AuthorProfileForm(instance=author_profile_instance) if author_profile_instance else None

    posts_list = BlogPost.objects.filter(author=author).exclude(status='archived')
    if request.user != author:
        posts_list = posts_list.filter(status='published')
    posts_list = posts_list.order_by('-date_created')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    total_posts = posts_list.count()
    total_comments = Comment.objects.filter(post__author=author).count()
    author_categories = Category.objects.filter(posts__author=author).distinct().select_related('sub_category__super_category')
    related_posts = BlogPost.objects.filter(category__in=author_categories).exclude(author=author).distinct().order_by('-date_created')[:5]
    suggested_topics = None
    if not author.is_author:
        liked_posts_sub_categories = SubCategory.objects.filter(categories__posts__post_likes__user=author).distinct().select_related('super_category')
        commented_posts_sub_categories = SubCategory.objects.filter(categories__posts__comments__author=author).distinct().select_related('super_category')
        suggested_topics = (liked_posts_sub_categories | commented_posts_sub_categories).distinct()

    context = {
        'author': author,
        'posts': posts,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'related_posts': related_posts,
        'suggested_topics': suggested_topics,
        'user_form': user_form,
        'password_form': password_form,
        'author_profile_form': author_profile_form,
    }
    return render(request, 'main/author_profile.html', context)


# Category View
def category_posts(request, category_slug):
    """Display all posts in a specific category"""
    sub_category = get_object_or_404(SubCategory, slug__iexact=category_slug)
    
    posts_list = BlogPost.objects.filter(status='published', category__sub_category=sub_category).select_related('author')
        
    posts_list = posts_list.order_by('-date_created')
    
    # Pagination
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'category': sub_category,
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
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb='liked',
                target=post
            )
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
@user_passes_test(is_author, login_url='home')
def create_post(request):
    super_categories = SuperCategory.objects.prefetch_related('sub_categories__categories').all()
    if request.method == 'POST':
        if 'create_category' in request.POST:
            new_category_form = NewCategoryForm(request.POST)
            if new_category_form.is_valid():
                super_category = new_category_form.cleaned_data['super_category']
                sub_category_name = new_category_form.cleaned_data['sub_category_name']
                category_name = new_category_form.cleaned_data['category_name']
                
                sub_category, _ = SubCategory.objects.get_or_create(
                    super_category=super_category,
                    name=sub_category_name
                )
                category, _ = Category.objects.get_or_create(
                    sub_category=sub_category,
                    name=category_name
                )
                messages.success(request, 'New category created successfully!')
                return redirect('create_post')
        else:
            form = BlogPostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                if request.user.is_staff:
                    post.status = 'published'
                    messages.success(request, 'Post created and published successfully!')
                else:
                    post.status = 'draft'
                    messages.success(request, 'Post submitted for review successfully!')
                post.save()
                return redirect('post_detail', pk=post.pk)
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(initial={'author': request.user})
    
    new_category_form = NewCategoryForm()
    return render(request, 'main/create_update_post.html', {'form': form, 'super_categories': super_categories, 'new_category_form': new_category_form})


@login_required
def update_post(request, pk):
    post = get_object_or_404(BlogPost, id=pk)
    
    if not (
        request.user.is_superuser or 
        request.user == post.author or 
        (request.user.is_staff and not post.author.is_staff)
    ):
        messages.error(request, "You do not have permission to edit this post.")
        return redirect('post_detail', pk=post.pk)

    super_categories = SuperCategory.objects.prefetch_related('sub_categories__categories').all()
    
    if request.method == 'POST':
        old_status = post.status # Get the old status before saving the form
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save() # Save the form to update the post object
            messages.success(request, 'Post updated successfully!')

            # Create a notification if the post is published
            if old_status == 'draft' and post.status == 'published':
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    verb='published',
                    target=post
                )

            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'main/create_update_post.html', {'form': form, 'super_categories':super_categories})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    
    if not (request.user == post.author or request.user.is_superuser):
        messages.error(request, "You do not have permission to delete this post.")
        return redirect('post_detail', pk=post.pk)

    if request.method == 'POST':
        post_title = post.title
        post.status = 'archived'
        post.save()
        messages.success(request, f'Post "{post_title}" has been archived successfully!')
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
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            text=comment_text
        )
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                actor=request.user,
                verb='commented on',
                target=post
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
        if parent_comment.author != request.user:
            Notification.objects.create(
                recipient=parent_comment.author,
                actor=request.user,
                verb='replied to',
                target=parent_comment
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
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', 'home'))
    return redirect(next_url)


@login_required
@require_POST
def update_comment(request, comment_pk):
    """Update an existing comment (AJAX endpoint)."""
    comment = get_object_or_404(Comment, pk=comment_pk)
    
    if request.user != comment.author:
        return JsonResponse({'success': False, 'error': 'You do not have permission to edit this comment.'}, status=403)
    
    new_text = request.POST.get('text', '').strip()
    if not new_text:
        return JsonResponse({'success': False, 'error': 'Comment text cannot be empty.'}, status=400)
    
    comment.text = new_text
    comment.save()
    
    return JsonResponse({'success': True, 'new_text': comment.text})


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
        if comment.author != request.user:
            Notification.objects.create(
                recipient=comment.author,
                actor=request.user,
                verb='liked your comment on',
                target=comment.post
            )
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes_count': comment.likes_count,
        'message': message
    })


# User Dashboard (for logged-in users)
@login_required
def user_dashboard(request):
    """Display user's own posts, comments, and viewing statistics"""
    user = request.user
    
    if user.is_author:
        # Author user data
        user_posts = BlogPost.objects.filter(author=user).exclude(status='archived').order_by('-date_created')
        total_posts = user_posts.count()
        total_post_likes = PostLike.objects.filter(post__author=user).count()
        
        # Pagination for posts
        paginator = Paginator(user_posts, 5)
        page_number = request.GET.get('page')
        posts = paginator.get_page(page_number)
        
        recently_viewed = None
    else:
        # Regular user data - viewing statistics
        user_posts = None
        posts = None
        total_post_likes = 0  # Not relevant for regular users
        
        # Total viewed posts
        total_posts = UserPostView.objects.filter(user=user).count()
        
        # Recently viewed posts for display
        recently_viewed = UserPostView.objects.filter(
            user=user
        ).select_related('post', 'post__author').order_by('-viewed_at')[:5]
    
    # Common data for all users
    user_comments = Comment.objects.filter(author=user).select_related('post').order_by('-date_created')[:10]
    total_comments = Comment.objects.filter(author=user).count()
    total_comment_likes = CommentLike.objects.filter(comment__author=user).count()
    
    context = {
        'posts': posts,
        'recent_comments': user_comments,
        'recently_viewed': recently_viewed,  # Add this for template
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
    total_authors = CustomUser.objects.filter(blogpost__isnull=False).distinct().count()
    total_comments = Comment.objects.count()
    
    context = {
        'total_posts': total_posts,
        'total_authors': total_authors,
        'total_comments': total_comments,
    }
    return render(request, 'main/about.html', context)



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


# Author Application View
def author_application_view(request):
    if request.user.is_authenticated:
        # Check if the user already has a pending or approved application
        if hasattr(request.user, 'author_applications') and request.user.author_applications.filter(status__in=['pending', 'approved']).exists():
            messages.info(request, 'You have already submitted an application.')
            return redirect('home')
        
        initial_data = {'name': request.user.get_full_name, 'email': request.user.email}
    else:
        initial_data = None

    if request.method == 'POST':
        form = AuthorApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            if request.user.is_authenticated:
                application.user = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully! We will review it and get back to you soon.')
            return redirect('home')
    else:
        form = AuthorApplicationForm(initial=initial_data)
        if request.user.is_authenticated:
            form.fields['name'].widget.attrs['readonly'] = True
            form.fields['email'].widget.attrs['readonly'] = True

    return render(request, 'main/author_application.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def archived_posts_list(request):
    """Display a list of all archived posts for staff review."""
    archived_posts = BlogPost.objects.filter(status='archived').order_by('-date_updated')
    
    paginator = Paginator(archived_posts, 20)  # 20 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
    }
    return render(request, 'main/archived_posts.html', context)

@login_required
def notification_list(request):
    """Display all notifications for the user and mark them as read."""
    notifications = request.user.notifications.all()
    request.user.notifications.filter(read=False).update(read=True)
    return render(request, 'main/notifications.html', {'notifications': notifications})