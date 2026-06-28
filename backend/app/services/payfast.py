"""
PayFast payment gateway integration
"""
import hashlib
from urllib.parse import urlencode, quote_plus
from app.config import settings


def generate_signature(data: dict, passphrase: str = None) -> str:
    if passphrase is None:
        passphrase = settings.PAYFAST_PASSPHRASE

    param_parts = []
    for key, value in data.items():
        if key != 'signature' and str(value).strip() != '':
            param_parts.append(f'{key}={quote_plus(str(value).strip())}')

    param_string = '&'.join(param_parts)

    if passphrase and passphrase.strip():
        param_string += f'&passphrase={quote_plus(passphrase.strip())}'

    return hashlib.md5(param_string.encode()).hexdigest()


def generate_payment_data(
    payment_id: int,
    amount: float,
    item_name: str,
    user_email: str,
    user_name: str,
    is_recurring: bool = False,
    billing_date: str = None,
    recurring_amount: float = None,
    frequency: int = 3,
    cycles: int = 0,
) -> dict:
    """
    Generate PayFast payment data for POST form submission.

    For recurring billing (is_recurring=True), `amount` is what's charged
    TODAY (use 0.00 to set up a card with no charge, e.g. during a free
    trial) and `recurring_amount` is what gets auto-charged on `billing_date`
    and every cycle after that. frequency: 1=Daily 2=Weekly 3=Monthly
    4=Quarterly 5=Biannually 6=Annual. cycles=0 means indefinite.
    A merchant passphrase MUST be set on the PayFast account for recurring
    billing to work — see PAYFAST_PASSPHRASE in settings.
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
        'm_payment_id': str(payment_id),
        'amount':       f'{amount:.2f}',
        'item_name':    item_name,
    }
    if len(name_parts) > 1:
        items = list(payment_data.items())
        idx = next(i for i, (k, _) in enumerate(items) if k == 'name_first')
        items.insert(idx + 1, ('name_last', ' '.join(name_parts[1:])))
        payment_data = dict(items)

    if is_recurring:
        payment_data['subscription_type'] = '1'
        if billing_date:
            payment_data['billing_date'] = billing_date
        payment_data['recurring_amount'] = f'{(recurring_amount if recurring_amount is not None else amount):.2f}'
        payment_data['frequency'] = str(frequency)
        payment_data['cycles'] = str(cycles)

    payment_data['signature'] = generate_signature(payment_data)
    return {'url': payfast_url, 'params': payment_data}


def generate_payment_url(payment_id: int, amount: float, item_name: str, user_email: str, user_name: str) -> str:
    """Legacy GET URL method — kept for compatibility."""
    data = generate_payment_data(payment_id, amount, item_name, user_email, user_name)
    return data['url'] + '?' + urlencode(data['params'])


def verify_payfast_signature(data: dict) -> bool:
    """Verify PayFast ITN signature."""
    received_signature = data.get('signature', '')
    if not received_signature:
        return False
    data_without_sig = {k: v for k, v in data.items() if k != 'signature'}
    expected_signature = generate_signature(data_without_sig)
    return received_signature == expected_signature
