from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class SignUp(models.Model):

    User_type_choice = [('admin', 'Admin'),
                 ('customer', 'Customer')]

    First_name = models.CharField(max_length = 50)
    Last_name = models.CharField(max_length = 50)
    User_type = models.CharField(max_length = 50, choices = User_type_choice)
    Email = models.EmailField(max_length = 100, primary_key = True, unique = True)
    Password = models.CharField(max_length = 250)
    Date_time = models.DateTimeField(auto_now_add=True)

    class Meta():
        db_table = 'signup'

    # to created the hashed password
    def set_password(self, raw_password):
        self.Password = make_password(raw_password)

    # to check the hashed password and compare it with the original password
    def check_password(self, raw_password):
        return check_password(raw_password, self.Password)

    def __str__(self):
        return f"{self.First_name} {self.Last_name}"
    
# Token Model

class PasswordResetToken(models.Model):
    user = models.ForeignKey(SignUp, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta():
        db_table = 'Password_reset_token'

    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at) < timedelta(minutes=30)

    def __str__(self):
        return f"Reset token for {self.user.Email}"