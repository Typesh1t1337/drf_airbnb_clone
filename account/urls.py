from django.urls import path

from .views import (RegisterView, LoginView, UserInfoView,
                    LogoutView, EditProfileView, VerifyEmailView,
                    VerificationSessionView, SendPasswordCodeView, ResetPasswordView)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('info/<str:username>/', UserInfoView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("edit/", EditProfileView.as_view()),
    path("email/verify/", VerifyEmailView.as_view()),
    path("/emai/verify/session/", VerificationSessionView.as_view()),
    path("reset/send/", SendPasswordCodeView.as_view()),
    path("reset/confirm/", ResetPasswordView.as_view()),
]