from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('create-account/', views.create_account, name='create_account'),
    path('thank_you/', views.thank_you, name='thankyou'),
    path('pin-generation/', views.pin_generation, name='pin_generation'),
    path('validate-otp/', views.validate_otp, name='validate_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('check-balance/',views.check_balance,name='check_balance'),
    path('money-deposit/',views.deposit, name='deposit'),
    path('money-withdrawal/',views.withdrawal,name='withdrawal'),
    path('account-transfer/',views.account_transfer,name='account_transfer'),
    path('transactions/', views.transaction_history, name='transactions'),

]
