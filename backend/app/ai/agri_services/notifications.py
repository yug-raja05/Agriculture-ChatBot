import os
import time
import logging
import smtplib
import json
import urllib.request
import urllib.parse
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.config import settings
from app.core.database import db_manager

logger = logging.getLogger(__name__)

class NotificationProvider:
    def send(self, recipient: str, title: str, body: str) -> bool:
        raise NotImplementedError()

class EmailNotificationProvider(NotificationProvider):
    def send(self, recipient: str, title: str, body: str) -> bool:
        logger.info(f"[SMTP Email Send] To: {recipient}, Title: {title}")
        
        smtp_host = settings.SMTP_HOST
        smtp_port = settings.SMTP_PORT
        smtp_user = settings.SMTP_USER
        smtp_password = settings.SMTP_PASSWORD
        
        if not smtp_user or "your_email@gmail.com" in smtp_user or not smtp_password:
            logger.warning("SMTP credentials not fully configured. Simulating successful SMTP pipeline.")
            return True
            
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient
            msg['Subject'] = title
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_host, int(smtp_port))
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            raise e

class SMSNotificationProvider(NotificationProvider):
    def send(self, recipient: str, title: str, body: str) -> bool:
        logger.info(f"[SMS Send] Sending to: {recipient}...")
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_number = settings.TWILIO_NUMBER
        
        if not account_sid or not auth_token or not twilio_number:
            logger.warning("Twilio SMS credentials are not configured in settings. Simulating SMS dispatch.")
            return True
            
        try:
            # Send Twilio SMS via raw urllib REST call (no dependencies required)
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            
            data = urllib.parse.urlencode({
                "To": recipient,
                "From": twilio_number,
                "Body": f"{title}\n{body}"
            }).encode("utf-8")
            
            req = urllib.request.Request(url, data=data, method="POST")
            
            # Setup Twilio HTTP Basic Authentication
            import base64
            auth_str = f"{account_sid}:{auth_token}"
            auth_bytes = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            req.add_header("Authorization", f"Basic {auth_bytes}")
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            
            ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                resp_data = json.loads(response.read().decode('utf-8'))
                logger.info(f"Twilio SMS message SID: {resp_data.get('sid')}")
                
            return True
        except Exception as e:
            logger.error(f"Failed to send Twilio SMS: {e}")
            raise e

class PushNotificationProvider(NotificationProvider):
    def send(self, recipient: str, title: str, body: str) -> bool:
        logger.info(f"[Push Alert Send] Target device: {recipient}...")
        
        fcm_key = settings.FCM_SERVER_KEY
        if not fcm_key:
            logger.warning("FCM server key is not configured in settings. Simulating push notification.")
            return True
            
        try:
            # Deliver via legacy FCM endpoint using urllib
            url = "https://fcm.googleapis.com/fcm/send"
            payload = {
                "to": recipient,
                "notification": {
                    "title": title,
                    "body": body,
                    "sound": "default"
                }
            }
            data = json.dumps(payload).encode("utf-8")
            
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Authorization", f"key={fcm_key}")
            req.add_header("Content-Type", "application/json")
            
            ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                resp_data = json.loads(response.read().decode('utf-8'))
                logger.info(f"FCM Push Alert response: {resp_data}")
                
            return True
        except Exception as e:
            logger.error(f"Failed to deliver FCM push alerts: {e}")
            raise e

class DatabaseNotificationProvider(NotificationProvider):
    def send(self, recipient: str, title: str, body: str) -> bool:
        # Logs directly in DB. Handled within the central service class
        logger.info(f"[Database Log] Recorded notification: To: {recipient}, Content: '{title}'")
        return True

class NotificationProviderRegistry:
    def __init__(self):
        self._providers = {
            "email": EmailNotificationProvider(),
            "sms": SMSNotificationProvider(),
            "push": PushNotificationProvider(),
            "database": DatabaseNotificationProvider()
        }

    def get_provider(self) -> NotificationProvider:
        active_name = settings.ACTIVE_NOTIFICATION_PROVIDER
        return self._providers.get(active_name, self._providers["database"])

class NotificationService:
    """
    Enterprise Notification Platform.
    Delivers in-app, SMS, email, and emergency alerts.
    """
    def __init__(self):
        self.registry = NotificationProviderRegistry()

    async def send_notification(
        self,
        user_id: str,
        recipient: str,
        category: str,  # Weather, Disease, Market, Reminder, System
        title: str,
        body: str,
        db: Optional[AsyncIOMotorDatabase] = None
    ) -> Dict[str, Any]:
        """
        Sends notification and records logs in MongoDB.
        """
        prov = self.registry.get_provider()
        active_prov_name = settings.ACTIVE_NOTIFICATION_PROVIDER
        
        # Implement retries for notification sends (3 attempts max)
        success = False
        last_error = None
        for attempt in range(1, 4):
            try:
                success = prov.send(recipient, title, body)
                if success:
                    break
            except Exception as e:
                last_error = e
                logger.warning(f"Notification send failed on attempt {attempt}/3: {e}")
                time.sleep(1)
        
        # Dynamic logger entry
        notification_entry = {
            "user_id": user_id,
            "recipient": recipient,
            "category": category,
            "title": title,
            "body": body,
            "delivery_status": "Delivered" if success else "Failed",
            "provider_used": active_prov_name,
            "timestamp": time.time(),
            "error_log": str(last_error) if last_error else None
        }

        # Auto connect database if not passed
        active_db = db if db is not None else db_manager.db
        if active_db is not None:
            try:
                await active_db["notifications"].insert_one(notification_entry)
            except Exception as e:
                logger.error(f"Failed to log notification in MongoDB: {e}")

        return {
            "notification_sent": success,
            "category": category,
            "provider": active_prov_name,
            "recipient": recipient,
            "status": "success" if success else "failed"
        }

notification_service = NotificationService()
