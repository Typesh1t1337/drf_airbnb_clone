from django.urls import path

from .views import RegisterView, LoginView, UserInfoView, LogoutView, EditProfileView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('info/<str:username>/', UserInfoView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("edit/", EditProfileView.as_view())
]