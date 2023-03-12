from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.home, name='home'),
    path('signup/', v.signup, name='signup'),
    path('Login/', v.SignIn, name='login'),
    path('logout/', v.logout_view, name='logout'),
    path('create_post/', v.create_post, name='create_post'),
]
