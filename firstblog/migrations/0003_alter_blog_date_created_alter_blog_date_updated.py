# Generated by Django 4.1.7 on 2023-03-05 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firstblog', '0002_blog_delete_blogpost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='date_created',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='blog',
            name='date_updated',
            field=models.DateField(auto_now=True),
        ),
    ]
