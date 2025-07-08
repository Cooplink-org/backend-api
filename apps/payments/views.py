from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q, Sum
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import structlog

from .models import PaymentMethod, Transaction, WithdrawalRequest, BalanceTransaction
from .services import MirPayService
from apps.projects.models import Purchase

logger = structlog.get_logger(__name__)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['GET'])
@permission_classes([AllowAny])
def payment_methods(request):
    """Get available payment methods"""
    methods = PaymentMethod.objects.filter(is_active=True)
    data = []
    
    for method in methods:
        data.append({
            'id': method.id,
            'name': method.name,
            'method_type': method.method_type,
            'commission_rate': float(method.commission_rate),
            'min_amount': float(method.min_amount),
            'max_amount': float(method.max_amount),
            'description': method.description,
            'icon': method.icon.url if method.icon else None
        })
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='10/m', method='POST')
def initiate_payment(request):
    """Initiate payment for a purchase"""
    try:
        purchase_id = request.data.get('purchase_id')
        payment_method_id = request.data.get('payment_method_id')
        
        if not purchase_id or not payment_method_id:
            return Response(
                {'error': 'Purchase ID and payment method are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get purchase
        try:
            purchase = Purchase.objects.get(
                id=purchase_id,
                buyer=request.user,
                status='pending'
            )
        except Purchase.DoesNotExist:
            return Response(
                {'error': 'Purchase not found or already processed'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get payment method
        try:
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id,
                is_active=True
            )
        except PaymentMethod.DoesNotExist:
            return Response(
                {'error': 'Invalid payment method'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate amounts
        amount = purchase.amount_uzs
        commission = amount * payment_method.commission_rate
        net_amount = amount - commission
        
        # Create transaction
        transaction = Transaction.objects.create(
            user=request.user,
            transaction_type='purchase',
            amount=amount,
            commission_amount=commission,
            net_amount=net_amount,
            payment_method=payment_method,
            purchase=purchase,
            description=f"Purchase of {purchase.project.title}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Process payment based on method
        if payment_method.method_type == 'balance':
            # Pay with account balance
            if request.user.balance >= amount:
                # Deduct from balance
                request.user.balance -= amount
                request.user.save()
                
                # Create balance transaction
                BalanceTransaction.objects.create(
                    user=request.user,
                    transaction_type='debit',
                    amount=amount,
                    balance_before=request.user.balance + amount,
                    balance_after=request.user.balance,
                    related_transaction=transaction,
                    description=f"Purchase payment: {purchase.project.title}"
                )
                
                # Complete transaction
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                transaction.save()
                
                # Complete purchase
                purchase.status = 'completed'
                purchase.completed_at = timezone.now()
                purchase.save()
                
                return Response({
                    'success': True,
                    'transaction_id': transaction.id,
                    'message': 'Payment completed successfully'
                })
            else:
                transaction.status = 'failed'
                transaction.failure_reason = 'Insufficient balance'
                transaction.save()
                
                return Response(
                    {'error': 'Insufficient balance'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif payment_method.method_type in ['mirpay', 'click', 'payme']:
            # Use external payment gateway
            payment_service = MirPayService()
            payment_url = payment_service.create_payment(
                transaction_id=str(transaction.id),
                amount=amount,
                description=transaction.description,
                success_url=request.build_absolute_uri('/payment/success/'),
                failure_url=request.build_absolute_uri('/payment/failure/')
            )
            
            if payment_url:
                return Response({
                    'success': True,
                    'payment_url': payment_url,
                    'transaction_id': transaction.id
                })
            else:
                transaction.status = 'failed'
                transaction.failure_reason = 'Payment gateway error'
                transaction.save()
                
                return Response(
                    {'error': 'Payment gateway error'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        else:
            return Response(
                {'error': 'Unsupported payment method'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error("Payment initiation error", error=str(e))
        return Response(
            {'error': 'Payment processing error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_payment(request):
    """Verify payment status"""
    try:
        transaction_id = request.data.get('transaction_id')
        
        if not transaction_id:
            return Response(
                {'error': 'Transaction ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # If transaction is already completed, return success
        if transaction.status == 'completed':
            return Response({
                'success': True,
                'status': 'completed',
                'transaction': {
                    'id': transaction.id,
                    'amount': float(transaction.amount),
                    'status': transaction.status,
                    'created_at': transaction.created_at
                }
            })
        
        # Verify with payment gateway if needed
        if transaction.payment_method.method_type in ['mirpay', 'click', 'payme']:
            payment_service = MirPayService()
            is_verified = payment_service.verify_payment(transaction.external_transaction_id)
            
            if is_verified:
                # Complete transaction
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                transaction.save()
                
                # Complete purchase if exists
                if transaction.purchase:
                    transaction.purchase.status = 'completed'
                    transaction.purchase.completed_at = timezone.now()
                    transaction.purchase.save()
                
                return Response({
                    'success': True,
                    'status': 'completed'
                })
            else:
                return Response({
                    'success': False,
                    'status': transaction.status
                })
        
        return Response({
            'success': False,
            'status': transaction.status
        })
        
    except Exception as e:
        logger.error("Payment verification error", error=str(e))
        return Response(
            {'error': 'Verification error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def payment_webhook(request):
    """Handle payment gateway webhooks"""
    try:
        # This would handle webhooks from payment gateways
        # Implementation depends on the specific gateway
        
        # For MirPay, extract transaction details
        transaction_id = request.data.get('transaction_id')
        status_code = request.data.get('status')
        
        if transaction_id and status_code:
            try:
                transaction = Transaction.objects.get(
                    external_transaction_id=transaction_id
                )
                
                if status_code == 'success':
                    transaction.status = 'completed'
                    transaction.completed_at = timezone.now()
                    
                    # Complete purchase if exists
                    if transaction.purchase:
                        transaction.purchase.status = 'completed'
                        transaction.purchase.completed_at = timezone.now()
                        transaction.purchase.save()
                
                elif status_code == 'failed':
                    transaction.status = 'failed'
                    transaction.failure_reason = request.data.get('error_message', 'Payment failed')
                
                transaction.gateway_response = request.data
                transaction.save()
                
                logger.info("Webhook processed", transaction_id=transaction_id, status=status_code)
                
            except Transaction.DoesNotExist:
                logger.warning("Webhook for unknown transaction", transaction_id=transaction_id)
        
        return Response({'status': 'ok'})
        
    except Exception as e:
        logger.error("Webhook processing error", error=str(e))
        return Response(
            {'error': 'Webhook processing error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    """Get user's transactions"""
    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('payment_method', 'purchase__project').order_by('-created_at')
    
    data = []
    for transaction in transactions:
        data.append({
            'id': transaction.id,
            'type': transaction.transaction_type,
            'amount': float(transaction.amount),
            'commission': float(transaction.commission_amount),
            'status': transaction.status,
            'payment_method': transaction.payment_method.name if transaction.payment_method else None,
            'description': transaction.description,
            'created_at': transaction.created_at,
            'completed_at': transaction.completed_at,
            'project': {
                'title': transaction.purchase.project.title,
                'id': transaction.purchase.project.id
            } if transaction.purchase else None
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, transaction_id):
    """Get transaction details"""
    try:
        transaction = Transaction.objects.select_related(
            'payment_method', 'purchase__project'
        ).get(id=transaction_id, user=request.user)
        
        data = {
            'id': transaction.id,
            'type': transaction.transaction_type,
            'amount': float(transaction.amount),
            'commission': float(transaction.commission_amount),
            'net_amount': float(transaction.net_amount),
            'status': transaction.status,
            'payment_method': {
                'name': transaction.payment_method.name,
                'type': transaction.payment_method.method_type
            } if transaction.payment_method else None,
            'description': transaction.description,
            'failure_reason': transaction.failure_reason,
            'created_at': transaction.created_at,
            'completed_at': transaction.completed_at,
            'purchase': {
                'id': transaction.purchase.id,
                'project': {
                    'id': transaction.purchase.project.id,
                    'title': transaction.purchase.project.title,
                    'image': transaction.purchase.project.image.url if transaction.purchase.project.image else None
                }
            } if transaction.purchase else None
        }
        
        return Response(data)
        
    except Transaction.DoesNotExist:
        return Response(
            {'error': 'Transaction not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='user', rate='3/d', method='POST')
def request_withdrawal(request):
    """Request withdrawal of earnings"""
    try:
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method')
        payment_details = request.data.get('payment_details', {})
        
        if not amount or not payment_method:
            return Response(
                {'error': 'Amount and payment method are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        amount = float(amount)
        
        # Check minimum withdrawal amount
        if amount < 10000:  # 10,000 UZS minimum
            return Response(
                {'error': 'Minimum withdrawal amount is 10,000 UZS'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user balance
        if request.user.balance < amount:
            return Response(
                {'error': 'Insufficient balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate commission (2% for withdrawals)
        commission = amount * 0.02
        net_amount = amount - commission
        
        # Create withdrawal request
        withdrawal = WithdrawalRequest.objects.create(
            user=request.user,
            amount=amount,
            commission_amount=commission,
            net_amount=net_amount,
            payment_method=payment_method,
            payment_details=payment_details
        )
        
        logger.info("Withdrawal requested", user_id=request.user.id, amount=amount)
        
        return Response({
            'success': True,
            'withdrawal_id': withdrawal.id,
            'message': 'Withdrawal request submitted for review'
        })
        
    except Exception as e:
        logger.error("Withdrawal request error", error=str(e))
        return Response(
            {'error': 'Withdrawal request error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def withdrawal_list(request):
    """Get user's withdrawal requests"""
    withdrawals = WithdrawalRequest.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    data = []
    for withdrawal in withdrawals:
        data.append({
            'id': withdrawal.id,
            'amount': float(withdrawal.amount),
            'commission': float(withdrawal.commission_amount),
            'net_amount': float(withdrawal.net_amount),
            'payment_method': withdrawal.payment_method,
            'status': withdrawal.status,
            'created_at': withdrawal.created_at,
            'processed_at': withdrawal.processed_at,
            'completed_at': withdrawal.completed_at,
            'rejection_reason': withdrawal.rejection_reason
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    """Get user's account balance"""
    return Response({
        'balance': float(request.user.balance),
        'currency': 'UZS'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def balance_history(request):
    """Get user's balance transaction history"""
    transactions = BalanceTransaction.objects.filter(
        user=request.user
    ).select_related('related_transaction').order_by('-created_at')[:50]
    
    data = []
    for transaction in transactions:
        data.append({
            'id': transaction.id,
            'type': transaction.transaction_type,
            'amount': float(transaction.amount),
            'balance_before': float(transaction.balance_before),
            'balance_after': float(transaction.balance_after),
            'description': transaction.description,
            'created_at': transaction.created_at,
            'related_transaction_id': transaction.related_transaction.id if transaction.related_transaction else None
        })
    
    return Response(data)
