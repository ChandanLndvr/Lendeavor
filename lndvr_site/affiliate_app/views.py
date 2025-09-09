from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
import jwt
from .serializers import AffiliateApplicationsSerializer
from lndvr_site.utils.send_graph_email_async import send_graph_email_async
from myapp.custom_middleware.log_ip import log_action

def affiliate(request):
    token = request.COOKIES.get('jwt_token')
    user_email = None

    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_email = payload.get('email')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            user_email = None

    if request.method == 'POST':
        log_action(request, "Affiliate application attempt", user_info=request.POST.get('email'))
        if not user_email:
            return render(request, 'affiliate.html', {
                'current_page': 'affiliates',
                'error': "You must be signed up and logged in to apply for the affiliate program.",
                'form_data': request.POST
            })

        cleaned_data = {
            'First_name': request.POST.get('first_name'),
            'Last_name': request.POST.get('last_name'),
            'Email': request.POST.get('email'),
            'Phone_no': request.POST.get('phone'),
            'Company': request.POST.get('company'),
            'Title': request.POST.get('title'),
            'Website': request.POST.get('website'),
            'Business_phone': request.POST.get('business_phone'),
            'Is_payment': request.POST.get('is_payment'),
            'Is_influencer': request.POST.get('is_influencer'),
            'Terms_accepted': request.POST.get('terms') == 'on'
        }

        serializer = AffiliateApplicationsSerializer(data=cleaned_data)

        if serializer.is_valid():
            instance = serializer.save()

            # Build HTML table rows with bold labels
            rows = ''.join(
                f"<tr>"
                f"<td style='border:1px solid #ccc;padding:8px;font-weight:bold;'>{field.replace('_', ' ').title()}</td>"
                f"<td style='border:1px solid #ccc;padding:8px;'>{value}</td>"
                f"</tr>"
                for field, value in serializer.validated_data.items()
            )

            # Extract applicant's name for email subject/body
            first_name = cleaned_data.get("First_name", "")
            last_name = cleaned_data.get("Last_name", "")

            # Email body for the company
            company_email_body = (
                f"<h3>New Affiliate Application from {first_name} {last_name}</h3>"
                f"<table style='border-collapse:collapse;border:1px solid #ccc;width:100%'>{rows}</table>"
            )

            # Email body for the user
            user_email_body = (
                "<h3>Thank you for applying at Lendeavor</h3>"
                "<p>We appreciate your interest in our 'Affiliate Program'. Our team will get in touch with you shortly.</p>"
                "<p>Here’s a copy of your submitted application details:</p>"
                f"<table style='border-collapse:collapse;border:1px solid #ccc;width:100%'>{rows}</table>"
            )

            # Send email to company
            send_graph_email_async(
                subject=f"New Affiliate Application from {first_name} {last_name}",
                body=company_email_body,
                to_emails=[settings.CONTACT_EMAIL],
                is_html=True
            )

            # Send email to user
            send_graph_email_async(
                subject="Your Affiliate Application at Lendeavor",
                body=user_email_body,
                to_emails=[serializer.validated_data.get('Email')],
                is_html=True
            )

            return redirect(reverse("affiliates") + "?message=Your application has been submitted successfully!")

        else:
            return render(request, 'affiliate.html', {
                'current_page': 'affiliates',
                'error': serializer.errors,
                'form_data': request.POST
            })

    # Handle GET
    return render(request, 'affiliate.html', {
        'current_page': 'affiliates',
        'message': request.GET.get('message'),
        'error': request.GET.get('error')
    })