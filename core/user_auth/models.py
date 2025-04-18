from django.contrib.auth.models import AbstractUser
from django.db import models
from .user_manager import UserManager

class User(AbstractUser):
    # حذف username از مدل
    username = None
    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    objects = UserManager() 

    def __str__(self):
        return self.mobile


class OTP(models.Model):
    mobile = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    def is_valid(self, input_code):
        return self.code == input_code and not self.is_used

    @classmethod
    def create_code(cls, mobile):
        from random import randint
        code = str(randint(100000, 999999))
        # حذف OTP قبلی که ممکنه برای این موبایل ارسال شده باشه
        cls.objects.filter(mobile=mobile).delete()
        return cls.objects.create(mobile=mobile, code=code)

    def __str__(self):
        return f"OTP for {self.mobile}: {self.code}"


class LoginAttempt(models.Model):
    mobile = models.CharField(max_length=15, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    attempt_type = models.CharField(max_length=20, choices=[('password', 'Password'), ('otp', 'OTP')])
    successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)  # وضعیت بلاک
    block_until = models.DateTimeField(null=True, blank=True)  # زمان پایان بلاک

    @classmethod
    def check_if_blocked(cls, mobile=None, ip_address=None, attempt_type='password', block_after=3, block_minutes=60):
        from django.utils import timezone
        from datetime import timedelta

        time_threshold = timezone.now() - timedelta(minutes=block_minutes)

        filters = {
            "created_at__gte": time_threshold,
            "successful": False,
            "attempt_type": attempt_type
        }
        if mobile:
            filters["mobile"] = mobile
        if ip_address:
            filters["ip_address"] = ip_address

        attempts = cls.objects.filter(**filters)
        failed_attempts = attempts.count()

        # بررسی اینکه آیا بیش از حد تلاش ناموفق بوده است
        if failed_attempts >= block_after:
            block_until = timezone.now() + timedelta(minutes=block_minutes)
            # به‌روزرسانی وضعیت بلاک برای شماره موبایل یا IP
            if mobile:
                attempts.update(is_blocked=True, block_until=block_until)
            if ip_address:
                attempts.update(is_blocked=True, block_until=block_until)

            return True  # نشان می‌دهد که بلاک شده است
        return False  # هنوز بلاک نشده است

    @classmethod
    def log(cls, mobile=None, ip_address=None, attempt_type='password', successful=False):
        return cls.objects.create(
            mobile=mobile,
            ip_address=ip_address,
            attempt_type=attempt_type,
            successful=successful
        )

    def __str__(self):
        return f"Attempt from {self.ip_address or self.mobile} for {self.attempt_type}"
