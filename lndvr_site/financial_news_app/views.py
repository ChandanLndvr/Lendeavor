from django.shortcuts import render, redirect
from financial_news_app.models import Financial_news
from financial_news_app.serializers import Financial_news_serializers
from django.urls import reverse
from myapp.models import SignUp
from django.shortcuts import get_object_or_404
from myapp.custom_middleware.log_ip import log_action
from django.conf import settings
import jwt
# Create your views here.


#------------------------- Financial News --------------------------

def financial_news(request):
    financial_data = Financial_news.objects.all()
    message = request.GET.get('message')
    error = request.GET.get('error')
    print(financial_data)
    context = {
        'financial_data': financial_data, 
        'current_page':'financial_news',
        'message': message,
        'error': error
    }
    return render(request, 'financial_news.html', context)
        

def add_news(request):
    token = request.COOKIES.get('jwt_token')
    user_email = None
    added_by_user = None

    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_email = payload.get('email')
            if user_email:
                added_by_user = get_object_or_404(SignUp, Email=user_email)
                if added_by_user.User_type.lower() != 'admin':
                    log_action(request, "Unauthorized news add attempt (not admin)", user_info=user_email)
                    return render(request, 'add_news.html', {
                        'error': "Only admin users are allowed to add news.",
                        'current_page': 'financial_news',
                        'user_email': user_email,
                    })
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            log_action(request, "JWT error on add_news", user_info=str(token))
            return redirect(reverse('login') + "?error=Session expired, please log in again.")

    else:
        log_action(request, "Anonymous news add attempt", user_info="No token")
        return redirect(reverse('login') + "?error=You must be logged in to add news.")

    if request.method == "POST":
        log_action(request, "Add news attempt", user_info=user_email)
        cleaned_data = {
            'Title': request.POST.get('title'),
            'Date_publish': request.POST.get('date_publish'),
            'Content': request.POST.get('content'),
            'Summary': request.POST.get('summary'),
            'Added_by': added_by_user.pk,  # Always set from logged-in user
            'Active': request.POST.get('active') == 'on',
        }

        if 'thumbnail' in request.FILES:
            cleaned_data['Thumbnail'] = request.FILES['thumbnail']

        serializer = Financial_news_serializers(data=cleaned_data)

        if serializer.is_valid():
            serializer.save()
            log_action(request, "News added successfully", user_info=user_email)
            return redirect(reverse('financial_news') + "?message=News added successfully!")
        else:
            log_action(request, "News add failed: validation error", user_info=user_email)
            return render(request, 'add_news.html', {
                'error': serializer.errors,
                'current_page': 'financial_news',
                'user_email': user_email,
                'form_data': request.POST,
            })

    # GET request: render form with email filled in readonly field
    return render(request, 'add_news.html', {
        'current_page': 'financial_news',
        'user_email': user_email,
        'message': request.GET.get('message'),
        'error': request.GET.get('error'),
    })
