from django.db import models
from django.contrib import admin
from .models import BlogPost, PostLike, CustomUser, Comment, SuperCategory, SubCategory, Category, AuthorApplication, AuthorProfile, Notification, CommentLike, UserPostView
from .forms import BlogPostForm
from django.db.models import Count
from unfold.admin import ModelAdmin
from django.utils import timezone
# IMPORT ALLAUTH MODELS
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from allauth.account.models import EmailAddress

from unfold.sites import UnfoldAdminSite as unfold_admin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AdminBlogPostForm
from unfold.contrib.forms.widgets import WysiwygWidget

from django.contrib.auth.models import Group


class AuthorApplicationAdmin(ModelAdmin):
    list_display = ['user__username', 'user__email', 'primary_genre', 'status', 'date_applied']
    list_filter = ['status', 'primary_genre', 'date_applied']
    list_editable = ['status']
    search_fields = ['name', 'email', 'bio']
    readonly_fields = ['name', 'email', 'bio', 'sample_work_link', 'date_applied', 'reviewed_by', 'reviewed_at']
        

    def save_model(self, request, obj, form, change):
        # Get old status if the object is being changed
        old_status = AuthorApplication.objects.get(pk=obj.pk).status if obj.pk else None
        
        super().save_model(request, obj, form, change) # Save the object first

        if 'status' in form.changed_data:
            if obj.status == 'approved' and old_status != 'approved':
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
                if obj.user:
                    AuthorProfile.objects.get_or_create(user=obj.user)
                
                # Create notification for approval
                if obj.user: # Ensure there's a registered user to notify
                    Notification.objects.create(
                        recipient=obj.user,
                        actor=request.user,
                        verb='approved your author application',
                        target=obj
                    )
            elif obj.status == 'rejected' and old_status != 'rejected':
                # Create notification for rejection
                if obj.user: # Ensure there's a registered user to notify
                    Notification.objects.create(
                        recipient=obj.user,
                        actor=request.user,
                        verb='rejected your author application',
                        target=obj
                    )




class AuthorProfileAdmin(ModelAdmin):
    list_display = ['user', 'user__email', 'bio', 'website']
    search_fields = ['user__username', 'bio']
    date_hierarchy = 'user__date_joined'

class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ['id', 'username', 'full_name', 'email', 'is_staff', 'is_active', 'date_joined']
    list_display_links = ['id', 'username', 'full_name', 'email']
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

    def full_name(self, obj):
        return obj.get_full_name
    full_name.short_description = 'Full name'


class BlogPostAdmin(ModelAdmin):
    form = AdminBlogPostForm
    list_display = ['id','title', 'status', 'category', 'author', 'date_created', 'get_comment_count',
                    'likes_count', 'view_count']
    list_display_links = ['id', 'title', 'category']
    list_filter = ['status', 'date_created', 'author', ('date_created', RangeDateFilter)]
    list_editable = ['status']
    list_filter_submit = True
    search_fields = ['title', 'post']
    date_hierarchy = 'date_created'
    ordering = ['-view_count', '-date_created']
    readonly_fields = ['view_count', 'date_created', 'date_updated']

    # def total_likes(self, obj):
    #     return obj.likes_count

class UserPostViewAdmin(ModelAdmin):
    list_display = ['user', 'post', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__username', 'post__title']
    date_hierarchy = 'viewed_at'

class PostLikeAdmin(ModelAdmin):
    list_display = ['user', 'post', 'date_created']
    list_filter = ['date_created']
    search_fields = ['user__username', 'post__text']
    date_hierarchy = 'date_created'

class CommentAdmin(ModelAdmin):
    list_display = ['get_short_text', 'author', 'post', 'parent', 'date_created', 'likes_count']
    list_filter = ['date_created', 'author']
    search_fields = ['text', 'author__username', 'post__title']
    date_hierarchy = 'date_created'
    readonly_fields = ['date_created', 'date_updated']
    
    def get_short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    get_short_text.short_description = 'Comment Text'

class CommentLikeAdmin(ModelAdmin):
    list_display = ['user', 'comment', 'date_created']
    list_filter = ['date_created']
    search_fields = ['user__username', 'comment__text']
    date_hierarchy = 'date_created'

class SuperCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class SubCategoryAdmin(ModelAdmin):
    list_display = ('name', 'super_category', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('super_category',)

class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'sub_category', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('sub_category',)


class SocialAccountAdmin(ModelAdmin):
    list_display = ['user', 'provider', 'uid', 'last_login']
    search_fields = ['user__username', 'user__email', 'uid']
    list_filter = ['provider']
    date_hierarchy = 'last_login'

class SocialAppAdmin(ModelAdmin):
    list_display = ['name', 'provider', 'client_id']
    search_fields = ['name', 'provider', 'client_id']

class SocialTokenAdmin(ModelAdmin):
    list_display = ['app', 'account', 'token', 'expires_at']
    search_fields = ['app__name', 'account__user__username', 'token']
    date_hierarchy = 'expires_at'

class EmailAddressAdmin(ModelAdmin):
    list_display = ['user', 'email', 'verified', 'primary']
    search_fields = ['user__username', 'email']
    list_filter = ['verified', 'primary']
    # date_hierarchy = 'date_added'

class customGroupAdmin(ModelAdmin):
    list_display = ['name']
    search_fields = ['name']



class customAdminSite(unfold_admin):
    site_header = 'FirstBlog Administration'
    site_title = 'FirstBlog Admin Portal'
    index_title = 'Welcome to FirstBlog Admin'


custom_admin_site = customAdminSite(name='custom_admin_site')

custom_admin_site.register(CustomUser, CustomUserAdmin)
custom_admin_site.register(BlogPost, BlogPostAdmin)
custom_admin_site.register(PostLike, PostLikeAdmin)
custom_admin_site.register(Comment, CommentAdmin)
custom_admin_site.register(CommentLike, CommentLikeAdmin)
custom_admin_site.register(SuperCategory, SuperCategoryAdmin)
custom_admin_site.register(SubCategory, SubCategoryAdmin)
custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Group, customGroupAdmin)
custom_admin_site.register(UserPostView, UserPostViewAdmin)
custom_admin_site.register(AuthorApplication, AuthorApplicationAdmin)
custom_admin_site.register(AuthorProfile, AuthorProfileAdmin)

# Allauth Models
custom_admin_site.register(SocialApp, SocialAppAdmin)
custom_admin_site.register(SocialAccount, SocialAccountAdmin)
custom_admin_site.register(SocialToken, SocialTokenAdmin)
custom_admin_site.register(EmailAddress, EmailAddressAdmin)
# custom_admin_site.register(Site)