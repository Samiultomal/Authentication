#views.py
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str  
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .serializers import *
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            activation_link = reverse('verify-email', kwargs={'token': token}) + f'?uid={uid}'
            activate_url = f"http://{current_site.domain}{activation_link}"
            html_message = render_to_string('email_verification.html', {
                'user': user,
                'activation_link': activate_url
            })
            plain_message = strip_tags(html_message)
            send_mail(
                'Activate your account',
                plain_message,
                'ftextrading@gmail.com',
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'contact_number': user.contact_number.as_e164 if user.contact_number else None,
                'user_type': user.user_type
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if not user.is_email_verified:
                return Response({
                    'error': 'Email not verified. Please verify your email before logging in.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if user.user_type in ['staff', 'employee'] and not user.is_approved:
                return Response({
                    'error': 'Your account is not approved. Please contact support.'
                }, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'contact_number': user.contact_number.as_e164 if user.contact_number else None,
                'user_id': user.id  
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyEmailView(APIView):
    def get(self, request, token):
        try:
            uid = force_str(urlsafe_base64_decode(request.GET.get('uid')))
            user = User.objects.get(pk=uid)
            if account_activation_token.check_token(user, token):
                user.is_email_verified = True
                user.save()
                return redirect(f'{settings.FRONTEND_URL}/email-verification-success')
            else:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid UID'}, status=status.HTTP_400_BAD_REQUEST)
        

class EmailVerificationSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)
    
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"/reset-password/{token}?uid={uid}"
        reset_url = f"{settings.FRONTEND_URL}{reset_link}"
        html_message = render_to_string('password_reset_email.html', {
            'user': user,
            'reset_link': reset_url
        })
        plain_message = strip_tags(html_message)

        send_mail(
            'Password Reset Request',
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, token):
        uid = request.data.get('uid')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({'message': 'Password has been reset'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid UID'}, status=status.HTTP_400_BAD_REQUEST)