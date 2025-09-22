#!/usr/bin/env python3
"""
Email Reminder Script for WordMaster AI
This script can be run manually or scheduled with cron to send daily reminders
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service
from database import Database
from datetime import datetime, timedelta
import sqlite3


def send_daily_reminders():
    """Send daily reminders to all users who need them"""
    print("🔄 Starting daily reminder process...")

    try:
        db = Database()
        conn = sqlite3.connect('wordmaster.db')
        cursor = conn.cursor()

        # Get users who haven't logged in today
        cursor.execute('''
            SELECT id, email, name, last_login, current_streak, total_words_learned
            FROM users 
            WHERE email IS NOT NULL AND email != ''
        ''')

        users = cursor.fetchall()
        conn.close()

        print(f"📧 Found {len(users)} users to check for reminders")

        reminders_sent = 0
        inactive_reminders = 0
        daily_reminders = 0

        for user in users:
            user_id, email, name, last_login, streak, words_learned = user

            # Calculate days inactive
            if last_login:
                try:
                    last_login_date = datetime.strptime(last_login, '%Y-%m-%d %H:%M:%S')
                    days_inactive = (datetime.now() - last_login_date).days
                except:
                    days_inactive = 7  # Default if parsing fails
            else:
                days_inactive = 7  # Default for users who never logged in

            try:
                if days_inactive >= 3:
                    # Send inactive reminder
                    success = email_service.send_inactive_reminder(email, name or "User", days_inactive)
                    if success:
                        inactive_reminders += 1
                        print(f"✅ Inactive reminder sent to {email} ({days_inactive} days inactive)")
                    else:
                        print(f"❌ Failed to send inactive reminder to {email}")

                elif streak > 0 and days_inactive < 2:
                    # Send daily reminder to maintain streak
                    success = email_service.send_daily_reminder(email, name or "User", streak, words_learned)
                    if success:
                        daily_reminders += 1
                        print(f"✅ Daily reminder sent to {email} (streak: {streak})")
                    else:
                        print(f"❌ Failed to send daily reminder to {email}")

                reminders_sent += 1

            except Exception as e:
                print(f"❌ Error sending reminder to {email}: {e}")

        print(f"\n📊 Summary:")
        print(f"   Total users checked: {len(users)}")
        print(f"   Daily reminders sent: {daily_reminders}")
        print(f"   Inactive reminders sent: {inactive_reminders}")
        print(f"   Total reminders sent: {daily_reminders + inactive_reminders}")

        return True

    except Exception as e:
        print(f"❌ Error in send_daily_reminders: {e}")
        return False


def test_email_system():
    """Test the email system with a sample email"""
    print("🧪 Testing email system...")

    test_email = "test@example.com"
    test_name = "Test User"

    try:
        # Test welcome email
        success = email_service.send_welcome_email(test_email, test_name)
        if success:
            print("✅ Welcome email test passed")
        else:
            print("❌ Welcome email test failed")

        return success

    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False


if __name__ == "__main__":
    print("📧 WordMaster AI Email Reminder System")
    print("=" * 50)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "daily":
            send_daily_reminders()
        elif command == "test":
            test_email_system()
        elif command == "all":
            print("🔄 Running all reminder types...")
            send_daily_reminders()
        else:
            print("❌ Unknown command. Use: daily, test, or all")
    else:
        print("Usage: python email_reminder.py [daily|test|all]")
        print("\nCommands:")
        print("  daily  - Send daily learning reminders")
        print("  test   - Test email system")
        print("  all    - Run all reminder types")