from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import BlogPost, CustomUser, Comment
from django.core.validators import FileExtensionValidator
from tinymce.widgets import TinyMCE  # Import TinyMCE widget

class UserForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs = {'class':'form-in form-control', 'placeholder':'Enter username', 'id':'username'}
        )
    )
    email = forms.CharField(
        widget=forms.TextInput(
            attrs = {'class':'form-in form-control', 'placeholder':'Enter Email'}
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
        fields =  "__all__"


class BlogPostForm(forms.ModelForm):
    title = forms.CharField(
        label='Post Title',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter an engaging title for your post...',
                'maxlength': '100',
                'autocomplete': 'off'
            }
        ),
        required=True,
        max_length=100,
        help_text='Maximum 100 characters'
    )
    
    add_image = forms.ImageField(
        label='Featured Image',
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/gif',
                'id': 'id_add_image'
            }
        ),
        required=False,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        help_text='Upload an image (JPG, JPEG, PNG, or GIF). Max size: 5MB'
    )
    
    post = forms.CharField(
        label='Post Content',
        widget=TinyMCE(
            attrs={
                'class': 'form-control',
                'placeholder': 'Share your story with the world...',
                'id': 'id_post'
            }
        ),
        required=True,
        help_text='Write the main content of your blog post'
    )
    
    class Meta:
        model = BlogPost
        fields = ['title', 'add_image', 'post']
    
    def clean_add_image(self):
        """Validate image file size"""
        image = self.cleaned_data.get('add_image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size cannot exceed 5MB.')
        return image
    
    def clean_title(self):
        """Clean and validate title"""
        title = self.cleaned_data.get('title')
        if title:
            title = ' '.join(title.split())
            if len(title) < 5:
                raise forms.ValidationError('Title must be at least 5 characters long.')
        return title
    
    def clean_post(self):
        """Clean and validate post content"""
        post = self.cleaned_data.get('post')
        if post:
            # Remove HTML tags for character count validation
            import re
            text_content = re.sub('<[^<]+?>', '', post)
            text_content = '\n\n'.join([' '.join(p.split()) for p in text_content.split('\n\n')])
            
            if len(text_content) < 50:
                raise forms.ValidationError('Post content must be at least 50 characters long.')
        return post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Comment'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your comment here'})