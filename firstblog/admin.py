# admin.py - Add this to your existing admin.py
# from django.contrib.admin import ModelAdmin
from django.contrib import admin
from .models import BlogPost, PostLike, CustomUser, Comment, CommentLike, Category
from django.contrib.auth.models import User
from .forms import BlogPostForm
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm, AdminOwnPasswordChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    # password_change_form = AdminOwnPasswordChangeForm
    change_password_form = AdminPasswordChangeForm
    list_display = ['id', 'username', 'email', 'is_staff', 'is_active', 'date_joined']
    list_display_links = ['id', 'username', 'email']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}),
    )

    search_fields = ['username', 'email']
    date_hierarchy = 'date_joined'

@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ['id','title', 'author', 'date_created', 'get_comment_count', 'likes_count']
    list_display_links = ['id', 'title']
    list_filter = ['date_created', 'author', ('date_created', RangeDateFilter)]
    list_filter_submit = True
    search_fields = ['title', 'post']
    date_hierarchy = 'date_created'
    readonly_fields = ['date_created', 'date_updated']



@admin.register(PostLike)
class PostLikeAdmin(ModelAdmin):
    list_display = ['user', 'post', 'date_created']
    list_filter = ['date_created']
    search_fields = ['user__username', 'post__text']
    date_hierarchy = 'date_created'


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['get_short_text', 'author', 'post', 'parent', 'date_created', 'likes_count']
    list_filter = ['date_created', 'author']
    search_fields = ['text', 'author__username', 'post__title']
    date_hierarchy = 'date_created'
    readonly_fields = ['date_created', 'date_updated']
    
    def get_short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    get_short_text.short_description = 'Comment Text'


@admin.register(CommentLike)
class CommentLikeAdmin(ModelAdmin):
    list_display = ['user', 'comment', 'date_created']
    list_filter = ['date_created']
    search_fields = ['user__username', 'comment__text']
    date_hierarchy = 'date_created'


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'post_count', 'date_created']
    search_fields = ['name', 'description']
    date_hierarchy = 'date_created'


