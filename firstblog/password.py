from django.core.exceptions import ValidationError

def validate_password_length(password):
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
