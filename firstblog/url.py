from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.home, name='home'),
    path('signup/', v.signup, name='signup'),
    path('Login/', v.SignIn, name='login'),
    # path('user-profile/', v.UserProfile, name='user-profile'),
    path('logout/', v.logout_view, name='logout'),
    path('create_post/', v.create_post, name='create_post'),
    path('update-post/<int:pk>/', v.update_post, name='update_post'),
    path('delete-post/<int:pk>/', v.delete_post, name='delete_post'),
    path('post/<int:pk>/comment/', v.add_comment_to_post, name='add_comment_to_post'),
]
