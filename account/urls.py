from django.urls import path

from .views import RegisterView, LoginView, UserInfoView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('info/', UserInfoView.as_view()),
]