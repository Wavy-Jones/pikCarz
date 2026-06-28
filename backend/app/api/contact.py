"""
Public "Get In Touch" contact form endpoint.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.config import settings
from app.services.email import send_email

router = APIRouter(prefix="/api/contact", tags=["Contact"])

SUPPORT_EMAIL = "support@pikcarz.co.za"


class ContactMessage(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    user_type: str | None = None
    subject: str
    message: str


@router.post("")
@router.post("/")
def submit_contact_form(payload: ContactMessage):
    """
    Sends the 'Get In Touch' form submission to support@pikcarz.co.za,
    and a short confirmation back to the person who submitted it.
    """
    body = (
        f"New contact form submission from pikCarz.co.za\n\n"
        f"Name: {payload.first_name} {payload.last_name}\n"
        f"Email: {payload.email}\n"
        f"Phone: {payload.phone or 'Not provided'}\n"
        f"I am a: {payload.user_type or 'Not specified'}\n"
        f"Subject: {payload.subject}\n\n"
        f"Message:\n{payload.message}\n"
    )

    sent = send_email(
        to=SUPPORT_EMAIL,
        subject=f"[pikCarz Contact] {payload.subject}",
        body=body,
    )

    if not sent:
        # SendGrid not configured or failed to send \u2014 don't silently lose the
        # enquiry: surface a clear error so the admin notices in the logs/UI
        # instead of the user thinking it worked when nothing was sent.
        raise HTTPException(
            status_code=502,
            detail="We couldn't send your message right now. Please email us "
                   f"directly at {SUPPORT_EMAIL} or WhatsApp us instead.",
        )

    # Best-effort confirmation to the sender \u2014 don't fail the request if this part fails
    send_email(
        to=payload.email,
        subject="We've received your message \u2014 pikCarz",
        body=(
            f"Hi {payload.first_name},\n\n"
            f"Thanks for reaching out to pikCarz! We've received your message "
            f"about \"{payload.subject}\" and will get back to you within 24 hours "
            f"on business days.\n\n"
            f"The pikCarz Team"
        ),
    )

    return {"message": "Thanks! Your message has been sent \u2014 we'll be in touch shortly."}
