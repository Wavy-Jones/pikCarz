"""
PayFast payment gateway integration
"""
import hashlib
from urllib.parse import urlencode, quote_plus, quote
from app.config import settings

def generate_payment_data(payment_id: int, amount: float, item_name: str, user_email: str, user_name: str) -> dict:
    """
    Generate PayFast payment data for POST form submission.
    Returns the PayFast URL and all signed parameters.
    """
    merchant_id  = settings.PAYFAST_MERCHANT_ID
    merchant_key = settings.PAYFAST_MERCHANT_KEY

    if settings.PAYFAST_MODE == "sandbox":
        payfast_url = "https://sandbox.payfast.co.za/eng/process"
    else:
        payfast_url = "https://www.payfast.co.za/eng/process"

    name_parts = user_name.strip().split()
    payment_data = {
        'merchant_id':  str(merchant_id),
        'merchant_key': str(merchant_key),
        'return_url':   f'{settings.FRONTEND_URL}/payment-success',
        'cancel_url':   f'{settings.FRONTEND_URL}/payment-cancelled',
        'notify_url':   f'{settings.BACKEND_URL}/api/subscriptions/webhook/payfast',
        'name_first':   name_parts[0],
        'email_address': user_email,
        'amount':       f'{amount:.2f}',
        'item_name':    item_name,
        'm_payment_id': str(payment_id),
    }
    if len(name_parts) > 1:
        # insert name_last right after name_first
        items = list(payment_data.items())
        idx = next(i for i, (k, _) in enumerate(items) if k == 'name_first')
        items.insert(idx + 1, ('name_last', ' '.join(name_parts[1:])))
        payment_data = dict(items)

    payment_data['signature'] = generate_signature(payment_data)

    return {'url': payfast_url, 'params': payment_data}


def generate_payment_url(payment_id: int, amount: float, item_name: str, user_email: str, user_name: str) -> str:
    """Legacy GET URL method — kept for compatibility."""
    data = generate_payment_data(payment_id, amount, item_name, user_email, user_name)
    return data['url'] + '?' + urlencode(data['params'])

def generate_signature(data: dict, passphrase: str = None) -> str:
    if passphrase is None:
        passphrase = settings.PAYFAST_PASSPHRASE

    param_parts = []
    for key, value in data.items():  # insertion order — must match form submission order
        if key != 'signature' and str(value).strip() != '':
            param_parts.append(f'{key}={quote_plus(str(value).strip())}')

    base_string = '&'.join(param_parts)
    string_with    = base_string + f'&passphrase={quote_plus(passphrase.strip())}' if (passphrase and passphrase.strip()) else base_string
    string_without = base_string

    sig_with    = hashlib.md5(string_with.encode()).hexdigest()
    sig_without = hashlib.md5(string_without.encode()).hexdigest()

    print(f"PAYFAST_DEBUG base: {base_string}")
    print(f"PAYFAST_DEBUG sig_WITH passphrase: {sig_with}")
    print(f"PAYFAST_DEBUG sig_WITHOUT passphrase: {sig_without}")

    # Currently using WITH passphrase — change to sig_without to test
    return sig_with if (passphrase and passphrase.strip()) else sig_without

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
