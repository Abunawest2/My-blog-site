# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True, default="LEGGETECH")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        
    
    @property
    def get_full_name(self):
        """Return full name or username as fallback"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return f"{self.username}"
    

    def __str__(self):
        return f"{self.username}"

    @property
    def is_author(self):
        return hasattr(self, 'author_profile')

class AuthorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='author_profile')
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    profile_picture = models.ImageField(null=True, blank=True, upload_to='author_profiles/')
    linkedin_url = models.URLField(blank=True, help_text="Your LinkedIn profile URL")
    twitter_url = models.URLField(blank=True, help_text="Your Twitter profile URL")
    facebook_url = models.URLField(blank=True, help_text="Your Facebook profile URL")
    github_url = models.URLField(blank=True, help_text="Your GitHub profile URL")

    def __str__(self):
        return f"{self.user.username}'s Author Profile"

class BlogPost(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, verbose_name='author')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=100)
    add_image = models.ImageField(null=True, blank=True, upload_to='image/')
    post = models.TextField()
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times product has been viewed"
    )

    class Meta:
        ordering = ['-date_updated', '-date_created']
        verbose_name = "post"
        verbose_name_plural = "posts"

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Override save to add custom behavior if needed"""
        return super().save(*args, **kwargs)
    
    def get_comment_count(self):
        """Return count of top-level comments only (not replies)"""
        return self.comments.filter(parent=None).count()

    @property
    def likes_count(self):
        """Return the number of likes for this Post"""
        return self.post_likes.count()
    
    
    def is_liked_by(self, user):
        """Check if a specific user has liked this comment"""
        if user.is_authenticated:
            return self.post_likes.filter(user=user).exists()
        return False
    
    def increment_view_count(self, user=None):
        """Increment view count without updating date_updated"""
        from django.db.models import F
        BlogPost.objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)
        if user and user.is_authenticated:
            UserPostView.objects.get_or_create(user=user, post=self)
        self.refresh_from_db(fields=['view_count'])

class UserPostView(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_views')
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='user_views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.user.username} viewed {self.post.title}"
    

class PostLike(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_likes')
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "Post Like"
        verbose_name_plural = "Post Likes"
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.user.username} likes Post by {self.post.author.username}"

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_comments')
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['date_created']

    def __str__(self):
        return f"{self.author.username}: {self.text[:50]}"
    
    @property
    def likes_count(self):
        """Return the number of likes for this comment"""
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Check if a specific user has liked this comment"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comment_likes')
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('comment', 'user')
        verbose_name = "Comment Like"
        verbose_name_plural = "Comment Likes"
        ordering = ['-date_created']
    
    def __str__(self):
        return f"{self.user.username} likes comment by {self.comment.author.username}"



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def post_count(self):
        """Return count of posts in this category"""
        return self.posts.count()

class AuthorApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='author_applications', help_text="The user account if the applicant is already registered.")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    bio = models.TextField(help_text="Tell us about yourself and why you want to be an author.")
    sample_work_link = models.URLField(help_text="A link to a sample of your writing (e.g., a blog post, article, or portfolio).")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    date_applied = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Author Application"
        verbose_name_plural = "Author Applications"
        ordering = ['-date_applied']

    def __str__(self):
        return f"Application from {self.name} ({self.email})"