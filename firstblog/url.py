# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('signup/', views.signup, name='signup'),
    path('login/', views.SignIn, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Home
    path('', views.home, name='home'),
    
    # Post URLs
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/update/', views.update_post, name='update_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_pk>/like/', views.toggle_post_like, name='toggle_post_like'),
    
    # Search & Filter URLs
    path('search/', views.search_posts, name='search_posts'),
    path('category/<str:category_name>/', views.category_posts, name='category_posts'),
    path('author/<path:username>/', views.author_profile, name='author_profile'),
    path('archived-posts/', views.archived_posts_list, name='archived_posts'),

    # Comment URLs
    path('post/<int:pk>/comment/', views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/<int:comment_pk>/reply/', views.add_reply_to_comment, name='add_reply_to_comment'),
    path('comment/<int:comment_pk>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_pk>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    
    # User Dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # Other Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('apply-to-write/', views.author_application_view, name='author_application'),
    
    # Legacy view (optional - for backwards compatibility)
    path('post/<int:pk>/comments/', views.ViewComment, name='view_comments'),
    

]