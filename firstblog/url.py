from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.home, name='home'),
    path('signup/', v.signup, name='signup'),
]
