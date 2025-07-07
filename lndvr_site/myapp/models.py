from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import timedelta
from django.utils import timezone
from job_posting_app.models import JobDetails

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
    
# User Application info

class UserApplications(models.Model):

    entity_choice = [('llc','LLC'),
                     ('corporation','Corporation'),
                     ('sole_proprietor', 'Sole Proprietor'),
                     ('partnership','Partnership')]
    ID = models.AutoField(primary_key=True)
    Business_name = models.CharField(max_length=250)
    Doing_business_as = models.CharField(max_length=250)
    Business_address = models.TextField()
    Industry = models.CharField(max_length=250)
    Tax_ID = models.CharField(max_length=12) 
    Entity = models.CharField(max_length=50, choices = entity_choice)
    Business_Start_date = models.CharField(max_length=7)
    
    Owner_First_Name = models.CharField(max_length=100)
    Owner_Middle_Name = models.CharField(max_length=100, null=True, blank=True)  # Allow null
    Owner_Last_Name = models.CharField(max_length=100)
    Birth_Date = models.DateField()
    Home_address = models.TextField(max_length=250)  
    Business_Email = models.EmailField()
    Phone_no = models.CharField(max_length=10)
    
    SSN = models.CharField(max_length=11)  
    Ownership = models.PositiveIntegerField()
    Monthly_Revenue = models.PositiveIntegerField()
    Funds_Requested = models.PositiveIntegerField()
    Existing_loans = models.CharField(max_length=5)

    Documents = models.FileField(upload_to='uploaded_files/', null=True, blank=True)
    First_time = models.CharField(max_length=5, default='Yes')  
    Applied_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'User_Applications'

    def __str__(self):
        return f"{self.Owner_First_Name} {self.Owner_Last_Name}"

# Job Applications
 
class JobApplications(models.Model):
    experience_choices = [
        ('fresher','Fresher'),
        ('1-2','1-2'),
        ('3-4','3-4'),
        ('5-7','5-7'),
        ('8-10','8-10'),
        ('10+','10+')
    ]

    qualification_level = [
        ('undergrad','Under Graduation'),
        ('grad','Graduation'),
        ('postgrad','Post Graduation')
    ]

    Application_id = models.CharField(max_length=10, primary_key=True, unique=True)
    Job = models.ForeignKey(JobDetails, on_delete=models.CASCADE, related_name='applications')
    Job_title = models.CharField(max_length=255, null=True, blank=True)
    First_name = models.CharField(max_length=150)
    Last_name = models.CharField(max_length=150)
    Email = models.EmailField()
    Phone_no = models.CharField(max_length=15)
    Expirence = models.CharField(max_length=150, choices=experience_choices)
    Qualification_level = models.CharField(max_length=200, choices=qualification_level)
    Major = models.CharField(max_length=200)
    School_name = models.CharField(max_length=200)
    Degree_year = models.IntegerField()
    Expected_salary  = models.IntegerField(null=True, blank=True)
    Gender = models.CharField(max_length=50)
    Resume = models.FileField(upload_to='uploaded_files/resume/', null=True, blank=True)
    Applied_on = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.Application_id:  # Only generate ID if it doesn't already exist
            # Get the last Application_id, if available
            last_appln_id = JobApplications.objects.order_by('Application_id').last()
            
            # Determine the next ID
            if last_appln_id and last_appln_id.Application_id.startswith('JA'):
                # Extract the numeric part and increment it
                next_id_num = int(last_appln_id.Application_id[2:]) + 1
            else:
                # Start from 101 if no valid last ID exists
                next_id_num = 101
            
            # Set the new Application_id with prefix 'CR'
            self.Application_id = f'JA{next_id_num}'
        
        # Call the parent save method
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'Job_applications'

    def __str__(self):
        return f"{self.First_name} + {self.Last_name}"

