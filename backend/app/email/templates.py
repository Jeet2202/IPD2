"""
Reusable responsive HTML & plain-text email templates for KaamSetu.

Architecture:
    - Provides standardized branding, styling, responsive HTML layout, and plain-text fallback.
    - Encapsulated within EmailTemplateService static methods.
    - Eliminates template code duplication across email flows.
"""

from typing import NamedTuple


class RenderedEmail(NamedTuple):
    """Container for rendered HTML and plain-text email content."""
    html_content: str
    text_content: str
    subject: str


class EmailTemplateService:
    """
    HTML & Text template renderer for authentication and operational emails.
    """

    @staticmethod
    def _render_layout(
        title: str,
        preheader: str,
        content_body: str,
    ) -> str:
        """
        Base responsive HTML layout wrapper with KaamSetu design system branding.
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #f4f6f8;
            margin: 0;
            padding: 0;
            color: #1e293b;
        }}
        .container {{
            max-width: 580px;
            margin: 30px auto;
            background: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        .header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: #ffffff;
            padding: 24px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .header p {{
            margin: 4px 0 0 0;
            font-size: 13px;
            opacity: 0.9;
        }}
        .body {{
            padding: 32px 24px;
        }}
        .otp-box {{
            background-color: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 24px 0;
        }}
        .otp-code {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 36px;
            font-weight: 800;
            letter-spacing: 8px;
            color: #1e3a8a;
            margin: 0;
        }}
        .expiry-notice {{
            font-size: 13px;
            color: #64748b;
            margin-top: 8px;
        }}
        .warning-box {{
            background-color: #fffbe6;
            border-left: 4px solid #f59e0b;
            padding: 12px 16px;
            font-size: 13px;
            color: #78350f;
            margin-top: 24px;
            border-radius: 4px;
        }}
        .footer {{
            background-color: #f8fafc;
            border-top: 1px solid #e2e8f0;
            padding: 20px 24px;
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>KaamSetu</h1>
            <p>AI Powered Home Services Marketplace</p>
        </div>
        <div class="body">
            {content_body}
        </div>
        <div class="footer">
            <p>© 2026 KaamSetu Technologies Ltd. All rights reserved.</p>
            <p>This is an automated system email. Please do not reply directly.</p>
        </div>
    </div>
</body>
</html>"""

    @classmethod
    def render_registration_otp(
        cls,
        otp_code: str,
        expiry_minutes: int = 5,
        user_name: str | None = None,
    ) -> RenderedEmail:
        """Render HTML & text for user registration OTP verification."""
        subject = f"Your KaamSetu Registration Code: {otp_code}"
        greeting = f"Hello {user_name}," if user_name else "Hello,"

        body = f"""
            <h2>Welcome to KaamSetu!</h2>
            <p>{greeting}</p>
            <p>Thank you for signing up with KaamSetu. Please use the verification code below to complete your registration:</p>
            <div class="otp-box">
                <div class="otp-code">{otp_code}</div>
                <div class="expiry-notice">Valid for the next {expiry_minutes} minutes</div>
            </div>
            <div class="warning-box">
                <strong>Security Reminder:</strong> Never share this OTP with anyone. KaamSetu staff will never ask for your verification code.
            </div>
        """
        html = cls._render_layout("KaamSetu Registration Verification", "Your OTP Code", body)
        text = f"{greeting}\n\nYour KaamSetu registration verification code is: {otp_code}\n\nValid for {expiry_minutes} minutes.\nDo not share this OTP with anyone."
        return RenderedEmail(html_content=html, text_content=text, subject=subject)

    @classmethod
    def render_login_otp(
        cls,
        otp_code: str,
        expiry_minutes: int = 5,
        user_name: str | None = None,
    ) -> RenderedEmail:
        """Render HTML & text for multi-factor login OTP verification."""
        subject = f"Your KaamSetu Login Security Code: {otp_code}"
        greeting = f"Hello {user_name}," if user_name else "Hello,"

        body = f"""
            <h2>Account Login Verification</h2>
            <p>{greeting}</p>
            <p>A login attempt was initiated for your KaamSetu account. Please enter the One-Time Password (OTP) below to authenticate:</p>
            <div class="otp-box">
                <div class="otp-code">{otp_code}</div>
                <div class="expiry-notice">Valid for the next {expiry_minutes} minutes</div>
            </div>
            <div class="warning-box">
                <strong>Security Alert:</strong> If you did not initiate this login request, please change your password immediately and contact support.
            </div>
        """
        html = cls._render_layout("KaamSetu Login Verification", "Your Login OTP Code", body)
        text = f"{greeting}\n\nYour KaamSetu login OTP code is: {otp_code}\n\nValid for {expiry_minutes} minutes.\nIf you did not request this, please secure your account."
        return RenderedEmail(html_content=html, text_content=text, subject=subject)

    @classmethod
    def render_password_reset_otp(
        cls,
        otp_code: str,
        expiry_minutes: int = 5,
        user_name: str | None = None,
    ) -> RenderedEmail:
        """Render HTML & text for password reset OTP verification."""
        subject = f"Your KaamSetu Password Reset Code: {otp_code}"
        greeting = f"Hello {user_name}," if user_name else "Hello,"

        body = f"""
            <h2>Password Reset Request</h2>
            <p>{greeting}</p>
            <p>We received a request to reset the password for your KaamSetu account. Use the code below to authorize the password reset:</p>
            <div class="otp-box">
                <div class="otp-code">{otp_code}</div>
                <div class="expiry-notice">Valid for the next {expiry_minutes} minutes</div>
            </div>
            <div class="warning-box">
                <strong>Important:</strong> If you did not request a password reset, you can safely ignore this email. Your current password remains active.
            </div>
        """
        html = cls._render_layout("KaamSetu Password Reset", "Your Password Reset OTP", body)
        text = f"{greeting}\n\nYour KaamSetu password reset verification code is: {otp_code}\n\nValid for {expiry_minutes} minutes.\nIf you did not request a reset, ignore this message."
        return RenderedEmail(html_content=html, text_content=text, subject=subject)

    @classmethod
    def render_email_verification_otp(
        cls,
        otp_code: str,
        expiry_minutes: int = 5,
        user_name: str | None = None,
    ) -> RenderedEmail:
        """Render HTML & text for email verification OTP."""
        subject = f"Verify Your Email Address — KaamSetu: {otp_code}"
        greeting = f"Hello {user_name}," if user_name else "Hello,"

        body = f"""
            <h2>Verify Your Email Address</h2>
            <p>{greeting}</p>
            <p>Please enter the OTP verification code below to confirm your email address on KaamSetu:</p>
            <div class="otp-box">
                <div class="otp-code">{otp_code}</div>
                <div class="expiry-notice">Valid for the next {expiry_minutes} minutes</div>
            </div>
            <div class="warning-box">
                <strong>Security Reminder:</strong> Do not share this verification code with anyone.
            </div>
        """
        html = cls._render_layout("Verify Email Address", "Your Email Verification OTP", body)
        text = f"{greeting}\n\nYour KaamSetu email verification OTP is: {otp_code}\n\nValid for {expiry_minutes} minutes."
        return RenderedEmail(html_content=html, text_content=text, subject=subject)
