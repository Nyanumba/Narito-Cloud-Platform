from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    email = models.EmailField(unique = True)
    is_email_verified = models.BooleanField (default = False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__ (self):
        return self.email
    
#email verification class (it will be used to send email verification links)
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name= 'verification_token')
    token = models.UUIDField(default=uuid.uuid4, unique = True)
    created_at = models.DateTimeField(auto_now_add= True)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours = 24)
    
    def __str__(self):
        return f"Token for {self.user.email}"
    
    
        