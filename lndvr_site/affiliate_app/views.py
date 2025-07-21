from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from affiliate_app.models import AffiliateApplications
from django.urls import reverse
import jwt
from lndvr_site.utils.graph_email import send_graph_email


def affiliate(request):
    # Check if user is logged in by decoding JWT token cookie
    token = request.COOKIES.get('jwt_token')
    user_email = None
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_email = payload.get('email')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            user_email = None

    if request.method == 'POST':
        if not user_email:
            error = "You must be signed up and logged in to apply for the affiliate program."
            return render(request, 'affiliate.html', {
                'current_page': 'affiliates',
                'error': error,
                'form_data': request.POST,
            })

        try:
            # Collect form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            company = request.POST.get('company')
            title = request.POST.get('title')
            website = request.POST.get('website')
            business_phone = request.POST.get('business_phone')
            is_payment = request.POST.get('is_payment')
            is_influencer = request.POST.get('is_influencer')
            terms = request.POST.get('terms') == 'on'

            # Save to database
            AffiliateApplications.objects.create(
                First_name=first_name,
                Last_name=last_name,
                Email=email,
                Phone_no=phone,
                Company=company,
                Title=title,
                Website=website,
                Business_phone=business_phone,
                Is_payment=is_payment,
                Is_influencer=is_influencer,
                Terms_accepted=terms
            )

            # Prepare email
            message = f"""
                    New Affiliate Application Received

                    Name: {first_name} {last_name}
                    Email: {email}
                    Phone: {phone}
                    Company: {company}
                    Title: {title}
                    Website: {website}
                    Business Phone: {business_phone}
                    Can Receive Payments: {is_payment}
                    Is Social Media Influencer: {is_influencer}
                    Terms Accepted: {terms}
                    
                    """

            # Send email via Graph
            try:
                send_graph_email(
                    subject="New Affiliate Application Received",
                    body=message,  # plain text or HTML based on your need
                    to_emails=[settings.CONTACT_EMAIL],
                    is_html=False  # or True if sending HTML
                )
            except Exception as e:
                return redirect(reverse("affiliates") + f"?error=Failed to send notification email: {str(e)}")

            # Redirect with success
            return redirect(reverse("affiliates") + "?message=Your application has been submitted successfully!")

        except Exception as e:
            return redirect(reverse("affiliates") + f"?error={str(e)}")

    # GET Request
    message = request.GET.get('message')
    error = request.GET.get('error')

    return render(request, 'affiliate.html', {
        'current_page': 'affiliates',
        'message': message,
        'error': error,
    })