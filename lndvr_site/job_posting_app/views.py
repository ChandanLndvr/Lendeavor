from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from job_posting_app.models import JobDetails
from lndvr_site.utils.loggedin_user_email import get_logged_in_user_email
from job_posting_app.serializers import JobDetailsSerializer
from myapp.custom_middleware.log_ip import log_action
from django.conf import settings
import jwt
from myapp.models import SignUp

#--------------- validating the admin user -------------------

def validate_admin_user(request):
    token = request.COOKIES.get('jwt_token')
    if not token:
        log_action(request, "No JWT token", user_info="Anonymous")
        return None, "Anonymous", redirect(reverse('login') + "?error=Login required.")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        email = payload.get('email')
        if not email:
            raise jwt.InvalidTokenError("No email in token")

        user = get_object_or_404(SignUp, Email=email)
        if user.User_type.lower() != "admin":
            log_action(request, "Unauthorized access - not admin", user_info=email)
            return None, email, render(request, "add_job.html", {
                "error": "Only admins allowed.",
                "user_email": email,
                "current_page": "careers"
            })

        return user, email, None

    except jwt.ExpiredSignatureError:
        log_action(request, "Token expired", user_info=token)
        return None, "Anonymous", redirect(reverse('login') + "?error=Session expired. Please login again.")
    except jwt.InvalidTokenError:
        log_action(request, "Invalid token", user_info=token)
        return None, "Anonymous", redirect(reverse('login') + "?error=Invalid session. Please login.")
    

#----------------------- getting data from html tag ------------------

def build_job_data_from_request(request, added_by_user):
    return {
        'Title': request.POST.get('title'),
        'Location': request.POST.get('location'),
        'Job_type': request.POST.get('job_type', '').lower(),
        'Work_mode': request.POST.get('work_mode', '').lower(),
        'Description': request.POST.get('description'),
        'Skills': request.POST.get('skills'),
        'Salary': request.POST.get('salary') or "TBD",
        'Email': request.POST.get('email'),
        'Added_by': added_by_user.Email  # pass email string (adjust as needed)
    }
    
#------------------------ add jobs --------------------------

def add_job(request):
    added_by_user, user_email, error_response = validate_admin_user(request)
    if error_response:
        return error_response

    if request.method == "POST":
        log_action(request, "Add job attempt", user_info=user_email)

        mapped_data = build_job_data_from_request(request, added_by_user)

        serializer = JobDetailsSerializer(data=mapped_data)

        if serializer.is_valid():
            serializer.save()
            log_action(request, "Job posted successfully", user_info=user_email)
            return redirect(reverse("careers") + "?message=Job posted successfully!")

        else:
            log_action(request, "Job add failed: validation error", user_info=user_email)
            return render(request, "add_job.html", {
                'error': serializer.errors,
                'current_page': 'careers',
                'user_email': user_email,
                'form_data': request.POST,
            })

    return render(request, 'add_job.html', {
        'current_page': 'careers',
        'user_email': user_email,
        'message': request.GET.get('message'),
        'error': request.GET.get('error')
    })

#----------------------- update or delete the single job ---------------------------

def update_or_delete_job(request, job_id):
    job = get_object_or_404(JobDetails, Job_id=job_id)

    added_by_user, user_email, error_response = validate_admin_user(request)
    if error_response:
        return error_response

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update":
            try:
                log_action(request, "Single job update attempt", user_info=user_email)

                data = build_job_data_from_request(request, added_by_user)

                serializer = JobDetailsSerializer(job, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    return redirect(reverse("careers") + "?message=Job updated successfully.")
                else:
                    log_action(request, f"Update validation errors: {serializer.errors}", user_info=user_email)
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
    added_by_user, user_email, error_response = validate_admin_user(request)
    if error_response:
        return error_response

    if request.method == "POST":
        job_ids = request.POST.getlist("job_ids")

        if not job_ids:
            return redirect(reverse("careers") + "?error=No jobs selected for deletion.")

        try:
            log_action(request, "Bulk job delete attempt", user_info=user_email)
            JobDetails.objects.filter(Job_id__in=job_ids).delete()
            return redirect(reverse("careers") + "?message=Selected jobs deleted successfully.")
        except Exception as e:
            return redirect(reverse("careers") + f"?error=Error during deletion: {str(e)}")

    # If GET or other method, redirect safely
    return redirect(reverse("careers") + "?error=Invalid request method for bulk deletion.")



