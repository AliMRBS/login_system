from django.utils import timezone
from datetime import timedelta
from .models import LoginAttempt

def block_mobile(mobile, block_minutes=60):
    """
    بلاک کردن شماره موبایل به مدت 60 دقیقه (یا هر زمان دلخواه)
    """
    block_until = timezone.now() + timedelta(minutes=block_minutes)
    # به‌روزرسانی وضعیت بلاک برای شماره موبایل
    LoginAttempt.objects.filter(mobile=mobile).update(is_blocked=True, block_until=block_until)
    print(f"Blocking mobile {mobile} until {block_until}")

def block_ip(ip_address, block_minutes=60):
    """
    بلاک کردن IP به مدت 60 دقیقه (یا هر زمان دلخواه)
    """
    block_until = timezone.now() + timedelta(minutes=block_minutes)
    # به‌روزرسانی وضعیت بلاک برای IP
    LoginAttempt.objects.filter(ip_address=ip_address).update(is_blocked=True, block_until=block_until)
    print(f"Blocking IP {ip_address} until {block_until}")
