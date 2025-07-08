from rest_framework import serializers
from .models import PaymentMethod, Transaction, WithdrawalRequest, BalanceTransaction


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ('id', 'name', 'method_type', 'commission_rate', 'min_amount', 
                 'max_amount', 'description', 'icon')


class TransactionSerializer(serializers.ModelSerializer):
    payment_method = PaymentMethodSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_type', 'status', 'amount', 'commission_amount', 
                 'net_amount', 'currency', 'payment_method', 'description', 
                 'created_at', 'completed_at')


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ('id', 'amount', 'commission_amount', 'net_amount', 'payment_method', 
                 'payment_details', 'status', 'rejection_reason', 'created_at', 
                 'processed_at', 'completed_at')


class BalanceTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceTransaction
        fields = ('id', 'transaction_type', 'amount', 'balance_before', 'balance_after', 
                 'description', 'created_at')
