from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from job_posting_app.models import JobDetails
from lndvr_site.utils.loggedin_user_email import get_logged_in_user_email
from job_posting_app.serializers import JobDetailsSerializer
from myapp.custom_middleware.log_ip import log_action

#------------------------ add jobs --------------------------

def add_job(request):
    if request.method == "POST":
        try:
            log_action(request, "Add job attempt", user_info=request.POST.get('added_by'))
            mapped_data = {
                'Title': request.POST.get('title'),
                'Location': request.POST.get('location'),
                'Job_type': request.POST.get('job_type').lower(),
                'Work_mode': request.POST.get('work_mode').lower(),
                'Description': request.POST.get('description'),
                'Skills': request.POST.get('skills'),
                'Salary': request.POST.get('salary') or "TBD",
                'Email': request.POST.get('email'),
                'Added_by': request.POST.get('added_by'),
            }
            serializer = JobDetailsSerializer(data=mapped_data)
            if serializer.is_valid():
                serializer.save()
                return redirect(reverse("careers") + "?message=Job posted successfully!")
            else:
                return render(request, "add_job.html", {
                    'error': serializer.errors,
                    'current_page': 'careers'
                })

        except Exception as e:
            return render(request, 'add_job.html', {
                'error': str(e),
                'current_page': 'careers'
            })

    return render(request, 'add_job.html', {'current_page': 'careers'})

#----------------------- update or delete the single job ---------------------------

def update_or_delete_job(request, job_id):
    job = get_object_or_404(JobDetails, Job_id=job_id)

    if request.method == "POST":
        action = request.POST.get("action")
        user_email = get_logged_in_user_email(request)

        if action == "update":
            try:
                log_action(request, "Single job update attempt", user_info=user_email)
                serializer = JobDetailsSerializer(job, data=request.POST, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return redirect(reverse("careers") + "?message=Job updated successfully.")
                else:
                    return redirect(reverse("careers") + f"?error=Update failed: {serializer.errors}")

            except Exception as e:
                return redirect(reverse("careers") + f"?error=An error occurred while updating: {str(e)}")

        if action == "delete":
            try:
                log_action(request, "Single job delete attempt", user_info=user_email)
                job.delete()
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
        user_email = get_logged_in_user_email(request)
        job_ids = request.POST.getlist("job_ids")

        if not job_ids:
            return redirect(reverse("careers") + "?error=No jobs selected for deletion.")

        try:
            log_action(request, "Bulk job delete attempt", user_info=user_email)
            JobDetails.objects.filter(Job_id__in=job_ids).delete()
            return redirect(reverse("careers") + "?message=Selected jobs deleted successfully.")
        except Exception as e:
            return redirect(reverse("careers") + f"?error=Error during deletion: {str(e)}")

    # If GET, redirect safely
    return redirect(reverse("careers") + "?error=Invalid request method for bulk deletion.")



