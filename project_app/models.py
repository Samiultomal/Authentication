from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    USER_TYPES = [
        ('staff', 'Staff'),
        ('employee', 'Employee'),
        ('user', 'User'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='user', db_index=True)
    contact_number = PhoneNumberField(null=True, blank=True, unique=True, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    is_email_verified = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    def __str__(self):
        return self.username
    