from django.shortcuts import render, redirect
from django.http import HttpResponse
from myapp.models import SignUp
from myapp.utils.auth_utils import hash_password, verify_password, generate_jwt
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
import uuid

def main(request):
    return render(request, 'mainPage.html')

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


# login with JWT Auth

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

# Views for Forgot/Reset

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