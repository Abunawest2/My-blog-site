from django.db import migrations

def create_author_profiles(apps, schema_editor):
    CustomUser = apps.get_model('firstblog', 'CustomUser')
    AuthorProfile = apps.get_model('firstblog', 'AuthorProfile')
    for user in CustomUser.objects.filter(is_staff=True):
        AuthorProfile.objects.get_or_create(user=user)

class Migration(migrations.Migration):

    dependencies = [
        ('firstblog', '0016_authorapplication_user_authorprofile'),
    ]

    operations = [
        migrations.RunPython(create_author_profiles),
    ]