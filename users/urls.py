from django.urls import path, include

from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='registration'),
    path('activate/<uidb64>/<token>/', views.ActivateUserAPIView.as_view(), name='activate'),
    path('auth/', views.AuthTokenAPIView.as_view(), name='authentication'),
    path('profile/', views.ProfileAPIView.as_view(), name='profile')
]
