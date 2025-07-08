import requests
import logging
from django.conf import settings
from decimal import Decimal
import structlog

logger = structlog.get_logger(__name__)

class MirPayService:
    def __init__(self):
        self.kassa_id = settings.MIRPAY_KASSA_ID
        self.api_key = settings.MIRPAY_API_KEY
        self.base_url = settings.MIRPAY_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_balance(self):
        try:
            response = requests.get(
                f'{self.base_url}/balans',
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            logger.info("MirPay balance retrieved", balance=data.get('balance'))
            return data
        except requests.exceptions.RequestException as e:
            logger.error("Failed to get MirPay balance", error=str(e))
            raise
    
    def create_payment(self, amount, order_id, description):
        try:
            if settings.PAYMENT_MODE == 'development':
                return self._simulate_payment(amount, order_id, description)
            
            payload = {
                'kassa_id': self.kassa_id,
                'summa': str(amount),
                'order_id': order_id,
                'description': description,
                'success_url': settings.MIRPAY_SUCCESS_URL,
                'failure_url': settings.MIRPAY_FAILURE_URL
            }
            
            response = requests.post(
                f'{self.base_url}/payment/create',
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info("MirPay payment created", 
                       order_id=order_id, amount=amount, payid=data.get('payid'))
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to create MirPay payment", 
                        order_id=order_id, error=str(e))
            raise
    
    def _simulate_payment(self, amount, order_id, description):
        import uuid
        mock_payid = str(uuid.uuid4())[:8]
        
        logger.info("Simulated payment created (development mode)", 
                   order_id=order_id, amount=amount, payid=mock_payid)
        
        return {
            'payid': mock_payid,
            'payment_url': f'/payment/simulate/{mock_payid}',
            'status': 'pending'
        }
    
    def verify_payment(self, payid):
        try:
            if settings.PAYMENT_MODE == 'development':
                return {'status': 'success', 'verified': True}
            
            response = requests.get(
                f'{self.base_url}/payment/status/{payid}',
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            logger.info("MirPay payment verified", payid=payid, status=data.get('status'))
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error("Failed to verify MirPay payment", payid=payid, error=str(e))
            raise
