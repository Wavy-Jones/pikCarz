"""
PayFast payment gateway integration
"""
import hashlib
from urllib.parse import urlencode, quote_plus
from app.config import settings

def generate_payment_url(payment_id: int, amount: float, item_name: str, user_email: str, user_name: str) -> str:
    """
    Generate PayFast payment URL
    
    PayFast requires specific parameters to be sent
    Returns the payment URL that user should be redirected to
    """
    
    # PayFast merchant details (from environment variables)
    merchant_id = settings.PAYFAST_MERCHANT_ID
    merchant_key = settings.PAYFAST_MERCHANT_KEY
    
    # PayFast URLs
    if settings.PAYFAST_MODE == "sandbox":
        payfast_url = "https://sandbox.payfast.co.za/eng/process"
    else:
        payfast_url = "https://www.payfast.co.za/eng/process"
    
    # Build payment data - exclude empty values as PayFast signature must not include them
    name_parts = user_name.strip().split()
    payment_data = {
        'merchant_id': str(merchant_id),
        'merchant_key': str(merchant_key),
        'return_url': f'{settings.FRONTEND_URL}/payment-success',
        'cancel_url': f'{settings.FRONTEND_URL}/payment-cancelled',
        'notify_url': f'{settings.BACKEND_URL}/api/subscriptions/webhook/payfast',
        'name_first': name_parts[0],
        'email_address': user_email,
        'amount': f'{amount:.2f}',
        'item_name': item_name,
        'm_payment_id': str(payment_id),
        'email_confirmation': '1',
        'confirmation_address': user_email,
    }
    # Only add name_last if it exists
    if len(name_parts) > 1:
        payment_data['name_last'] = name_parts[-1]
    
    # Generate signature
    signature = generate_signature(payment_data)
    payment_data['signature'] = signature
    
    # Build payment URL
    query_string = urlencode(payment_data)
    payment_url = f'{payfast_url}?{query_string}'
    
    return payment_url

def generate_signature(data: dict, passphrase: str = None) -> str:
    """
    Generate PayFast signature.
    Uses quote_plus encoding (PHP urlencode equivalent) in insertion order.
    """
    if passphrase is None:
        passphrase = settings.PAYFAST_PASSPHRASE

    param_parts = []
    for key, value in data.items():
        if key != 'signature':
            param_parts.append(f'{key}={quote_plus(str(value))}')

    param_string = '&'.join(param_parts)

    if passphrase:
        param_string += f'&passphrase={quote_plus(passphrase)}'

    return hashlib.md5(param_string.encode()).hexdigest()

def verify_payfast_signature(data: dict) -> bool:
    """
    Verify PayFast ITN (Instant Transaction Notification) signature
    
    This ensures the webhook data came from PayFast and hasn't been tampered with
    """
    # Get signature from data
    received_signature = data.get('signature', '')
    
    if not received_signature:
        return False
    
    # Create a copy without the signature
    data_without_sig = {k: v for k, v in data.items() if k != 'signature'}
    
    # Generate expected signature
    expected_signature = generate_signature(data_without_sig)
    
    # Compare signatures
    return received_signature == expected_signature
