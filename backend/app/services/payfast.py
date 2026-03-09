"""
PayFast payment integration service
"""
import hashlib
from urllib.parse import urlencode
from app.config import settings, PAYFAST_URL

def generate_payment_signature(data: dict) -> str:
    """Generate PayFast payment signature"""
    
    # Create parameter string
    param_string = ""
    for key in sorted(data.keys()):
        param_string += f"{key}={data[key]}&"
    
    # Remove last ampersand
    param_string = param_string[:-1]
    
    # Add passphrase if configured
    if settings.PAYFAST_PASSPHRASE:
        param_string += f"&passphrase={settings.PAYFAST_PASSPHRASE}"
    
    # Generate signature
    signature = hashlib.md5(param_string.encode()).hexdigest()
    
    return signature

def generate_payment_url(
    amount: float,
    item_name: str,
    item_description: str,
    email_address: str,
    name_first: str,
    name_last: str,
    m_payment_id: str,
    user_id: int
) -> str:
    """
    Generate PayFast payment URL
    Returns the complete payment URL with signature
    """
    
    # Build payment data
    data = {
        "merchant_id": settings.PAYFAST_MERCHANT_ID,
        "merchant_key": settings.PAYFAST_MERCHANT_KEY,
        "return_url": f"{settings.FRONTEND_URL}/payment/success",
        "cancel_url": f"{settings.FRONTEND_URL}/payment/cancelled",
        "notify_url": f"https://pikcarz.vercel.app/api/subscriptions/webhook/payfast",
        "name_first": name_first,
        "name_last": name_last,
        "email_address": email_address,
        "m_payment_id": m_payment_id,
        "amount": f"{amount:.2f}",
        "item_name": item_name,
        "item_description": item_description,
        "custom_int1": user_id,
        "email_confirmation": "1",
        "confirmation_address": email_address
    }
    
    # Generate signature
    data["signature"] = generate_payment_signature(data)
    
    # Build URL
    payment_url = f"{PAYFAST_URL}?{urlencode(data)}"
    
    return payment_url

def verify_payfast_signature(data: dict) -> bool:
    """
    Verify PayFast ITN signature
    Returns True if signature is valid
    """
    
    # Extract signature from data
    signature = data.get("signature")
    if not signature:
        return False
    
    # Remove signature from data for verification
    verification_data = {k: v for k, v in data.items() if k != "signature"}
    
    # Generate expected signature
    expected_signature = generate_payment_signature(verification_data)
    
    return signature == expected_signature
