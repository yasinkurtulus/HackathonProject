import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os


class EmailService:
    def __init__(self):
        # Prefer environment variables; fall back to previous defaults if missing
        # Note: For Gmail, use an App Password when 2FA is enabled
        self.sender_email = os.getenv("SMTP_USERNAME", "wordmasterai@gmail.com")
        self.password = os.getenv("SMTP_PASSWORD", "ffco qqxl kwyo rfsb")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        # Cast port to int if provided, default 587
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))

    def send_email(self, to_email, subject, body, is_html=False):
        """Send email to specified recipient"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = to_email
            msg["Subject"] = subject

            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            # Connect to Gmail's SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Upgrade to secure connection
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, to_email, msg.as_string())
            server.quit()

            print(f" Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            return False

    def send_welcome_email(self, user_email, user_name):
        """Send welcome email to new users"""
        subject = " Welcome to WordMaster AI!"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">Welcome to WordMaster AI, {user_name}!</h2>

                <p>Thank you for joining our English learning community. You're about to embark on an exciting journey to master English vocabulary!</p>

                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">What you can do with WordMaster AI:</h3>
                    <ul>
                        <li>📚 Learn English words with Turkish translations</li>
                        <li>🎯 Practice with AI-generated example sentences</li>
                        <li>🔊 Listen to correct pronunciation</li>
                        <li>📊 Track your learning progress</li>
                        <li>🏆 Build learning streaks</li>
                    </ul>
                </div>

                <p><strong>Ready to start learning?</strong> Visit our platform and begin your first lesson!</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:8080" style="background-color: #4a90e2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Start Learning Now</a>
                </div>

                <p style="font-size: 14px; color: #666;">
                    Best regards,<br>
                    The WordMaster AI Team
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(user_email, subject, body, is_html=True)

    def send_daily_reminder(self, user_email, user_name, streak_days, words_learned):
        """Send daily learning reminder"""
        subject = f"📚 Daily Learning Reminder - Keep Your {streak_days} Day Streak!"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">Hello {user_name}!</h2>

                <p>Don't break your amazing <strong>{streak_days}-day learning streak</strong>! 🎯</p>

                <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">Your Progress So Far:</h3>
                    <ul style="margin: 0;">
                        <li>🔥 Current Streak: <strong>{streak_days} days</strong></li>
                        <li>📖 Words Learned: <strong>{words_learned}</strong></li>
                    </ul>
                </div>

                <p>Just 10 minutes of practice today can help you maintain your streak and learn new words!</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:8080" style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Continue Learning</a>
                </div>

                <p style="font-size: 14px; color: #666;">
                    Keep up the great work!<br>
                    The WordMaster AI Team
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(user_email, subject, body, is_html=True)

    def send_inactive_reminder(self, user_email, user_name, days_inactive):
        """Send reminder to inactive users"""
        subject = f"📚 We Miss You! Continue Your English Learning Journey"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a90e2;">Hello {user_name}!</h2>

                <p>We noticed you haven't visited WordMaster AI for {days_inactive} days. We miss you! 😊</p>

                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #6c757d; margin-top: 0;">Don't let your progress slip away!</h3>
                    <p>Consistent practice is key to mastering English vocabulary. Even just 5-10 minutes a day can make a huge difference.</p>
                </div>

                <p><strong>Ready to get back on track?</strong> We have new words and exercises waiting for you!</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:8080" style="background-color: #17a2b8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Resume Learning</a>
                </div>

                <p style="font-size: 14px; color: #666;">
                    We're here to support your learning journey!<br>
                    The WordMaster AI Team
                </p>
            </div>
        </body>
        </html>
        """

        return self.send_email(user_email, subject, body, is_html=True)


# Create a global instance
email_service = EmailService()


# Test function for standalone usage
def test_email():
    """Test function to verify email functionality"""
    test_email = "test@example.com"
    test_name = "Test User"

    print("Testing email functionality...")

    # Test welcome email
    success = email_service.send_welcome_email(test_email, test_name)
    if success:
        print("✅ Welcome email test passed")
    else:
        print("❌ Welcome email test failed")

    return success


if __name__ == "__main__":
    test_email()