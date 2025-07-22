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

            # Prepare email in tabular format
            table_rows = ""
            for field, value in serializer.validated_data.items():
                pretty_field = field.replace("_", " ").title()
                table_rows += f"<tr><td style='border:1px solid #ccc;padding:8px;font-weight:bold;'>{pretty_field}</td><td style='border:1px solid #ccc;padding:8px;'>{value}</td></tr>"

            email_body = f"""
            <h3>New Affiliate Application Received</h3>
            <table style='border-collapse:collapse;width:100%;'>
                {table_rows}
            </table>
            """

            # Send email asynchronously without blocking
            send_graph_email_async(
                subject="New Affiliate Application Received",
                body=email_body,
                to_emails=[settings.CONTACT_EMAIL],
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