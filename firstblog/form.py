from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import BlogPost, CustomUser
from django.core.validators import FileExtensionValidator


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
        model = CustomUser
        fields =  ['username', 'email', 'password1', 'password2']

class BlogPostForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs = {'class':'form-in form-control'}
        ),
        required=True
    )
    add_image = forms.ImageField(
        widget=forms.FileInput(
            attrs = {'class':'form-in form-control'}
        ),
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]
    )
    post = forms.CharField(
        widget=forms.Textarea(
            attrs = {'class':'form-in form-control'}
        )
    )
    class Meta:
        model = BlogPost
        fields = ['topic', 'title', 'add_image', 'post']