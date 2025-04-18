from django.urls import path
from . import views
urlpatterns = [
    path('mobile-input/', views.MobileInputView.as_view(), name='mobile_input'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', views.LoginWithPasswordView.as_view(), name='login_password'),
    path('complete-info/', views.CompleteProfileView.as_view(), name='complete_info'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
