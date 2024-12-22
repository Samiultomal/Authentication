from django.urls import path
from . import views
urlpatterns = [
    
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('email-verification-success/', views.EmailVerificationSuccessView.as_view(), name='email_verification_success'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    
]

