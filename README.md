# Django OTP Authentication (Test Mode)

این یک پروژه‌ی ساده احراز هویت با استفاده از OTP در فریم‌ورک Django است.

## ویژگی‌ها

- دریافت شماره موبایل از کاربر
- تولید و ارسال کد OTP
- نمایش OTP به‌صورت آزمایشی در صفحه‌ی تأیید
- بررسی تلاش‌های ناموفق و بلاک کردن موقتی آی‌پی یا شماره

## نصب و اجرا

### 1. کلون کردن پروژه

```bash
git clone https://github.com/ALIMRBS/login_system.git
cd login_system
```
### 2. ساخت محیط مجازی (اختیاری ولی توصیه‌شده)

```bash
python -m venv venv
source venv/bin/activate  # ویندوز: venv\Scripts\activate
```

### 3. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 4. اجرای مایگریشن‌ها

```bash
python manage.py migrate
```

### 5. اجرای سرور

```bash
python manage.py runserver
```

### 6. آدرس‌های مهم

- دریافت شماره: http://127.0.0.1:8000/mobile-input/
- وارد کردن کد: http://127.0.0.1:8000/verify-otp/
- وارد کردن رمزعبور: http://127.0.0.1:8000/login-password/
- تکمیل کردن اطلاعات: http://127.0.0.1:8000/complete-info/
- داشبورد(ورود موفق): http://127.0.0.1:8000/dashboard/

---

> ⚠️ **توجه:** این پروژه برای اهداف آموزشی است و ارسال واقعی OTP (مثلاً با پیامک) انجام نمی‌دهد.

---
