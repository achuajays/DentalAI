from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/email",
    tags=["email-sender"],
    responses={404: {"description": "Not found"}}
)

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # e.g., your email address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # e.g., app-specific password for Gmail

# Predefined HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visit Hospital Notification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
        .content {
            padding: 20px;
            line-height: 1.6;
        }
        .hospital-details {
            background-color: #f9f9f9;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #4CAF50;
        }
        .footer {
            text-align: center;
            font-size: 12px;
            color: #777;
            padding: 10px;
        }
        a {
            color: #4CAF50;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Dental Care Hospital</h2>
        </div>
        <div class="content">
            <h3>Important Notification</h3>
            <p>Dear Patient,</p>
            <p>We kindly request your presence at our hospital for a scheduled dental check-up or follow-up appointment. Your oral health is our priority, and we are here to assist you with any concerns.</p>
            <div class="hospital-details">
                <h4>Hospital Details</h4>
                <p><strong>Name:</strong> Dental Care Hospital</p>
                <p><strong>Address:</strong> 123 Health Street, Suite 100, Wellness City, WC 12345</p>
                <p><strong>Contact:</strong> (555) 123-4567 | <a href="mailto:info@dentalcarehospital.com">info@dentalcarehospital.com</a></p>
                <p><strong>Website:</strong> <a href="https://www.dentalcarehospital.com">www.dentalcarehospital.com</a></p>
            </div>
            <p>Please visit us at your earliest convenience. If you need to reschedule, feel free to contact us using the details above.</p>
            <p>Thank you for choosing Dental Care Hospital!</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Dental Care Hospital. All rights reserved.</p>
            <p><a href="https://www.dentalcarehospital.com/unsubscribe">Unsubscribe</a> from these notifications.</p>
        </div>
    </div>
</body>
</html>
"""

@router.post("/send")
async def send_email(recipient_email: str):
    """
    Send a predefined HTML email notifying the recipient to visit the hospital
    Example: {"recipient_email": "recipient@example.com"}
    """
    try:
        # Validate input
        if not recipient_email:
            raise HTTPException(
                status_code=400,
                detail="Recipient email is required"
            )
        if not recipient_email.endswith(("@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com")):
            raise HTTPException(
                status_code=400,
                detail="Invalid recipient email domain"
            )

        # Create the email message with HTML content
        msg = MIMEText(HTML_TEMPLATE, "html")
        msg["Subject"] = "Urgent: Please Visit Dental Care Hospital"
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient_email

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        # Log the success
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "status": "success",
            "recipient_email": recipient_email,
            "subject": "Urgent: Please Visit Dental Care Hospital",
            "sent_at": timestamp,
            "message": "Email sent successfully"
        }

        return JSONResponse(content=result)

    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed. Check SMTP username and password."
        )
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"SMTP error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Email sending service is running"}