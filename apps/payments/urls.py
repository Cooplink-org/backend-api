from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment processing
    path('initiate/', views.initiate_payment, name='initiate-payment'),
    path('verify/', views.verify_payment, name='verify-payment'),
    path('webhook/', views.payment_webhook, name='payment-webhook'),
    
    # Transactions
    path('transactions/', views.transaction_list, name='transaction-list'),
    path('transactions/<uuid:transaction_id>/', views.transaction_detail, name='transaction-detail'),
    
    # Withdrawals
    path('withdraw/', views.request_withdrawal, name='request-withdrawal'),
    path('withdrawals/', views.withdrawal_list, name='withdrawal-list'),
    
    # Balance
    path('balance/', views.get_balance, name='get-balance'),
    path('balance/history/', views.balance_history, name='balance-history'),
    
    # Methods
    path('methods/', views.payment_methods, name='payment-methods'),
]
