#!/usr/bin/env python3
"""
Mobile Alert Notification System for Vehicle Predictive Maintenance
This module extends the Vehicle Alert System to send notifications to mobile devices.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
import time
import threading

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Try to import Firebase, but make it optional
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    # Create a placeholder for messaging
    class messaging:
        class AndroidNotification:
            def __init__(self, **kwargs):
                pass
        class AndroidConfig:
            def __init__(self, **kwargs):
                pass
        class Notification:
            def __init__(self, **kwargs):
                pass
        class Message:
            def __init__(self, **kwargs):
                pass
        @staticmethod
        def send(message):
            return "firebase-not-available"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/mobile_alerts.log')
    ]
)
logger = logging.getLogger(__name__)

class MobileAlertSystem:
    """
    Mobile alert system that sends notifications to driver's mobile devices
    """
    def __init__(self, alert_system, config_path='config/mobile_config.json', 
                 firebase_cred_path='config/firebase_credentials.json'):
        """
        Initialize the mobile alert system
        
        Args:
            alert_system: Vehicle alert system instance
            config_path (str): Path to mobile configuration file
            firebase_cred_path (str): Path to Firebase credentials file
        """
        self.alert_system = alert_system
        self.config_path = config_path
        self.firebase_cred_path = firebase_cred_path
        self.config = {}
        self.firebase_initialized = False
        self.registered_devices = {}
        self.alert_history = {}  # Track sent alerts to avoid duplicates
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Load or create configuration
        self._load_or_create_config()
        
        # Initialize Firebase if credentials exist
        self._initialize_firebase()
        
    def _load_or_create_config(self):
        """Load configuration or create default if not exists"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded mobile alert configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading mobile configuration: {e}")
                self._create_default_config()
        else:
            logger.info("Mobile configuration not found, creating default")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default mobile alert configuration"""
        self.config = {
            "notification_settings": {
                "enable_mobile_alerts": True,
                "high_priority_cooldown_minutes": 30,
                "medium_priority_cooldown_minutes": 120,
                "low_priority_cooldown_minutes": 360,
                "quiet_hours_start": 22,  # 10 PM
                "quiet_hours_end": 7,      # 7 AM
                "respect_quiet_hours": True,
                "override_quiet_hours_for_high_priority": True
            },
            "notification_services": {
                "use_firebase": False,  # Disabled by default
                "use_sms": False,
                "use_email": False
            },
            "sms_settings": {
                "api_key": "",
                "from_number": ""
            },
            "email_settings": {
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "vehicle-alerts@example.com"
            }
        }
        
        # Save default configuration
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, indent=4, fp=f)
            logger.info(f"Created default mobile configuration at {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving default mobile configuration: {e}")
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK for push notifications"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase Admin SDK not installed, push notifications disabled")
            return
            
        if not self.config["notification_services"]["use_firebase"]:
            logger.info("Firebase notifications disabled in config")
            return
        
        if not os.path.exists(self.firebase_cred_path):
            logger.warning(f"Firebase credentials not found at {self.firebase_cred_path}")
            return
        
        try:
            cred = credentials.Certificate(self.firebase_cred_path)
            firebase_admin.initialize_app(cred)
            self.firebase_initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
            
            # Load registered devices
            devices_path = 'config/registered_devices.json'
            if os.path.exists(devices_path):
                with open(devices_path, 'r') as f:
                    self.registered_devices = json.load(f)
                logger.info(f"Loaded {len(self.registered_devices)} registered devices")
        
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
    
    def start_monitoring(self, interval=10.0):
        """
        Start monitoring for alerts and sending mobile notifications
        
        Args:
            interval (float): Check interval in seconds
        """
        if not self.config["notification_settings"]["enable_mobile_alerts"]:
            logger.info("Mobile alerts disabled in config")
            return
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("Mobile alert monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for alerts"""
        self.running = False
        if hasattr(self, 'monitor_thread') and self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("Mobile alert monitoring stopped")
    
    def _monitoring_loop(self, interval):
        """
        Main monitoring loop for checking alerts and sending notifications
        
        Args:
            interval (float): Check interval in seconds
        """
        while self.running:
            try:
                # Get current alerts from the alert system
                current_alerts = self.alert_system.get_current_alerts()
                
                # Process and send notifications for these alerts
                self._process_alerts(current_alerts)
                
                # Sleep for the specified interval
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in mobile alert monitoring loop: {e}")
                time.sleep(interval)
    
    def _process_alerts(self, alerts):
        """
        Process alerts and send notifications if needed
        
        Args:
            alerts (list): List of current alerts
        """
        current_time = datetime.now()
        
        # Check if we're in quiet hours
        in_quiet_hours = self._check_quiet_hours(current_time)
        
        for alert in alerts:
            component = alert['component']
            alert_level = alert['alert_level']
            
            # Check if this alert should be sent based on cooldown and quiet hours
            if self._should_send_alert(component, alert_level, current_time, in_quiet_hours):
                # Send the notification
                self._send_notification(alert)
                
                # Update alert history
                self.alert_history[component] = {
                    'level': alert_level,
                    'sent_time': current_time,
                    'message': alert['message']
                }
    
    def _check_quiet_hours(self, current_time):
        """
        Check if current time is within quiet hours
        
        Args:
            current_time (datetime): Current time
            
        Returns:
            bool: True if within quiet hours, False otherwise
        """
        if not self.config["notification_settings"]["respect_quiet_hours"]:
            return False
            
        quiet_start = self.config["notification_settings"]["quiet_hours_start"]
        quiet_end = self.config["notification_settings"]["quiet_hours_end"]
        
        current_hour = current_time.hour
        
        # Handle time range that crosses midnight
        if quiet_start > quiet_end:
            return current_hour >= quiet_start or current_hour < quiet_end
        else:
            return current_hour >= quiet_start and current_hour < quiet_end
    
    def _should_send_alert(self, component, level, current_time, in_quiet_hours):
        """
        Determine if an alert should be sent based on cooldown and quiet hours
        
        Args:
            component (str): Vehicle component
            level (str): Alert level (high, medium, low)
            current_time (datetime): Current time
            in_quiet_hours (bool): Whether current time is within quiet hours
            
        Returns:
            bool: True if alert should be sent, False otherwise
        """
        # Check quiet hours - only send high priority during quiet hours if override enabled
        if in_quiet_hours:
            if level == 'high' and self.config["notification_settings"]["override_quiet_hours_for_high_priority"]:
                pass  # Allow high priority alerts during quiet hours
            else:
                return False  # Don't send other alerts during quiet hours
        
        # Check cooldown periods
        if component in self.alert_history:
            last_alert = self.alert_history[component]
            sent_time = last_alert['sent_time']
            last_level = last_alert['level']
            
            # If new alert is higher priority than previous, always send it
            if (level == 'high' and last_level != 'high') or \
               (level == 'medium' and last_level == 'low'):
                return True
                
            # Get cooldown duration based on alert level
            if level == 'high':
                cooldown_minutes = self.config["notification_settings"]["high_priority_cooldown_minutes"]
            elif level == 'medium':
                cooldown_minutes = self.config["notification_settings"]["medium_priority_cooldown_minutes"]
            else:
                cooldown_minutes = self.config["notification_settings"]["low_priority_cooldown_minutes"]
                
            # Check if cooldown period has elapsed
            cooldown_time = sent_time + timedelta(minutes=cooldown_minutes)
            return current_time >= cooldown_time
            
        # No previous alert for this component, so send it
        return True
    
    def _send_notification(self, alert):
        """
        Send notification through configured channels
    
        Args:
        alert (dict): Alert data
        """
        message = self._format_notification_message(alert)
        title = self._format_notification_title(alert)
    
        # Check if any notification service is enabled
        any_service_enabled = (
            (self.config["notification_services"]["use_firebase"] and self.firebase_initialized) or
            self.config["notification_services"]["use_sms"] or
            self.config["notification_services"]["use_email"]
        )
    
        # Only log and attempt to send if some service is enabled
        if any_service_enabled:
            # Log the notification (without emojis)
            safe_title = title.encode('ascii', 'ignore').decode('ascii')
            safe_message = message.encode('ascii', 'ignore').decode('ascii')
            logger.info(f"Sending mobile notification: {safe_title} - {safe_message}")
        
            # Send through enabled channels
            success = False
        
            if self.config["notification_services"]["use_firebase"] and self.firebase_initialized:
                success = self._send_firebase_notification(title, message, alert)
            
            if self.config["notification_services"]["use_sms"]:
                success = success or self._send_sms_notification(message, alert)
            
            if self.config["notification_services"]["use_email"]:
                success = success or self._send_email_notification(title, message, alert)
            
            if not success:
                logger.warning(f"Failed to send notification for {alert['component']} through any channel")
            else:
        # Just log that notification was processed but not sent (no channels enabled)
                logger.debug(f"Alert for {alert['component']} processed but not sent (no notification channels enabled)")
    
    def _format_notification_title(self, alert):
        """
        Format notification title based on alert level and component
        
        Args:
            alert (dict): Alert data
            
        Returns:
            str: Formatted notification title
        """
        level_prefix = {
            'high': 'URGENT: ',
            'medium': 'WARNING: ',
            'low': 'NOTICE: '
        }
        
        component_name = alert['component'].replace('_', ' ').title()
        return f"{level_prefix.get(alert['alert_level'], '')}{component_name} Issue Detected"
    
    def _format_notification_message(self, alert):
        """
        Format notification message
        
        Args:
            alert (dict): Alert data
            
        Returns:
            str: Formatted notification message
        """
        # Use the message from the alert, which already has the details
        return alert['message']
    
    def _send_firebase_notification(self, title, message, alert):
        """
        Send notification through Firebase Cloud Messaging
        
        Args:
            title (str): Notification title
            message (str): Notification message
            alert (dict): Alert data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.firebase_initialized:
            logger.warning("Firebase not initialized, can't send push notification")
            return False
            
        if not self.registered_devices:
            logger.warning("No registered devices found for Firebase notifications")
            return False
            
        try:
            # Create a message for each registered device
            for device_token, device_info in self.registered_devices.items():
                # Create message
                android_notification = messaging.AndroidNotification(
                    title=title,
                    body=message,
                    priority='high' if alert['alert_level'] == 'high' else 'normal',
                    color='#FF0000' if alert['alert_level'] == 'high' else 
                           '#FFA500' if alert['alert_level'] == 'medium' else '#FFFF00'
                )
                
                android_config = messaging.AndroidConfig(
                    priority='high' if alert['alert_level'] == 'high' else 'normal',
                    notification=android_notification
                )
                
                notification = messaging.Notification(
                    title=title,
                    body=message
                )
                
                msg = messaging.Message(
                    notification=notification,
                    android=android_config,
                    token=device_token,
                    data={
                        'component': alert['component'],
                        'alert_level': alert['alert_level'],
                        'probability': str(alert['probability']),
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                # Send the message
                response = messaging.send(msg)
                logger.info(f"Firebase notification sent: {response}")
                
            return True
            
        except Exception as e:
            logger.error(f"Error sending Firebase notification: {e}")
            return False
    
    def _send_sms_notification(self, message, alert):
        """
        Send notification through SMS
        
        Args:
            message (str): Notification message
            alert (dict): Alert data
            
        Returns:
            bool: True if successful, False otherwise
        """
        sms_settings = self.config["sms_settings"]
        api_key = sms_settings.get("api_key", "")
        from_number = sms_settings.get("from_number", "")
        
        if not api_key or not from_number:
            logger.warning("SMS settings incomplete, can't send SMS notification")
            return False
            
        # Find phone numbers in registered devices
        phone_numbers = []
        for device_info in self.registered_devices.values():
            if "phone_number" in device_info:
                phone_numbers.append(device_info["phone_number"])
                
        if not phone_numbers:
            logger.warning("No phone numbers found for SMS notifications")
            return False
            
        # This is a placeholder for a real SMS API integration
        # In a real implementation, you would use a service like Twilio, Nexmo, etc.
        try:
            for phone_number in phone_numbers:
                logger.info(f"Would send SMS to {phone_number}: {message}")
                # In a real implementation:
                # response = requests.post(
                #     'https://api.sms-service.com/send',
                #     json={
                #         'api_key': api_key,
                #         'from': from_number,
                #         'to': phone_number,
                #         'message': message
                #     }
                # )
                # response.raise_for_status()
                
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            return False
    
    def _send_email_notification(self, title, message, alert):
        """
        Send notification through email
        
        Args:
            title (str): Notification title
            message (str): Notification message
            alert (dict): Alert data
            
        Returns:
            bool: True if successful, False otherwise
        """
        email_settings = self.config["email_settings"]
        smtp_server = email_settings.get("smtp_server", "")
        
        if not smtp_server:
            logger.warning("Email settings incomplete, can't send email notification")
            return False
            
        # Find email addresses in registered devices
        email_addresses = []
        for device_info in self.registered_devices.values():
            if "email" in device_info:
                email_addresses.append(device_info["email"])
                
        if not email_addresses:
            logger.warning("No email addresses found for email notifications")
            return False
            
        # This is a placeholder for a real email sending implementation
        # In a real implementation, you would use smtplib or a service like SendGrid
        try:
            for email_address in email_addresses:
                logger.info(f"Would send email to {email_address}: {title} - {message}")
                # In a real implementation:
                # import smtplib
                # from email.mime.text import MIMEText
                # from email.mime.multipart import MIMEMultipart
                # msg = MIMEMultipart()
                # msg['From'] = email_settings['from_address']
                # msg['To'] = email_address
                # msg['Subject'] = title
                # msg.attach(MIMEText(message, 'plain'))
                # server = smtplib.SMTP(smtp_server, email_settings['smtp_port'])
                # server.starttls()
                # server.login(email_settings['username'], email_settings['password'])
                # server.send_message(msg)
                # server.quit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    def register_device(self, device_token, device_info=None):
        """
        Register a new device for notifications
        
        Args:
            device_token (str): Device token for push notifications
            device_info (dict): Additional device information (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if device_info is None:
            device_info = {}
            
        try:
            # Add the device to registered devices
            self.registered_devices[device_token] = device_info
            
            # Save registered devices
            devices_path = 'config/registered_devices.json'
            os.makedirs(os.path.dirname(devices_path), exist_ok=True)
            with open(devices_path, 'w') as f:
                json.dump(self.registered_devices, f, indent=4)
                
            logger.info(f"Device registered: {device_token}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return False
    
    def unregister_device(self, device_token):
        """
        Unregister a device from notifications
        
        Args:
            device_token (str): Device token to unregister
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove the device if it exists
            if device_token in self.registered_devices:
                del self.registered_devices[device_token]
                
                # Save updated registered devices
                devices_path = 'config/registered_devices.json'
                with open(devices_path, 'w') as f:
                    json.dump(self.registered_devices, f, indent=4)
                    
                logger.info(f"Device unregistered: {device_token}")
                return True
            else:
                logger.warning(f"Device not found for unregistration: {device_token}")
                return False
                
        except Exception as e:
            logger.error(f"Error unregistering device: {e}")
            return False
    
    def update_config(self, new_config):
        """
        Update mobile alert system configuration
        
        Args:
            new_config (dict): New configuration dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update configuration
            self.config.update(new_config)
            
            # Save to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, indent=4, fp=f)
                
            logger.info("Mobile alert configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating mobile alert configuration: {e}")
            return False


# Example mobile app integration components

class MobileAppIntegration:
    """
    Example class for integrating with a mobile app for vehicle alerts
    """
    def __init__(self, mobile_alert_system, api_port=5000):
        """
        Initialize mobile app integration
        
        Args:
            mobile_alert_system (MobileAlertSystem): Mobile alert system instance
            api_port (int): Port for REST API
        """
        self.mobile_alert_system = mobile_alert_system
        self.api_port = api_port
    
    def start_rest_api(self):
        """
        Start REST API for mobile app integration
        This is a placeholder for a real implementation using Flask, FastAPI, etc.
        """
        logger.info(f"Mobile app integration API would start on port {self.api_port}")
        # In a real implementation:
        # from flask import Flask, request, jsonify
        # app = Flask(__name__)
        #
        # @app.route('/api/register-device', methods=['POST'])
        # def register_device():
        #     data = request.json
        #     success = self.mobile_alert_system.register_device(
        #         data['device_token'], data.get('device_info', {})
        #     )
        #     return jsonify({'success': success})
        #
        # @app.route('/api/unregister-device', methods=['POST'])
        # def unregister_device():
        #     data = request.json
        #     success = self.mobile_alert_system.unregister_device(data['device_token'])
        #     return jsonify({'success': success})
        #
        # app.run(host='0.0.0.0', port=self.api_port)
        
    def mock_app_registration(self):
        """
        Mock registration from a mobile app
        """
        device_token = f"mock-device-{int(time.time())}"
        device_info = {
            "device_name": "Driver's Android Phone",
            "platform": "Android",
            "os_version": "12",
            "app_version": "1.0.0",
            "phone_number": "+1234567890",
            "email": "driver@example.com",
            "user_name": "Test Driver"
        }
        
        success = self.mobile_alert_system.register_device(device_token, device_info)
        logger.info(f"Mock device registration {'successful' if success else 'failed'}")
        return device_token


# Example usage 
def main():
    """Main function to demonstrate the mobile alert system"""
    from vehicle_alert_system import VehicleAlertSystem, MockTelemetryProvider, DriverAlertInterface
    
    print("Starting Mobile Alert System Demo...")
    
    # Initialize components
    alert_system = VehicleAlertSystem()
    mobile_alert_system = MobileAlertSystem(alert_system)
    mobile_app = MobileAppIntegration(mobile_alert_system)
    
    # Register a mock device
    device_token = mobile_app.mock_app_registration()
    print(f"Registered mock device: {device_token}")
    
    # Initialize mock telemetry provider
    telemetry_provider = MockTelemetryProvider(failure_probability=0.4)
    
    # Initialize driver interface
    driver_interface = DriverAlertInterface(alert_system)
    
    try:
        # Start monitoring with mock telemetry
        driver_interface.start_monitoring(
            telemetry_source=telemetry_provider.get_telemetry,
            interval=2.0
        )
        
        # Start mobile alert monitoring
        mobile_alert_system.start_monitoring(interval=5.0)
        
        print("\nSystem is now running. Mobile alerts will be simulated.")
        print("Press Ctrl+C to exit.")
        
        # Main loop
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting Mobile Alert System Demo...")
    finally:
        driver_interface.stop_monitoring()
        mobile_alert_system.stop_monitoring()


if __name__ == '__main__':
    main()