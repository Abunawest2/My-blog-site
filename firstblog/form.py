from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
class UserForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs = {'class':'form-in form-control', 'placeholder':'Enter username', 'id':'username'}
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs = {'class':'form-in form-control', 'placeholder':'Enter email'}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs = {'class':'form-in form-control', 'placeholder':'Enter Password'}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs = {'class':'form-in form-control', 'placeholder':'Confirm Password'}
        )
    )
    class Meta:
        model = User
        fields =  ['username', 'email', 'password1', 'password2']