from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.conf import settings
from affiliate_app.models import AffiliateApplications
from django.urls import reverse

def affiliate(request):
    if request.method == 'POST':
        try:
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

            # Save to DB
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

            # Prepare and send email
            subject = "New Affiliate Application Received"
            message = (
                f"New Affiliate Application:\n\n"
                f"Name: {first_name} {last_name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n"
                f"Company: {company}\n"
                f"Title: {title}\n"
                f"Website: {website}\n"
                f"Business Phone: {business_phone}\n"
                f"Can Receive Payments: {is_payment}\n"
                f"Is Social Media Influencer: {is_influencer}\n"
                f"Terms Accepted: {terms}\n"
            )
            email_message = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
            )
            email_message.send(fail_silently=False)

            # Redirect with success message
            return redirect(reverse("affiliates") + "?message=Your application has been submitted successfully!")

        except Exception as e:
            # Redirect with error message
            return redirect(reverse("affiliates") + f"?error={str(e)}")

    # Extract messages on GET
    message = request.GET.get('message')
    error = request.GET.get('error')

    return render(request, 'affiliate.html', {
        'current_page': 'affiliates',
        'message': message,
        'error': error
    })