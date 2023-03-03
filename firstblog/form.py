from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):

    class Meta:
        models = User
        fields = ['username', 'email', 'password1', 'password2']