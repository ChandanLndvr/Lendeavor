from django.shortcuts import render, redirect
from financial_news_app.models import Financial_news
from financial_news_app.serializers import Financial_news_serializers
from django.urls import reverse
from myapp.models import SignUp
from django.shortcuts import get_object_or_404
from myapp.custom_middleware.log_ip import log_action
from django.conf import settings
import jwt
from myapp.utils.auth_utils import decode_jwt
# Create your views here.


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
            return None, email, render(request, "financial_news.html", {
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


#------------------------- Financial News --------------------------

def financial_news(request):
    # Fetch financial news sorted descending by Date_publish
    financial_data = Financial_news.objects.filter(Active=True).order_by('-Date_publish')[:20]

    message = request.GET.get('message')
    error = request.GET.get('error')
    # print(financial_data)
    token = request.COOKIES.get('jwt_token')
    user_type = None

    if token:
        payload = decode_jwt(token)
        if payload:
            user_type = payload.get('user_type')

    show_admin_tools = (str(user_type).lower() == 'admin')
    context = {
        'financial_data': financial_data, 
        'current_page':'financial_news',
        'show_admin_tools': show_admin_tools,
        'message': message,
        'error': error
    }
    return render(request, 'financial_news.html', context)
        
#---------------------- add the financial news -------------------

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
            'Active': True if request.POST.get('active') == 'on' else False,
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


#------------------------- To see the particular news ------------------------

def news_info(request, news_id):
    try:
        news = get_object_or_404(Financial_news, News_id=news_id)
        context = {
            'news': news,
            'current_page': 'financial_news'
        }
        return render(request, 'news_info.html', context)
    except Exception as e:
        # Add error message to context for the template to display
        return render(request, 'news_info.html', {
            'news': None,
            'current_page': 'financial_news',
            'error': f"An error occurred: {str(e)}"
        })  

#----------------------- update or delete the single job ---------------------------

def update_or_delete_news(request, news_id):
    """
    View to update or delete a Financial_news object based on POST action.
    Only accessible to admin users validated via JWT.
    """
    news = get_object_or_404(Financial_news, News_id=news_id)

    # Validate the user is admin
    added_by_user, user_email, error_response = validate_admin_user(request)
    if error_response:
        return error_response

    if request.method == "POST":
        action = request.POST.get("action")
        log_action(request, f"News action attempted: {action}", user_info=user_email)

        if action == "update":
            try:
                # Copy POST data dict to mutable dict
                data = {
                    'Title': request.POST.get('title'),
                    'Date_publish': request.POST.get('date_publish'),
                    'Content': request.POST.get('content'),
                    'Summary': request.POST.get('summary'),
                    'Added_by': added_by_user.pk,
                    'Active': True if request.POST.get('active') == 'on' else False,
                }

                # If new file uploaded, add to data
                if 'thumbnail' in request.FILES:
                    data['Thumbnail'] = request.FILES['thumbnail']

                # No 'files' argument - just pass 'data'
                serializer = Financial_news_serializers(news, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    log_action(request, "News updated successfully", user_info=user_email)
                    return redirect(reverse("financial_news") + "?message=News updated successfully.")
                else:
                    log_action(request, f"Update validation errors: {serializer.errors}", user_info=user_email)
                    return redirect(reverse("editNews", args=[news.News_id]) + f"?error=Update failed: {serializer.errors}")

            except Exception as e:
                log_action(request, f"Exception during update: {str(e)}", user_info=user_email)
                return redirect(reverse("editNews", args=[news.News_id]) + f"?error=An error occurred while updating: {str(e)}")
            
        elif action == "delete":
            try:
                log_action(request, "Single news delete attempt", user_info=user_email)
                news.delete()
                log_action(request, "News deleted successfully", user_info=user_email)
                return redirect(reverse("financial_news") + "?message=News deleted successfully.")
            except Exception as e:
                log_action(request, f"Exception during delete: {str(e)}", user_info=user_email)
                return redirect(reverse("editNews", args=[news.News_id]) + f"?error=An error occurred: {str(e)}")

    # For GET (or fallback), render the edit page with current news data
    return render(request, "update_news.html", {
        'news': news,
        'current_page': 'careers'
    })
    

#----------------------- Bulk delete -------------------

def bulk_delete_news(request):
    added_by_user, user_email, error_response = validate_admin_user(request)
    if error_response:
        return error_response

    if request.method == "POST":
        news_id = request.POST.getlist("news_id")

        if not news_id:
            return redirect(reverse("financial_news") + "?error=No news selected for deletion.")

        try:
            log_action(request, "Bulk news delete attempt", user_info=user_email)
            Financial_news.objects.filter(News_id__in=news_id).delete()
            return redirect(reverse("financial_news") + "?message=Selected news deleted successfully.")
        except Exception as e:
            return redirect(reverse("financial_news") + f"?error=Error during deletion: {str(e)}")

    # If GET or other method, redirect safely
    return redirect(reverse("financial_news") + "?error=Invalid request method for bulk deletion.")

