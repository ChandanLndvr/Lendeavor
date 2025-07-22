import jwt
from django.conf import settings
from myapp.models import SignUp

def get_logged_in_user_email(request):
    token = request.COOKIES.get('jwt_token')
    if not token:
        return "Anonymous"
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        email = payload.get('email')
        if email:
            user = SignUp.objects.filter(Email=email).first()
            if user:
                return user.Email
    except jwt.InvalidTokenError:
        pass
    return "Anonymous"
