from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
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
            salary = request.POST.get('salary') or "TBD"
            email = request.POST.get('email')
            added_by = request.POST.get('added_by')

            if not added_by.lower().endswith("@lendeavorusa.com"):
                return render(request, "add_job.html", {"error": "You are not allowed to post a Job."})

            job_obj = JobDetails(
                Title=title,
                Location=location,
                Job_type=job_type,
                Work_mode=work_mode,
                Description=description,
                Skills=skills,
                Salary=salary,
                Email=email,
                Added_by=added_by
            )
            job_obj.save()

            # Redirect to careers page with success message after posting
            return redirect(reverse("careers") + "?message=Job posted successfully!")

        except Exception as e:
            return render(request, 'add_job.html', {'error': str(e)})

    return render(request, 'add_job.html', {'current_page': 'careers'})

#----------------------- update or delete the single job ---------------------------

def update_or_delete_job(request, job_id):
    job = get_object_or_404(JobDetails, Job_id=job_id)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "update":
            try:
                added_by = request.POST.get("added_by", "")
                if not added_by.endswith("lendeavorusa.com"):
                    # Redirect with error if added_by does not contain lendeavorusa.com
                    return redirect(reverse("careers") + "?error=Update failed: 'added_by' must contain 'lendeavorusa.com'.")

                # Proceed to update since condition passed
                job.Title = request.POST.get("title")
                job.Location = request.POST.get("location")
                job.Job_type = request.POST.get("job_type")
                job.Work_mode = request.POST.get("work_mode")
                job.Description = request.POST.get("description")
                job.Skills = request.POST.get("skills")
                job.Salary = request.POST.get("salary")
                job.Email = request.POST.get("email")
                job.Added_by = added_by
                job.save()

                return redirect(reverse("careers") + "?message=Job updated successfully.")

            except Exception as e:
                return redirect(reverse("careers") + f"?error=An error occurred while updating: {str(e)}")
            
        if action == "delete":
            try:
                job.delete()
                # Redirect to careers page with success message
                return redirect(reverse("careers") + "?message=Job deleted successfully.")
            except Exception as e:
                return redirect(reverse("careers") + f"?error=An error occurred: {str(e)}")

    return render(request, "update_job.html", {
        'jobs': job,
        'current_page': 'careers'
    })

#----------------------- bulk deletion of the jobs ----------------------

def bulk_delete_jobs(request):
    if request.method == "POST":
        job_ids = request.POST.getlist("job_ids")

        if not job_ids:
            return redirect(reverse("careers") + "?error=No jobs selected for deletion.")

        try:
            JobDetails.objects.filter(Job_id__in=job_ids).delete()
            return redirect(reverse("careers") + "?message=Selected jobs deleted successfully.")
        except Exception as e:
            return redirect(reverse("careers") + f"?error=Error during deletion: {str(e)}")

    # If GET, redirect safely
    return redirect(reverse("careers") + "?error=Invalid request method for bulk deletion.")



