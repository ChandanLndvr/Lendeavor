from django.shortcuts import render, redirect
from django.http import HttpResponse
from myapp.models import SignUp, UserApplications
from myapp.utils.auth_utils import hash_password, verify_password, generate_jwt
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from .models import PasswordResetToken
import uuid

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

            return render(request, "signUp.html", {"message": "User registered successfully, now you can login!"})

        except Exception as e:
            return render(request, "signUp.html", {"error": str(e)})

    return render(request, "signUp.html")


#---------------------- login with JWT Auth ----------------------------

def login(request):
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

    return render(request, 'login.html')

#----------------------------- Forgot Password ----------------------------------

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = SignUp.objects.get(Email=email)
            token = str(uuid.uuid4())

            PasswordResetToken.objects.create(user=user, token=token)

            reset_link = f"http://localhost:8000/reset-password/{token}/"

            send_mail(
                'Reset Your Password',
                f'Click the link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.Email],
                fail_silently=False,
            )

            return render(request, "forgot_password.html", {"message": "Check your email for a reset link."})
        except SignUp.DoesNotExist:
            return render(request, "forgot_password.html", {"error": "No account with that email."})

    return render(request, "forgot_password.html")

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
    job_list = [
        {
            "title": "Frontend Developer",
            "location": "New York, NY",
            "description": "Looking for an expert in React.js and UI/UX design.",
            "email": "careers@lendeavorusa.com",
        },
        {
            "title": "Marketing Analyst",
            "location": "Remote",
            "description": "Data-driven marketing specialist with B2B experience.",
            "email": "careers@lendeavorusa.com",
        }
    ]
    return render(request, 'careers.html', {'jobs': job_list})

#---------------------------- Contact ----------------------------

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', 'No Subject')
        msg_body = request.POST.get('message')

        send_mail(
            subject,
            f"From: {name} <{email}>\n\n{msg_body}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=True,
        )    
        return render(request, "contactus.html", {'message': "Thank you for contacting us!"})
    return render(request, "contactus.html")



