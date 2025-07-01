from django.db import models
import uuid

# Create your models here.

class JobDetails(models.Model):
    work_mode_choices = [
        ('in_office', 'In office'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote')
    ]
    job_type_choices = [
        ('contract', 'Contract'),
        ('part_time', 'Part Time'),
        ('full_time', 'Full Time'),
        ('internship', 'Internship')
    ]
    Job_id = models.UUIDField(default = uuid.uuid4, editable=False, unique=True, primary_key=True)
    Title = models.CharField(max_length=150)
    Location = models.CharField(max_length=250)
    Work_mode = models.CharField(max_length=50, choices=work_mode_choices)
    Job_type = models.CharField(max_length=50, choices=job_type_choices)
    Description = models.TextField()
    Skills = models.TextField()
    Salary = models.CharField(max_length=12, null=True, blank=True)
    Email = models.EmailField(default=" info@lendeavorusa.com")
    Added_by = models.EmailField()
    Date = models.DateField(auto_now_add=True)

    class Meta():
        db_table = 'Job_details'
    
    def __str__(self):
        return f"{self.Title} - {self.Location}"