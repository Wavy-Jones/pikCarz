"""
Email service using SendGrid
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional

def send_password_reset_email(to_email: str, reset_link: str, user_name: str) -> bool:
    """
    Send password reset email via SendGrid
    
    Args:
        to_email: Recipient email address
        reset_link: Password reset link with token
        user_name: User's full name
        
    Returns:
        True if email sent successfully, False otherwise
    """
    
    # Get SendGrid API key from environment
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    from_email = os.environ.get('EMAIL_FROM', 'noreply@pikcarz.co.za')
    
    # If no API key, fall back to console logging
    if not sendgrid_api_key:
        print(f"\n{'='*60}")
        print(f"⚠️  SENDGRID NOT CONFIGURED - EMAIL NOT SENT")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"Subject: Reset Your Password - pikCarz")
        print(f"Reset Link: {reset_link}")
        print(f"{'='*60}\n")
        return False
    
    try:
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #1F2128; color: #FFFFFF;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #1F2128;">
                <tr>
                    <td align="center" style="padding: 40px 20px;">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #2A2D35; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                            <!-- Header -->
                            <tr>
                                <td align="center" style="padding: 40px 40px 20px 40px;">
                                    <h1 style="margin: 0; color: #FFFFFF; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                                        Reset Your Password
                                    </h1>
                                    <p style="margin: 10px 0 0 0; color: #9CA3AF; font-size: 14px;">
                                        POWERED BY CUBEAS
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Body -->
                            <tr>
                                <td style="padding: 20px 40px;">
                                    <p style="margin: 0 0 20px 0; color: #FFFFFF; font-size: 16px; line-height: 1.6;">
                                        Hi {user_name},
                                    </p>
                                    <p style="margin: 0 0 20px 0; color: #9CA3AF; font-size: 15px; line-height: 1.6;">
                                        We received a request to reset your password for your pikCarz account. Click the button below to create a new password:
                                    </p>
                                    
                                    <!-- Button -->
                                    <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                                        <tr>
                                            <td align="center">
                                                <a href="{reset_link}" style="display: inline-block; padding: 16px 32px; background-color: #FF4545; color: #FFFFFF; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 16px;">
                                                    Reset Password
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 20px 0; color: #9CA3AF; font-size: 14px; line-height: 1.6;">
                                        Or copy and paste this link into your browser:
                                    </p>
                                    <p style="margin: 0 0 20px 0; color: #FF4545; font-size: 13px; word-break: break-all;">
                                        {reset_link}
                                    </p>
                                    
                                    <p style="margin: 20px 0 0 0; color: #9CA3AF; font-size: 14px; line-height: 1.6;">
                                        This link will expire in <strong style="color: #FFFFFF;">1 hour</strong> for security reasons.
                                    </p>
                                    
                                    <p style="margin: 20px 0 0 0; color: #9CA3AF; font-size: 14px; line-height: 1.6;">
                                        If you didn't request this password reset, you can safely ignore this email. Your password will not be changed.
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; border-top: 1px solid rgba(255,255,255,0.08);">
                                    <p style="margin: 0; color: #6B7280; font-size: 13px; line-height: 1.6; text-align: center;">
                                        This email was sent by <strong style="color: #9CA3AF;">pikCarz</strong> - South Africa's Fastest Growing Auto Marketplace
                                    </p>
                                    <p style="margin: 10px 0 0 0; color: #6B7280; font-size: 13px; text-align: center;">
                                        <a href="https://pikcarz.co.za" style="color: #FF4545; text-decoration: none;">pikcarz.co.za</a>
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        # Plain text version for email clients that don't support HTML
        text_content = f"""
        Reset Your Password - pikCarz
        
        Hi {user_name},
        
        We received a request to reset your password for your pikCarz account.
        
        Click this link to create a new password:
        {reset_link}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, you can safely ignore this email.
        Your password will not be changed.
        
        ---
        pikCarz - South Africa's Fastest Growing Auto Marketplace
        https://pikcarz.co.za
        """
        
        # Create message
        message = Mail(
            from_email=Email(from_email, "pikCarz"),
            to_emails=To(to_email),
            subject="Reset Your Password - pikCarz",
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        # Send email
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        # Log success
        print(f"\n{'='*60}")
        print(f"✅ PASSWORD RESET EMAIL SENT")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"Status Code: {response.status_code}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ FAILED TO SEND EMAIL")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"To: {to_email}")
        print(f"Fallback: Reset link - {reset_link}")
        print(f"{'='*60}\n")
        return False


def send_welcome_email(to_email: str, user_name: str) -> bool:
    """
    Send welcome email to new users
    
    Args:
        to_email: Recipient email address
        user_name: User's full name
        
    Returns:
        True if email sent successfully, False otherwise
    """
    
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    from_email = os.environ.get('EMAIL_FROM', 'noreply@pikcarz.co.za')
    
    if not sendgrid_api_key:
        return False
    
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #1F2128; color: #FFFFFF;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center" style="padding: 40px 20px;">
                        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #2A2D35; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
                            <tr>
                                <td align="center" style="padding: 40px;">
                                    <h1 style="margin: 0 0 20px 0; color: #FFFFFF; font-size: 32px;">Welcome to pikCarz! 🚗</h1>
                                    <p style="margin: 0; color: #9CA3AF; font-size: 16px; line-height: 1.6;">
                                        Hi {user_name},
                                    </p>
                                    <p style="margin: 20px 0; color: #9CA3AF; font-size: 16px; line-height: 1.6;">
                                        Thank you for joining South Africa's fastest-growing auto marketplace!
                                    </p>
                                    <a href="https://pikcarz.co.za/dashboard.html" style="display: inline-block; margin: 20px 0; padding: 16px 32px; background-color: #FF4545; color: #FFFFFF; text-decoration: none; border-radius: 8px; font-weight: 700;">
                                        Go to Dashboard
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=Email(from_email, "pikCarz"),
            to_emails=To(to_email),
            subject="Welcome to pikCarz! 🚗",
            html_content=Content("text/html", html_content)
        )
        
        sg = SendGridAPIClient(sendgrid_api_key)
        sg.send(message)
        
        return True
        
    except Exception as e:
        print(f"Failed to send welcome email: {str(e)}")
        return False
