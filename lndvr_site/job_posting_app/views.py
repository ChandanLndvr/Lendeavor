from django.shortcuts import render
from job_posting_app.models import JobDetails

# Create your views here.

#------------------------ add jobs --------------------------

def add_job(request):
    if request.method == "POST":
        try:
            title = request.POST.get('title')
            location = request.POST.get('location')
            job_type = request.POST.get('job_type')
            work_mode = request.POST.get('work_mode')
            description = request.POST.get('description')
            skills = request.POST.get('skills')
            salary = request.POST.get('salary')
            email = request.POST.get('email')
            added_by = request.POST.get('added_by')

            if not added_by.lower().endswith("@lendeavorusa.com"):
                return render(request, "add_job.html", {"error": "You are not allowed to post a Job."})

            job_obj = JobDetails(Title = title, 
                         Location = location, 
                         Job_type = job_type, 
                         Work_mode = work_mode, 
                         Description = description, 
                         Skills = skills, 
                         Salary = salary,
                         Email = email, 
                         Added_by = added_by)
            job_obj.save()
            return render(request, 'add_job.html', {'message':'Data added successfully!'})
            
        except Exception as e:
            return render(request, 'add_job.html', {'error':str(e)})
    return render(request, 'add_job.html', {'current_page':'careers'})

