from django.contrib import admin
from myapp.models import SignUp, UserApplications, JobApplications

# Register your models here.

admin.site.register(SignUp)
admin.site.register(UserApplications)
admin.site.register(JobApplications)
