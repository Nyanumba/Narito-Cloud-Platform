from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
import uuid

from .models import EmailVerificationToken
from .utilis import send_verification_email
from .serializers import RegisterSerializer  # your existing serializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send verification email after registration
            token_obj = EmailVerificationToken.objects.create(user=user)
            send_verification_email(user, token_obj.token)

            return Response(
                {'message': 'Registration successful. Please check your email to verify your account.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')

        if not token:
            return Response({'error': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token_obj = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_obj.is_expired():
            token_obj.delete()
            return Response(
                {'error': 'Token has expired. Please request a new verification email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user
        user.is_email_verified = True
        user.save()
        token_obj.delete()

        return Response({'message': 'Email verified successfully. You can now log in.'}, status=status.HTTP_200_OK)


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Vague on purpose to avoid user enumeration
            return Response({'message': 'If that email exists, a verification link has been sent.'}, status=status.HTTP_200_OK)

        if user.is_email_verified:
            return Response({'error': 'This email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        # Rotate the token
        EmailVerificationToken.objects.filter(user=user).delete()
        token_obj = EmailVerificationToken.objects.create(user=user)
        send_verification_email(user, token_obj.token)

        return Response({'message': 'If that email exists, a verification link has been sent.'}, status=status.HTTP_200_OK)