"""
WhatsApp notification service using the Meta WhatsApp Cloud API.

Setup required (one-time):
  1. Create a Meta developer app at https://developers.facebook.com
  2. Add the "WhatsApp" product, get a permanent access token + Phone Number ID
  3. Set these env vars in Vercel:
       WHATSAPP_API_TOKEN      - permanent access token
       WHATSAPP_PHONE_NUMBER_ID - the sending number's ID (not the number itself)
  4. Create an approved message template (Meta requires pre-approved templates
     for any business-initiated message, e.g. "subscription_reminder") OR use
     a free-form text message if the user has messaged your business number
     within the last 24 hours (session window).

This module degrades gracefully: if the env vars aren't set, it logs to
console instead of failing, exactly like the email service's dev fallback.
"""
import os
import requests

GRAPH_API_VERSION = "v21.0"


def _clean_number(phone: str) -> str:
    """Normalise a South African number to international format, no '+', no spaces."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if digits.startswith("0"):
        digits = "27" + digits[1:]
    elif not digits.startswith("27"):
        digits = "27" + digits
    return digits


def send_whatsapp_message(to_phone: str, message: str) -> bool:
    """
    Send a free-form WhatsApp text message via the Cloud API.

    Args:
        to_phone: User's phone number, any common SA format (e.g. "083 943 8885")
        message: Plain text message body

    Returns:
        True if the API accepted the message, False otherwise (including
        when WhatsApp isn't configured yet — check logs for the printed
        message so nothing is silently lost).
    """
    token = os.environ.get("WHATSAPP_API_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

    if not to_phone:
        print("⚠️ WhatsApp send skipped — user has no phone number on file.")
        return False

    to = _clean_number(to_phone)

    if not token or not phone_number_id:
        print(f"\n{'='*60}")
        print("⚠️  WHATSAPP NOT CONFIGURED - MESSAGE NOT SENT")
        print(f"{'='*60}")
        print(f"To: {to}")
        print(f"Message:\n{message}")
        print(f"{'='*60}\n")
        return False

    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message},
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code >= 400:
            print(f"❌ WhatsApp send failed ({resp.status_code}): {resp.text}")
            return False
        print(f"✅ WhatsApp message sent to {to}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp send error for {to}: {str(e)}")
        return False


def send_whatsapp_template(to_phone: str, template_name: str, language_code: str = "en", components: list | None = None) -> bool:
    """
    Send a pre-approved WhatsApp template message — required for the FIRST
    business-initiated contact (i.e. outside a 24h customer-service window,
    which is the normal case for renewal reminders). Create the template
    "subscription_reminder" in Meta Business Manager before using this.
    """
    token = os.environ.get("WHATSAPP_API_TOKEN")
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

    if not to_phone:
        return False
    to = _clean_number(to_phone)

    if not token or not phone_number_id:
        print(f"⚠️ WHATSAPP NOT CONFIGURED - template '{template_name}' not sent to {to}")
        return False

    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{phone_number_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                **({"components": components} if components else {}),
            },
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code >= 400:
            print(f"❌ WhatsApp template send failed ({resp.status_code}): {resp.text}")
            return False
        print(f"✅ WhatsApp template '{template_name}' sent to {to}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp template send error for {to}: {str(e)}")
        return False
