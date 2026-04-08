from flask_mail import Mail, Message
from flask import current_app
from logger import logger
from datetime import datetime

mail = Mail()

def send_email(subject, recipients, text_body=None, html_body=None):
    """
    Send email

    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        text_body (str): Plain text body
        html_body (str): HTML body
    """
    try:
        if not recipients or not isinstance(recipients, list):
            logger.warning("Invalid recipients list for email")
            return False

        msg = Message(subject, recipients=recipients)
        msg.body = text_body
        msg.html = html_body

        mail.send(msg)
        logger.info(f"Email sent to {recipients}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


def send_scan_notification(user_email, username, platforms_found):
    """
    Send scan result notification to user

    Args:
        user_email (str): User's email
        username (str): Scanned username
        platforms_found (list): List of platforms where username was found
    """
    subject = f"Scan Results: @{username}"

    platform_list = '\n'.join([f"• {p}" for p in platforms_found])

    text_body = f"""
Digital Footprint Scan Results

Username: {username}
Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Platforms Found:
{platform_list}

Found on {len(platforms_found)} platform(s).

Log in to your account for more details.
"""

    html_body = f"""
    <html>
        <body>
            <h2>Digital Footprint Scan Results</h2>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Scan Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <h3>Platforms Found:</h3>
            <ul>
    """
    for platform in platforms_found:
        html_body += f"<li>{platform}</li>"

    html_body += f"""
            </ul>
            <p>Found on <strong>{len(platforms_found)}</strong> platform(s).</p>
            <p><a href="https://yourapp.com">Log in to your account</a> for more details.</p>
        </body>
    </html>
    """

    return send_email(subject, [user_email], text_body, html_body)


def send_weekly_digest(user_email, username, scan_count, top_platforms):
    """
    Send weekly digest of scan activity

    Args:
        user_email (str): User's email
        username (str): Username for greeting
        scan_count (int): Number of scans performed
        top_platforms (list): Most frequently found platforms
    """
    subject = "Your Weekly Digital Footprint Report"

    platform_list = '\n'.join([f"• {p[0]}: {p[1]} scan(s)" for p in top_platforms])

    text_body = f"""
Your Weekly Digital Footprint Report

Hello {username},

This week, you performed {scan_count} scans.

Most Frequent Platforms:
{platform_list}

Keep monitoring your digital presence!

Visit https://yourapp.com to view your complete history.
"""

    html_body = f"""
    <html>
        <body>
            <h2>Your Weekly Digital Footprint Report</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>This week, you performed <strong>{scan_count}</strong> scans.</p>
            <h3>Most Frequent Platforms:</h3>
            <ul>
    """
    for platform, count in top_platforms:
        html_body += f"<li>{platform}: {count} scan(s)</li>"

    html_body += f"""
            </ul>
            <p>Keep monitoring your digital presence!</p>
            <p><a href="https://yourapp.com">View your complete history</a></p>
        </body>
    </html>
    """

    return send_email(subject, [user_email], text_body, html_body)


def send_security_alert(user_email, alert_message):
    """
    Send security alert to user

    Args:
        user_email (str): User's email
        alert_message (str): Alert message
    """
    subject = "Security Alert - Digital Footprint Tracker"

    text_body = f"""
Security Alert

{alert_message}

If you didn't perform this action, please change your password immediately.

Visit https://yourapp.com for more information.
"""

    html_body = f"""
    <html>
        <body>
            <h2>Security Alert</h2>
            <p>{alert_message}</p>
            <p>If you didn't perform this action, please <a href="https://yourapp.com/change-password">change your password</a> immediately.</p>
        </body>
    </html>
    """

    return send_email(subject, [user_email], text_body, html_body)
