from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import MobileInputForm, UserInfoForm, OTPForm, PasswordForm
from .models import OTP, LoginAttempt
from .utils import block_mobile, block_ip
from django.contrib.auth import authenticate, login, logout
User = get_user_model()



class MobileInputView(FormView):
    template_name = 'mobile_input.html'
    form_class = MobileInputForm
    success_url = '/verify-otp/'  # این بخش برای هدایت به صفحه تایید OTP است

    def form_valid(self, form):
        mobile = form.cleaned_data.get('mobile')
        ip = self.request.META.get('REMOTE_ADDR')

        # چک وجود کاربر
        User = get_user_model()
        user_exists = User.objects.filter(mobile=mobile).exists()

        if user_exists:
            # شماره را در سشن ذخیره می‌کنیم
            self.request.session['mobile'] = mobile
            return redirect('login_password')  # هدایت به صفحه وارد کردن رمز عبور

        # ✅ فقط در این حالت که کاربر وجود نداره، چک بلاک و لاگ ثبت می‌کنیم
        if LoginAttempt.check_if_blocked(mobile=mobile, ip_address=ip, attempt_type='otp'):
            messages.error(self.request, "به دلیل تلاش‌های زیاد، شماره یا آی‌پی شما موقتاً بلاک شده است.")
            return redirect('mobile_input')

        login_attempt = LoginAttempt.log(mobile=mobile, ip_address=ip, attempt_type='otp', successful=False)

        # بررسی مجدد بلاک بودن (بعد از لاگ)
        if LoginAttempt.check_if_blocked(mobile=mobile, ip_address=ip, attempt_type='otp'):
            messages.error(self.request, "شما به دلیل تلاش‌های زیاد موقتاً بلاک شده‌اید.")
            return redirect('mobile_input')

        # اگر کاربر وجود نداشته باشد، OTP ارسال کنید
        otp = OTP.create_code(mobile)
        print(f"Sending OTP {otp.code} to {mobile}")
        self.request.session['otp_code'] = otp.code  # فقط برای تست، بعداً حذف بشه

        self.request.session['mobile'] = mobile
        messages.success(self.request, "کد تأیید برای شما ارسال شد.")
        return redirect('verify_otp')




class SendOTPView(View):
    def get(self, request):
        return render(request, 'send_otp.html')  # فرم دریافت شماره

    def post(self, request):
        mobile = request.POST.get('mobile')
        ip = request.META.get('REMOTE_ADDR')

        # بررسی بلاک بودن شماره یا آی‌پی برای OTP
        if LoginAttempt.check_if_blocked(mobile=mobile, attempt_type='otp', block_after=4) or \
           LoginAttempt.check_if_blocked(ip_address=ip, attempt_type='otp', block_after=4):
            messages.error(request, "شما به دلیل تلاش‌های زیاد، موقتاً بلاک شده‌اید.")
            return redirect('send_otp')

        # ثبت تلاش ناموفق دریافت OTP
        LoginAttempt.log(mobile=mobile, ip_address=ip, attempt_type='otp', successful=False)

        # بررسی مجدد بلاک شدن پس از ثبت تلاش
        if LoginAttempt.check_if_blocked(mobile=mobile, attempt_type='otp', block_after=4):
            messages.error(request, "شماره شما به دلیل تلاش زیاد برای دریافت کد، بلاک شده است.")
            return redirect('send_otp')

        if LoginAttempt.check_if_blocked(ip_address=ip, attempt_type='otp', block_after=4):
            messages.error(request, "آی‌پی شما به دلیل تلاش زیاد برای دریافت کد، بلاک شده است.")
            return redirect('send_otp')

        # ساخت و ارسال OTP
        otp = OTP.create_code(mobile)
        print(f"Sending OTP {otp.code} to {mobile}")  # برای تست
        request.session['otp_code'] = otp.code  # فقط برای تست، بعداً حذف بشه


        request.session['mobile'] = mobile
        return redirect('verify_otp')


class VerifyOTPView(View):
    template_name = 'verify_otp.html'

    def get(self, request):
        form = OTPForm()
        otp_code = request.session.get('otp_code')  # فقط برای تست
        return render(request, self.template_name, {'form': form, 'test_otp': otp_code})

    def post(self, request):
        form = OTPForm(request.POST)
        mobile = request.session.get('mobile')
        ip_address = request.META.get('REMOTE_ADDR')

        if not mobile:
            messages.error(request, 'شماره موبایل یافت نشد.')
            return redirect('mobile_input')

        # چک کنیم بلاک شده یا نه
        if LoginAttempt.check_if_blocked(
            mobile=mobile,
            ip_address=ip_address,
            attempt_type='otp',
            block_after=4,
            block_minutes=60
        ):
            messages.error(request, 'تعداد تلاش‌های ناموفق زیاد بوده. لطفاً بعداً امتحان کنید.')
            return render(request, self.template_name, {'form': form})

        if form.is_valid():
            otp = form.cleaned_data['otp']
            try:
                otp_instance = OTP.objects.get(mobile=mobile, code=otp, is_used=False)
            except OTP.DoesNotExist:
                # ذخیره تلاش ناموفق
                LoginAttempt.log(mobile=mobile, ip_address=ip_address, attempt_type='otp', successful=False)
                messages.error(request, 'کد وارد شده اشتباه است.')
                return render(request, self.template_name, {'form': form})

            # موفقیت
            otp_instance.is_used = True
            otp_instance.save()

            LoginAttempt.log(mobile=mobile, ip_address=ip_address, attempt_type='otp', successful=True)

            # پیدا کردن یا ساختن کاربر
            user, created = User.objects.get_or_create(mobile=mobile)

            # ذخیره آیدی یوزر تو سشن
            request.session['user_id'] = user.id

            return redirect('complete_info')  # یا هر صفحه‌ای که میخوای
        else:
            messages.error(request, 'لطفاً کد OTP معتبر وارد کنید.')
            return render(request, self.template_name, {'form': form})



class LoginWithPasswordView(View):
    def get(self, request):
        form = PasswordForm()
        return render(request, 'login_password.html', {'form': form})

    def post(self, request):
        form = PasswordForm(request.POST)
        if form.is_valid():
            mobile = request.session.get('mobile')  # موبایل از session گرفته میشه
            password = form.cleaned_data.get('password')
            ip = request.META.get('REMOTE_ADDR')

            # بررسی بلاک بودن
            if LoginAttempt.check_if_blocked(mobile=mobile, ip_address=ip, attempt_type='password'):
                messages.error(request, "شما به دلیل تلاش‌های زیاد، موقتاً بلاک شده‌اید.")
                return redirect('login_password')

            print('username:', mobile)
            print('pass:', password)
            user = authenticate(username=mobile, password=password)
            if user:
                login(request, user)
                # لاگ کردن تلاش موفق
                LoginAttempt.log(mobile=mobile, ip_address=ip, attempt_type='password', successful=True)
                return redirect('dashboard')
            else:
                # لاگ کردن تلاش ناموفق
                LoginAttempt.log(mobile=mobile, ip_address=ip, attempt_type='password', successful=False)
                messages.error(request, "شماره یا رمز عبور اشتباه است.")
                return redirect('login_password')
        else:
            return render(request, 'login_password.html', {'form': form})



class CompleteProfileView(FormView):
    template_name = 'user_info.html'
    form_class = UserInfoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = PasswordForm()
        return context

    def form_valid(self, form):
        mobile = self.request.session.get('mobile')
        if not mobile:
            return redirect('send_otp')

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            messages.error(self.request, "کاربری با این شماره پیدا نشد.")
            return redirect('mobile_input')

        # بروزرسانی اطلاعات فرم
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        
        password_form = PasswordForm(self.request.POST)
        if password_form.is_valid():
            user.set_password(password_form.cleaned_data['password'])
            user.save()
            login(self.request, user)
            messages.success(self.request, "ثبت‌نام با موفقیت انجام شد.")
            return render(self.request, 'dashboard.html', {'user': user})
        else:
            return render(self.request, 'user_info.html', {
                'form': form,
                'password_form': password_form
            })

class DashboardView(View):
    def get(self, request):
        user = request.user
        return render(request, 'dashboard.html', {'user': user})


