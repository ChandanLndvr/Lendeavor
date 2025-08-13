from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from myapp.models import SignUp, UserApplications, JobApplications, BlacklistedToken, Lenders, ApplicationDocument
from myapp.utils.auth_utils import hash_password, verify_password, generate_jwt
from django.conf import settings
from .models import PasswordResetToken
import uuid
from job_posting_app.models import JobDetails
from datetime import date, timedelta
import jwt
from datetime import datetime, timezone as dt_timezone
from .utils.auth_utils import decode_jwt
from lndvr_site.utils.graph_email import send_graph_email
from lndvr_site.utils.send_graph_email_async import send_graph_email_async
from .serializers import SignUpSerializer, UserApplicationsSerializer, JobApplicationsSerializer
from myapp.custom_middleware.log_ip import log_action
from collections import defaultdict

#----------------------- Main page ------------------------

def main(request):
    return render(request, 'mainPage.html')

#------------------------ Signup --------------------------

def signUp(request):
    if request.method == "POST":
        try:
            log_action(request, "Signup attempt", user_info=request.POST.get('email'))
            data = {
                "First_name": request.POST.get("first_name", "").strip(),
                "Last_name": request.POST.get("last_name", "").strip(),
                "User_type": request.POST.get("user_type", "").lower().strip(),
                "Email": request.POST.get("email", "").strip(),
                "password1": request.POST.get("password1"),
                "password2": request.POST.get("password2"),
            }

            # Business rule for admin email
            if data["User_type"] == "admin" and not data["Email"].endswith("@lendeavorusa.com"):
                return render(request, "signUp.html", {"error": "Admin email must end with @lendeavorusa.com"})

            # Check for existing user
            if SignUp.objects.filter(Email=data["Email"]).exists():
                return render(request, "signUp.html", {"error": "Email already exists."})

            serializer = SignUpSerializer(data=data)
            if serializer.is_valid():
                serializer.save()  # instance of your SignUp (userDetails) model
                
                # Redirect with message
                return redirect(reverse("login") + "?message=Registration successful. Please login.")

            # If serializer invalid
            return render(request, "signUp.html", {"error": serializer.errors})

        except Exception as e:
            return render(request, "signUp.html", {"error": "An unexpected error occurred. Please try again."})

    # GET
    return render(request, "signUp.html")


#---------------------- login with JWT Auth ----------------------------

def login_user(request):
    if request.method == "POST":
        log_action(request, "login attempt", user_info=request.POST.get('email'))
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
            log_action(request, "logout attempt", user_info=payload.get('email', 'Anonymuous'))
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
            log_action(request, "Forgot password attempt", user_info=request.POST.get('email'))
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
        log_action(request, "Reset password attempt", user_info=reset_token.user.Email)
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
    
#------------------------------- Apply Now for funding ----------------------------------------

def apply(request):
    if request.method == "POST":
        try:
            log_action(request, "Funding application attempt", user_info=request.POST.get('bemail'))
            data = request.POST.dict()
            files = request.FILES.getlist('financial_statement')

            # Server-side check for max 3 files
            if len(files) > 3:
                return render(request, 'apply.html', {
                    'error': "You can upload a maximum of 3 files only.",
                    'data': request.POST  # repopulate form if needed
                })

            # Validate all uploaded PDFs
            for f in files:
                if not f.name.lower().endswith('.pdf'):
                    return render(request, 'apply.html', {'error': "Only PDF files are allowed."})
                if f.size > 10 * 1024 * 1024:
                    return render(request, 'apply.html', {'error': "Each file must be under 10MB."})

            # Map POST keys to serializer fields, normalize entity & first_time
            cleaned_data = {
                'Business_name': data.get('business_name'),
                'Doing_business_as': data.get('dba'),
                'Business_address': data.get('business_add'),
                'Industry': data.get('industry'),
                'Tax_ID': data.get('taxid'),
                'Entity': data.get('entity', '').lower() or None,
                'Business_Start_date': data.get('startdate'),
                'Owner_First_Name': data.get('fname'),
                'Owner_Middle_Name': data.get('mname'),
                'Owner_Last_Name': data.get('lname'),
                'Birth_Date': data.get('dob'),
                'Home_address': data.get('haddress'),
                'Business_Email': data.get('bemail'),
                'Phone_no': data.get('phone'),
                'SSN': data.get('ssn'),
                'Ownership': data.get('ownership_percent'),
                'Monthly_Revenue': data.get('monthly_revenue'),
                'Funds_Requested': data.get('fund'),
                'Existing_loans': data.get('existing_loans'),
                'First_time': data.get('application_no', '').lower(),
            }

            instance = UserApplications.objects.filter(SSN=cleaned_data['SSN']).first() if cleaned_data['First_time'] == "yes" else None

            serializer = UserApplicationsSerializer(instance, data=cleaned_data)
            if serializer.is_valid():
                application = serializer.save()

                # Save all PDFs
                for f in files:
                    ApplicationDocument.objects.create(application=application, file=f)

                message_text = "Application updated successfully!" if instance else "Application submitted successfully!"

                # Build HTML email body with bold labels
                rows = ''.join(
                    f"<tr><td style='border:1px solid #ccc;padding:8px;font-weight:bold;'>{field.replace('_', ' ').title()}</td>"
                    f"<td style='border:1px solid #ccc;padding:8px;'>{value}</td></tr>"
                    for field, value in serializer.validated_data.items()
                )
                email_body = f"<h3>New / Updated Business Application</h3><table style='border-collapse:collapse;border:1px solid #ccc;width:100%'>{rows}</table>"

                # Send email asynchronously with attachments
                send_graph_email_async(
                    subject="New / Updated Business Application",
                    body=email_body,
                    to_emails=[cleaned_data['Business_Email'], settings.CONTACT_EMAIL],
                    is_html=True,
                    files=files if files else None
                )

                # Redirect with success message
                return redirect(f"{reverse('apply')}?message={message_text}")

            return render(request, 'apply.html', {'error': serializer.errors})
        except Exception as e:
            return render(request, 'apply.html', {'error': str(e)})

    # GET request: show form with optional messages
    return render(request, 'apply.html', {
        'message': request.GET.get('message'),
        'error': request.GET.get('error')
    })


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
    try:
        log_action(request, "Job application attempt", user_info=request.POST.get('email'))
        job = get_object_or_404(JobDetails, Job_id=job_id)
        context = {'job': job, 'current_page': 'careers'}

        if request.method == "POST":
            data = request.POST.dict()
            resume_file = request.FILES.get('resume')

            cleaned_data = {
                'Job': job.pk,
                'First_name': data.get('fname'),
                'Last_name': data.get('lname'),
                'Email': data.get('email'),
                'Phone_no': data.get('phone'),
                'Expirence': data.get('experience'),
                'Qualification_level': data.get('qualification'),
                'Major': data.get('major'),
                'School_name': data.get('school'),
                'Degree_year': data.get('year'),
                'Expected_salary': data.get('salary') or None,
                'Gender': data.get('gender'),
                'Resume': resume_file
            }

            twenty_days_ago = date.today() - timedelta(days=20)
            if JobApplications.objects.filter(
                Email=cleaned_data['Email'], Job=job, Applied_on__gte=twenty_days_ago
            ).exists():
                return redirect(
                    f"{reverse('jobApplication', args=[job_id])}?error=You have already applied for this job within the last 20 days."
                )

            serializer = JobApplicationsSerializer(data=cleaned_data)
            if serializer.is_valid():
                instance = serializer.save()

                table_rows = ""
                for field, value in serializer.validated_data.items():
                    if field == 'Resume':
                        continue
                    pretty_field = field.replace('_', ' ').title()
                    table_rows += f"<tr><td style='border:1px solid #ccc;padding:8px;font-weight:bold;'>{pretty_field}</td><td style='border:1px solid #ccc;padding:8px;'>{value}</td></tr>"

                email_body = f"""
                    <h3>New Job Application for {job.Title}</h3>
                    <table style='border-collapse:collapse;width:90%;margin-top:10px;'>{table_rows}</table>
                    <p>Please find the attached resume for further details.</p>
                """

                files = [resume_file] if resume_file else []

                send_graph_email_async(
                    subject=f"New Job Application for {job.Title}",
                    body=email_body,
                    to_emails=[job.Email, settings.CONTACT_EMAIL],
                    is_html=True,
                    files=files
                )

                return redirect(
                    f"{reverse('jobApplication', args=[job_id])}?message=You have successfully applied for this job."
                )

            context['error'] = serializer.errors
            return render(request, "job_apply.html", context)

        context['message'] = request.GET.get('message')
        context['error'] = request.GET.get('error')
        return render(request, "job_apply.html", context)

    except Exception as e:
        context['error'] = "An unexpected error occurred. Please try again later."
        return render(request, "job_apply.html", context)


#---------------------------- Contact ----------------------------

def contact(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject', 'No Subject')
            msg_body = request.POST.get('message')

            body = f"From: {name} <{email}>\n\n{msg_body}"

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

    except Exception as e:
        return render(
            request,
            "contactus.html",
            {
                'message': "An unexpected error occurred. Please try again later.",
                'current_page': 'contact'
            }
        )

#-------------------------- lenders / Marketplace ---------------------

def lenders_marketplace(request):
    lenders_info = Lenders.objects.all().order_by('Lender_name')

    logo_map = {
        'IOU': 'lenders_logo/iou.png',
        'Kalamata': 'lenders_logo/kalamata.png',
        'PIRS': 'lenders_logo/pirs.png',
        'Wall Street': 'lenders_logo/wallstreet.png',
        'Northeastern': 'lenders_logo/northeastern.png',
        'TAB Bank': 'lenders_logo/tabbank.png',
        'Idea Financial': 'lenders_logo/idea.png',
        'Headway': 'lenders_logo/headway.png',
        'OnDeck': 'lenders_logo/ondeck.png',
        'Channel': 'lenders_logo/channel.png',
        'Libertas': 'lenders_logo/libertas.png',
        'PEAC': 'lenders_logo/peac.png',
        'Mulligan': 'lenders_logo/mulligan.png',
        'Fin Part Group': 'lenders_logo/finpart.png',
    }

    category_map = {
        'IOU': 'Merchant Cash Advance / Revenue-Based Financing',
        'Kalamata': 'Merchant Cash Advance / Revenue-Based Financing',
        'PIRS': 'Merchant Cash Advance / Revenue-Based Financing',
        'Wall Street': 'Merchant Cash Advance / Revenue-Based Financing',
        'Northeastern': 'SBA Loans',
        'TAB Bank': 'SBA Loans',
        'Idea Financial': 'Business Line of Credits',
        'Headway': 'Business Line of Credits',
        'OnDeck': 'Business Line of Credits',
        'Channel': 'Business Term Loans',
        'Libertas': 'Business Term Loans',
        'PEAC': 'Business Term Loans',
        'Mulligan': 'Business Term Loans',
        'Fin Part Group': 'Equipment Financing',
    }

    grouped_lenders = defaultdict(list)

    for lender in lenders_info:
        name = lender.Lender_name.strip()
        
        # only categorize lenders that are in your category_map
        if name in category_map:
            lender.logo_path = logo_map.get(name, 'lenders_logo/default.png')
            category = category_map[name]
            grouped_lenders[category].append(lender)
        else:
            # Skip lenders not in your predefined list
            continue

    context = {
        'lenders_info': lenders_info,               # for full table view
        'grouped_lenders': dict(grouped_lenders),   # for categorized cards
        'current_page': 'lenders',
    }
    return render(request, 'lenders_marketplace.html', context)


#-------------------------- Funding Steps --------------------------

def funding_steps(request):
    return render(request, 'funding_steps.html', {'current_page':'steps'})


#-------------------------- sell business --------------------------

def sell_business(request):
    if request.method == 'POST':

        phone = request.POST.get('phone', '').strip()
        
        # Server-side validation: must be exactly 10 digits
        import re
        if not re.fullmatch(r'\d{10}', phone):
            return render(request, 'sell_business.html', {
                'current_page': 'sell_business',
                'error': 'Phone number must be exactly 10 digits.',
                'form_data': request.POST
            })  
        
        # Collect form data
        cleaned_data = {
            'Name': request.POST.get('name'),
            'Email': request.POST.get('email'),
            'Phone': request.POST.get('phone'),
            'Business Name': request.POST.get('business_name'),
            'Industry': request.POST.get('industry'),
            'Location': request.POST.get('location'),
            'Year Established': request.POST.get('established'),
            'Annual Revenue': request.POST.get('revenue'),
            'Asking Price': request.POST.get('asking_price'),
            'Reason for Selling': request.POST.get('reason'),
            'Business Description': request.POST.get('description'),
            'Terms Accepted': 'Yes' if request.POST.get('terms') == 'on' else 'No'
        }

        print("cleaned data", cleaned_data)

        # Create HTML table
        table_rows = ""
        for field, value in cleaned_data.items():
            table_rows += f"<tr><td style='border:1px solid #ccc;padding:8px;font-weight:bold;'>{field}</td><td style='border:1px solid #ccc;padding:8px;'>{value}</td></tr>"

        email_body = f"""
        <h3>New Sell Business Submission</h3>
        <table style='border-collapse:collapse;width:100%;'>
            {table_rows}
        </table>
        """

        # Send email asynchronously
        send_graph_email_async(
            subject="New Sell Business Submission",
            body=email_body,
            to_emails=[settings.CONTACT_EMAIL],
            is_html=True
        )

        return redirect(reverse("sell_business") + "?message=Your business information has been submitted successfully!")

    # Handle GET
    return render(request, 'sell_business.html', {
        'current_page': 'sell_business',
        'message': request.GET.get('message'),
        'error': request.GET.get('error')
    })

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

