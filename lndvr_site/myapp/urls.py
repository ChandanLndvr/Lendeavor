"""
URL configuration for lndvr_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.contrib.auth import views as auth_views #inbuilt views by django

urlpatterns = [
    path('', views.main, name = "mainPage"),
    path('signup/', views.signUp, name = "signup"),
    path('login/', views.login, name = "login"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<str:token>/", views.reset_password, name="reset_password"),
    path("aboutus/", views.aboutus, name="aboutus"),
    path("products/", views.products, name="products"),
    path("contact/", views.contact, name="contact"),
    path("careers/", views.career_page, name='careers'),
    path("apply/", views.apply, name = "apply"),
    path("steps/", views.funding_steps, name = "steps"),
    path("caseStudy/", views.case_study, name = "caseStudy"),
    path("faq/", views.faq, name = "faq"),
    path("terms/", views.terms, name = "terms"),
    path("privacy/", views.privacy, name = "privacy"),
    path("careers/application/<uuid:job_id>/", views.job_applications, name = "jobApplication"),
    path("job/", include("job_posting_app.urls")),
    path("affiliate/", include("affiliate_app.urls")),
]
