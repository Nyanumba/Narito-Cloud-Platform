from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user, token):
    verification_url = f"{settings.FRONTEND_URL}/api/auth/verify-email/?token={token}"
    send_mail(
        subject = "Verify your Narito Cloud Email",
        message = (
            f"Hello {user.username},\n\n"
            f"Please verify your email by clicking the link below:\n\n"
            f"{verification_url}\n\n"
            f"This link expires in 24 hours.\n\n"
            f"If you did not create the account, ignore this email."
            
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )