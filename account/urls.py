from django.urls import path

from .views import (RegisterView, LoginView, UserInfoView,
                    LogoutView, EditProfileView, VerifyEmailView,
                    VerificationSessionView, SendPasswordCodeView,
                    ResetPasswordView, SendNewCodeView)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('info/<str:username>/', UserInfoView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("edit/", EditProfileView.as_view()),
    path("email/verify/", VerifyEmailView.as_view()), #checked
    path("email/new_code/", SendNewCodeView.as_view()), #checked
    path("email/verify/session/", VerificationSessionView.as_view()),
    path("reset/send/", SendPasswordCodeView.as_view()), #checked
    path("reset/confirm/", ResetPasswordView.as_view()), #checked
]