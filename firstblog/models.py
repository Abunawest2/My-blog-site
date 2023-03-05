from django.db import models
from django.contrib.auth.models import AbstractUser, User

class BlogPost(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    post = models.TextField()
    Date_Created = models.DateField(auto_now_add=True)
    Date_Created = models.DateField(auto_now=True)

# class CustomerUser(AbstractUser):
#     pass