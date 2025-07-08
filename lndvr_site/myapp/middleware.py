from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from myapp.models import BlacklistedToken

#---------- Middleware to Check Blacklist and Redirect Cleanly -----------

class JWTBlacklistMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.COOKIES.get('jwt_token')
        if token and BlacklistedToken.objects.filter(token=token).exists():
            response = redirect(reverse('login') + "?error=Session expired or logged out. Please log in again.")
            response.delete_cookie('jwt_token')
            return response
        return None