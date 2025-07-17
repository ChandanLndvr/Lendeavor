from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from myapp.models import SignUp, UserApplications, JobApplications, BlacklistedToken, Lenders
from myapp.utils.auth_utils import hash_password, verify_password, generate_jwt
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .models import PasswordResetToken
import uuid
from job_posting_app.models import JobDetails
from datetime import date, timedelta
import jwt
from datetime import datetime, timezone as dt_timezone
from .utils.auth_utils import decode_jwt
from lndvr_site.utils.graph_email import send_graph_email

#----------------------- Main page ------------------------

def main(request):
    return render(request, 'mainPage.html')

#------------------------ Signup --------------------------

def signUp(request):
    if request.method == "POST":
        try:
            fname = request.POST.get('first_name')
            lname = request.POST.get('last_name')
            user_type = request.POST.get('user_type', '').title()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password1')
            confirm_pass = request.POST.get('password2')

            if password != confirm_pass:
                return render(request, "signUp.html", {"error": "Passwords do not match!"})

            if SignUp.objects.filter(Email=email).exists():
                return render(request, "signUp.html", {"error": "Email already exists!"})

            if user_type == "Admin" and not email.lower().endswith("@lendeavorusa.com"):
                return render(request, "signUp.html", {"error": "You can't be registered as Admin."})

            signup_obj = SignUp(
                First_name=fname,
                Last_name=lname,
                User_type=user_type,
                Email=email
            )

            signup_obj.set_password(password)
            signup_obj.save()

            return render(request, "login.html", {"message": "User registered successfully, now you can login!"})

        except Exception as e:
            return render(request, "signUp.html", {"error": str(e)})

    return render(request, "signUp.html")


#---------------------- login with JWT Auth ----------------------------

def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password1')

        try:
            print(SignUp.objects.get(Email=email))
            user = SignUp.objects.get(Email=email)

            if verify_password(password, user.Password):
                token = generate_jwt({'email': user.Email, 'user_type': user.User_type})
                response = redirect("mainPage")
                response.set_cookie('jwt_token', token)
                return response
            else:
                return render(request, 'login.html', {"error": "Incorrect password."})

        except SignUp.DoesNotExist:
            return render(request, 'login.html', {"error": "No account found with that email."})

    # Handle GET request — check if there is a message or error in query params
    message = request.GET.get('message')
    error = request.GET.get('error')

    return render(request, 'login.html', {
        "message": message,
        "error": error
    })


#---------------------------- logout -------------------------------------------

def logout_user(request):
    token = request.COOKIES.get('jwt_token')
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            expiry_timestamp = payload.get('exp')
            expires_at = datetime.fromtimestamp(expiry_timestamp, tz=dt_timezone.utc)   

            BlacklistedToken.objects.get_or_create(token=token, defaults={'expires_at': expires_at})
        except jwt.InvalidTokenError:
            pass

    response = redirect(reverse('mainPage') + "?message=You have successfully logged out.")
    response.delete_cookie('jwt_token')
    return response

#----------------------------- Forgot Password ----------------------------------

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = SignUp.objects.get(Email=email)
            token = str(uuid.uuid4())

            PasswordResetToken.objects.create(user=user, token=token)

            reset_link = f"http://localhost:8000/reset-password/{token}/"

            email_sent = send_graph_email(
            'Reset Your Password',
            f'Click the link to reset your password: {reset_link}',
            [user.Email]
            )

            if not email_sent:
                forgot_url = reverse("forgot_password") + "?error=Failed to send reset email."
                print("Redirecting to:", forgot_url)
                return redirect(forgot_url)
            else:
                # Add message in GET parameters for the login page
                login_url = reverse("login") + "?message=Check your email for a reset link."
                print("Redirecting to:", login_url)
                return redirect(login_url)  

        except SignUp.DoesNotExist:
            # Stay on the same page with an error message in GET parameters
            forgot_url = reverse("forgot_password") + "?error=No account with that email."
            print("Redirecting to:", forgot_url)
            return redirect(forgot_url)

    # Correctly read from GET, not POST
    message = request.GET.get('message')
    error = request.GET.get('error')

    print("Message:", message)
    print("Error:", error)

    return render(request, "forgot_password.html", {
        "message": message,
        "error": error
    })

#----------------------------- Reset Password ----------------------------------

def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            return HttpResponse("Token expired or already used.", status=400)

        if request.method == "POST":
            password = request.POST.get("password1")
            confirm = request.POST.get("password2")

            if password != confirm:
                return render(request, "reset_password.html", {"error": "Passwords don't match.", "token": token})

            user = reset_token.user
            user.set_password(password)
            user.save()

            reset_token.is_used = True
            reset_token.save()

            return render(request, "login.html", {"message": "Password reset successful!"})

        return render(request, "reset_password.html", {"token": token})

    except PasswordResetToken.DoesNotExist:
        return HttpResponse("Invalid token", status=400) 
    
#--------------------------------- Sending attached email ----------------------------------

def send_attached_email(data):
    # Prepare email body (skip Documents)
    email_body = "\n".join(
        f"{k.replace('_', ' ')}: {v}" for k, v in data.items() if v and k != 'Documents'
    )

    email = EmailMessage(
        subject="New / Updated  Business Application",
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[data['Business_Email']],
    )

    if data['Documents']:
        email.attach(
            data['Documents'].name,
            data['Documents'].read(),
            data['Documents'].content_type,
        )

    email.send(fail_silently=False)

#------------------------------- Apply Now ----------------------------------------

def apply(request):
    if request.method == "POST":
        try:
            # Extract form data
            data = {
                'Business_name': request.POST.get('business_name'),
                'Doing_business_as': request.POST.get('dba'),
                'Business_address': request.POST.get('business_add'),
                'Industry': request.POST.get('industry'),
                'Tax_ID': request.POST.get('taxid'),
                'Entity': request.POST.get('entity'),
                'Business_Start_date': request.POST.get('startdate'),
                'Owner_First_Name': request.POST.get('fname'),
                'Owner_Middle_Name': request.POST.get('mname'),
                'Owner_Last_Name': request.POST.get('lname'),
                'Birth_Date': request.POST.get('dob'),
                'Home_address': request.POST.get('haddress'),
                'Business_Email': request.POST.get('bemail'),
                'Phone_no': request.POST.get('phone'),
                'SSN': request.POST.get('ssn'),
                'Ownership': int(request.POST.get('ownership_percent') or 0),
                'Monthly_Revenue': int(request.POST.get('monthly_revenue') or 0),
                'Funds_Requested': int(request.POST.get('fund') or 0),
                'Existing_loans': request.POST.get('existing_loans'),
                'Documents': request.FILES.get('financial_statement'),
                'First_time': request.POST.get('application_no', '').lower(),
            }

            ssn = data['SSN']
            first_time = data['First_time']
            ssn_exists = UserApplications.objects.filter(SSN=ssn).exists()

            if not ssn_exists:
                # Case 1: New SSN — create
                UserApplications.objects.create(**data)
                send_attached_email(data)
                message = "Application submitted successfully!"
            elif first_time == "yes":
                # Case 2: SSN exists and first time = yes — update
                UserApplications.objects.update_or_create(SSN=ssn, defaults=data)
                send_attached_email(data)
                message = "Application updated successfully!"
            else:
                # Case 3: SSN exists and first time = no — create new
                UserApplications.objects.create(**data)
                send_attached_email(data)
                message = "Application submitted successfully!"

            return render(request, 'apply.html', {'message': message})

        except Exception as e:
            return render(request, 'apply.html', {'error': str(e)})

    return render(request, 'apply.html')

#----------------------------- About us ----------------------------

def aboutus(request):
    return render(request, "aboutus.html",{'current_page':'about'})

#---------------------------- Products -----------------------------

def products(request):
    return render(request, "products.html", {'current_page':'products'})

#---------------------------- Careers Page -------------------------

def career_page(request):
    all_jobs = JobDetails.objects.all()

    message = request.GET.get("message")
    error = request.GET.get("error")

    token = request.COOKIES.get('jwt_token')
    user_type = None

    if token:
        payload = decode_jwt(token)
        if payload:
            user_type = payload.get('user_type')

    show_admin_tools = (user_type == 'Admin')

    context = {
        'jobs': all_jobs,
        'current_page': 'careers',
        'message': message,
        'error': error,
        'show_admin_tools': show_admin_tools,
    }
    return render(request, 'careers.html', context)

#------------------------ Apply for jobs -------------------------

def job_applications(request, job_id):
    job = get_object_or_404(JobDetails, Job_id=job_id)
    context = {
        'job': job,
        'current_page': 'careers',
    }

    if request.method == "POST":
        try:
            f_name = request.POST.get('fname')
            l_name = request.POST.get("lname")
            email = request.POST.get("email")
            phone_no = request.POST.get("phone")
            experience = request.POST.get("experience")
            qualification = request.POST.get("qualification")
            major = request.POST.get("major")
            school = request.POST.get("school")
            degree_year = request.POST.get("year")
            expected_salary = request.POST.get("salary")
            gender = request.POST.get("gender")
            resume_file = request.FILES.get("resume")

            twenty_days_ago = date.today() - timedelta(days=20)
            duplicate = JobApplications.objects.filter(
                Email=email,
                Job=job,
                Applied_on__gte=twenty_days_ago
            ).exists()

            if duplicate:
                context['error'] = "You have already applied for this job within the last 20 days."
                return render(request, "job_apply.html", context)

            JobApplications.objects.create(
                Job=job,
                Job_title=job.Title,
                First_name=f_name,
                Last_name=l_name,
                Email=email,
                Phone_no=phone_no,
                Expirence=experience,
                Qualification_level=qualification,
                Major=major,
                School_name=school,
                Degree_year=degree_year,
                Expected_salary=expected_salary if expected_salary else None,
                Gender=gender,
                Resume=resume_file
            )

            # Prepare email with attachment
            subject = f"New Job Application for {job.Title}"
            message = f"""
                        Dear HR,

                        A new job application has been submitted.

                        Job: {job.Title}
                        Applicant Name: {f_name} {l_name}
                        Email: {email}
                        Phone: {phone_no}
                        Experience: {experience}
                        Qualification Level: {qualification}
                        Major: {major}
                        School: {school}
                        Degree Year: {degree_year}
                        Expected Salary: {expected_salary}
                        Gender: {gender}

                        Please find the attached resume for further details.

                        Regards,
                        Lendeavor Careers Bot
                        """

            email_message = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [job.Email, settings.DEFAULT_FROM_EMAIL],  # HR and archive
            )

            if resume_file:
                email_message.attach(resume_file.name, resume_file.read(), resume_file.content_type)

            email_message.send(fail_silently=False)

            context['message'] = "You have successfully applied for this job, and your resume has been sent to HR."

        except Exception as e:
            context['error'] = f"An error occurred: {str(e)}"

    return render(request, "job_apply.html", context)


#---------------------------- Contact ----------------------------

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'No Subject')
        msg_body = request.POST.get('message')

        # Construct message body with sender info
        body = f"From: {name} <{email}>\n\n{msg_body}"

        # Send via Graph API
        email_sent = send_graph_email(
            subject,
            body,
            [settings.CONTACT_EMAIL]
        )

        if email_sent:
            message = "Thank you for contacting us!"
        else:
            message = "We could not send your message at this time. Please try again later."

        return render(
            request,
            "contactus.html",
            {
                'message': message,
                'current_page': 'contact'
            }
        )

    return render(request, "contactus.html", {'current_page': 'contact'})

#-------------------------- lenders / Marketplace ---------------------

def lenders_marketplace(request):
    lenders_info = Lenders.objects.all().order_by('Lender_name')
    return render(request, 'lenders_marketplace.html', {'lenders_info': lenders_info})

#-------------------------- Funding Steps --------------------------

def funding_steps(request):
    return render(request, 'funding_steps.html', {'current_page':'steps'})

#-------------------------- FAQs -----------------------------------

def faq(request):
    return render(request, 'faq.html',{'current_page':'faq'})

#-------------------------- Case Study -----------------------------

def case_study(request):
    return render(request, 'case_study.html',{'current_page': 'case_study'})

#------------------------- Terms and conditions -------------------

def terms(request):
    return render(request, 'terms.html',{'current_page':'terms'})

#------------------------- Privacy Policy -------------------

def privacy(request):
    return render(request, 'privacy.html',{'current_page':'privacy'})

