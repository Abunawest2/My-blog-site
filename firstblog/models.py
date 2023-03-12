from django.db import models
from django.contrib.auth.models import AbstractUser, User, AbstractBaseUser
from multiselectfield import MultiSelectField

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email address')
    contact = models.CharField(max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic, blank=True)
    title = models.CharField(max_length=100)
    add_image = models.ImageField(null=True, blank=True, upload_to='image/')
    post = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.title