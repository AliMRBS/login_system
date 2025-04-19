from django import forms
from .models import User
from django.core.validators import RegexValidator


class MobileInputForm(forms.Form):
    mobile = forms.CharField(
        max_length=11,
        validators=[RegexValidator(
            regex=r"^09\d{9}$",
            message="شماره موبایل باید ۱۱ رقمی و با 09 شروع شود.",
            code="invalid_mobile"
        )]
    )

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        return mobile


class PasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور'}))

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'کد OTP'}))

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise forms.ValidationError("کد OTP باید فقط شامل اعداد باشد.")
        if len(otp) != 6:
            raise forms.ValidationError("کد OTP باید ۶ رقم باشد.")
        return otp


class UserInfoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 6:
            raise forms.ValidationError("رمز عبور باید حداقل ۶ کاراکتر باشد.")
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("رمز عبور و تکرار آن باید مشابه باشند.")
        return confirm_password
