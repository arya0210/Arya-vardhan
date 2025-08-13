#!/usr/bin/env python3
"""
Mobile App Client for Vehicle Alerts
This module provides a mobile app client implementation for the Vehicle Alert System.
"""

import json
import requests
import os
import time
from datetime import datetime, timedelta
import threading
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/mobile_client.log')
    ]
)
logger = logging.getLogger(__name__)

class MobileAppClient:
    """
    Mobile app client for receiving vehicle alerts
    """
    def __init__(self, server_url='http://localhost:5000'):
        """
        Initialize mobile app client
        
        Args:
            server_url (str): URL of the vehicle alert server
        """
        self.server_url = server_url
        self.device_token = None
        self.user_info = {
            "device_name": "User's Phone",
            "platform": "Android",
            "os_version": "12",
            "app_version": "1.0.0",
            "phone_number": "",
            "email": "",
            "user_name": ""
        }
        self.alerts = []
        self.alert_callbacks = []
        self.connected = False
        self.settings = self._load_settings()
        
    def _load_settings(self):
        """
        Load client settings from file
        
        Returns:
            dict: Client settings
        """
        settings_path = 'client_settings.json'
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
        
        # Default settings
        default_settings = {
            "notification_sound": True,
            "vibration": True,
            "show_low_priority": True,
            "alert_expiry_hours": 24,
            "auto_connect": True,
            "theme": "light"
        }
        
        return default_settings
    
    def _save_settings(self):
        """Save client settings to file"""
        settings_path = 'client_settings.json'
        
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, indent=4, fp=f)
            logger.info("Settings saved")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def register_device(self, user_info=None):
        """
        Register device with the alert server
        
        Args:
            user_info (dict): User information
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        if user_info:
            self.user_info.update(user_info)
            
        # In a real implementation, this would send a request to the server
        # For demo purposes, we'll generate a unique token locally
        self.device_token = f"mobile-device-{int(time.time())}"
        logger.info(f"Device registered with token: {self.device_token}")
        
        # Save device token
        try:
            with open('device_token.txt', 'w') as f:
                f.write(self.device_token)
        except Exception as e:
            logger.error(f"Error saving device token: {e}")
            
        # Example of real server request:
        # try:
        #     response = requests.post(
        #         f"{self.server_url}/api/register-device",
        #         json={
        #             "device_info": self.user_info
        #         }
        #     )
        #     if response.status_code == 200:
        #         result = response.json()
        #         if result.get('success'):
        #             self.device_token = result.get('device_token')
        #             return True
        #     return False
        # except Exception as e:
        #     logger.error(f"Error registering device: {e}")
        #     return False
            
        return True
    
    def unregister_device(self):
        """
        Unregister device from the alert server
        
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        if not self.device_token:
            logger.warning("No device token to unregister")
            return False
            
        # In a real implementation, this would send a request to the server
        logger.info(f"Device unregistered: {self.device_token}")
        self.device_token = None
        
        # Remove saved device token
        if os.path.exists('device_token.txt'):
            os.remove('device_token.txt')
            
        # Example of real server request:
        # try:
        #     response = requests.post(
        #         f"{self.server_url}/api/unregister-device",
        #         json={
        #             "device_token": self.device_token
        #         }
        #     )
        #     if response.status_code == 200:
        #         result = response.json()
        #         if result.get('success'):
        #             self.device_token = None
        #             return True
        #     return False
        # except Exception as e:
        #     logger.error(f"Error unregistering device: {e}")
        #     return False
            
        return True
    
    def connect(self):
        """
        Connect to the alert server for receiving alerts
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        # In a real implementation, this would establish a WebSocket connection
        # or start a background process to poll for alerts
        
        # For demonstration, we'll simulate connection
        self.connected = True
        logger.info("Connected to alert server")
        
        # Start simulated alert reception
        threading.Thread(target=self._simulate_alert_reception, daemon=True).start()
        
        return True
    
    def disconnect(self):
        """
        Disconnect from the alert server
        
        Returns:
            bool: True if disconnection was successful, False otherwise
        """
        if not self.connected:
            logger.warning("Not connected to alert server")
            return False
            
        # Stop simulated alert reception
        self.connected = False
        logger.info("Disconnected from alert server")
        
        return True
    
    def _simulate_alert_reception(self):
        """Simulate receiving alerts from the server"""
        # This is a simulation for demonstration purposes
        # In a real implementation, this would be replaced with a WebSocket
        # connection or a background polling process
        
        # Component failure probabilities - these would normally come from the server
        component_probs = {
            'engine': 0.3,
            'transmission': 0.2,
            'brakes': 0.25,
            'battery': 0.15,
            'electrical': 0.1
        }
        
        # Alert levels based on probability thresholds
        def get_level(prob):
            if prob > 0.7:
                return 'high'
            elif prob > 0.4:
                return 'medium'
            elif prob > 0.2:
                return 'low'
            return None
        
        count = 0
        while self.connected:
            count += 1
            # Every 10 iterations, simulate receiving an alert
            if count % 10 == 0:
                # Choose a random component to generate an alert for
                import random
                component = random.choice(list(component_probs.keys()))
                
                # Simulate varying probability
                base_prob = component_probs[component]
                variation = random.uniform(-0.1, 0.3)
                probability = min(0.95, max(0.1, base_prob + variation))
                
                level = get_level(probability)
                if level:
                    alert = {
                        'component': component,
                        'probability': probability,
                        'alert_level': level,
                        'timestamp': datetime.now().isoformat(),
                        'message': self._generate_mock_message(component, level, probability)
                    }
                    
                    # Add to alerts and notify callbacks
                    self.alerts.append(alert)
                    for callback in self.alert_callbacks:
                        callback(alert)
                    
                    # Log the alert
                    logger.info(f"Received alert: {component} - {level} - {probability:.2f}")
            
            # Sleep for a short period
            time.sleep(1)
    
    def _generate_mock_message(self, component, level, probability):
        """Generate a mock alert message"""
        time_frame = {
            'high': 'immediate',
            'medium': 'soon',
            'low': 'future'
        }
        
        urgency = {
            'high': 'Urgent service required! ',
            'medium': 'Service recommended. ',
            'low': 'Monitor condition. '
        }
        
        component_name = component.replace('_', ' ').title()
        
        msg = f"{urgency[level]}{component_name} issue detected. "
        msg += f"Potential failure risk: {probability:.1%}. "
        
        if level == 'high':
            msg += "Please visit a service center immediately."
        elif level == 'medium':
            msg += "Schedule service within the next week."
        else:
            msg += "Check during your next maintenance visit."
            
        return msg
    
    def register_alert_callback(self, callback):
        """
        Register a callback function to be called when a new alert is received
        
        Args:
            callback (function): Function to call with the alert data
        """
        if callback not in self.alert_callbacks:
            self.alert_callbacks.append(callback)
    
    def unregister_alert_callback(self, callback):
        """
        Unregister a previously registered callback function
        
        Args:
            callback (function): Function to unregister
        """
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def get_alerts(self, filter_level=None):
        """
        Get all received alerts, optionally filtered by level
        
        Args:
            filter_level (str): Alert level to filter by (high, medium, low)
            
        Returns:
            list: List of alerts
        """
        if filter_level:
            return [alert for alert in self.alerts if alert['alert_level'] == filter_level]
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
        logger.info("Alerts cleared")
    
    def update_settings(self, new_settings):
        """
        Update client settings
        
        Args:
            new_settings (dict): New settings dictionary
        """
        self.settings.update(new_settings)
        self._save_settings()
        logger.info("Settings updated")


class MobileAppGUI:
    """GUI for the mobile app client"""
    def __init__(self, root, client):
        """
        Initialize the mobile app GUI
        
        Args:
            root (tk.Tk): Tkinter root window
            client (MobileAppClient): Mobile app client instance
        """
        self.root = root
        self.client = client
        
        # Register for alert callbacks
        self.client.register_alert_callback(self._on_alert_received)
        
        # Setup UI
        self._setup_ui()
        
        # Connect to server if auto-connect is enabled
        if self.client.settings.get('auto_connect', True):
            self._connect()
    
    def _setup_ui(self):
        """Setup the user interface"""
        self.root.title("Vehicle Alert System - Mobile App")
        self.root.geometry("400x600")
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.alerts_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.alerts_tab, text="Alerts")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.about_tab, text="About")
        
        # Setup tabs
        self._setup_alerts_tab()
        self._setup_settings_tab()
        self._setup_about_tab()
    
    def _setup_alerts_tab(self):
        """Setup the alerts tab"""
        # Connection frame
        conn_frame = ttk.Frame(self.alerts_tab)
        conn_frame.pack(fill=tk.X, pady=5)
        
        self.conn_status = ttk.Label(conn_frame, text="Status: Disconnected")
        self.conn_status.pack(side=tk.LEFT, padx=5)
        
        self.conn_button = ttk.Button(conn_frame, text="Connect", command=self._connect)
        self.conn_button.pack(side=tk.RIGHT, padx=5)
        
        # Filters frame
        filter_frame = ttk.Frame(self.alerts_tab)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var, 
                        value="all", command=self._apply_filter).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="High", variable=self.filter_var, 
                        value="high", command=self._apply_filter).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Medium", variable=self.filter_var, 
                        value="medium", command=self._apply_filter).pack(side=tk.LEFT)
        ttk.Radiobutton(filter_frame, text="Low", variable=self.filter_var, 
                        value="low", command=self._apply_filter).pack(side=tk.LEFT)
        
        # Clear button
        ttk.Button(filter_frame, text="Clear", command=self._clear_alerts).pack(side=tk.RIGHT, padx=5)
        
        # Alerts list
        self.alert_list = ttk.Frame(self.alerts_tab)
        self.alert_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollable canvas for alerts
        self.canvas = tk.Canvas(self.alert_list)
        scrollbar = ttk.Scrollbar(self.alert_list, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Empty alert message
        self.empty_label = ttk.Label(self.scrollable_frame, text="No alerts to display")
        self.empty_label.pack(pady=20)
    
    def _setup_settings_tab(self):
        """Setup the settings tab"""
        # User information frame
        user_frame = ttk.LabelFrame(self.settings_tab, text="User Information")
        user_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # User name
        ttk.Label(user_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_var = tk.StringVar(value=self.client.user_info.get("user_name", ""))
        ttk.Entry(user_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Phone number
        ttk.Label(user_frame, text="Phone:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_var = tk.StringVar(value=self.client.user_info.get("phone_number", ""))
        ttk.Entry(user_frame, textvariable=self.phone_var).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Email
        ttk.Label(user_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_var = tk.StringVar(value=self.client.user_info.get("email", ""))
        ttk.Entry(user_frame, textvariable=self.email_var).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Device information
        device_frame = ttk.LabelFrame(self.settings_tab, text="Device Information")
        device_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(device_frame, text="Device:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(device_frame, text=self.client.user_info.get("device_name", "Unknown")).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(device_frame, text="Platform:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(device_frame, text=f"{self.client.user_info.get('platform', 'Unknown')} {self.client.user_info.get('os_version', '')}").grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(device_frame, text="App Version:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(device_frame, text=self.client.user_info.get("app_version", "1.0.0")).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Notification settings
        notif_frame = ttk.LabelFrame(self.settings_tab, text="Notification Settings")
        notif_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Sound
        self.sound_var = tk.BooleanVar(value=self.client.settings.get("notification_sound", True))
        ttk.Checkbutton(notif_frame, text="Enable Sound", variable=self.sound_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Vibration
        self.vibration_var = tk.BooleanVar(value=self.client.settings.get("vibration", True))
        ttk.Checkbutton(notif_frame, text="Enable Vibration", variable=self.vibration_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Show low priority
        self.show_low_var = tk.BooleanVar(value=self.client.settings.get("show_low_priority", True))
        ttk.Checkbutton(notif_frame, text="Show Low Priority Alerts", variable=self.show_low_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Auto connect
        self.auto_connect_var = tk.BooleanVar(value=self.client.settings.get("auto_connect", True))
        ttk.Checkbutton(notif_frame, text="Automatically Connect on Startup", variable=self.auto_connect_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # Save settings button
        ttk.Button(self.settings_tab, text="Save Settings", command=self._save_settings).pack(pady=10)
        
        # Registration buttons
        reg_frame = ttk.Frame(self.settings_tab)
        reg_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(reg_frame, text="Register Device", command=self._register_device).pack(side=tk.LEFT, padx=5)
        ttk.Button(reg_frame, text="Unregister Device", command=self._unregister_device).pack(side=tk.RIGHT, padx=5)
    
    def _setup_about_tab(self):
        """Setup the about tab"""
        # App info
        ttk.Label(self.about_tab, text="Vehicle Alert System", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.about_tab, text="Mobile App Client").pack()
        ttk.Label(self.about_tab, text="Version 1.0.0").pack(pady=5)
        
        # Description
        desc_frame = ttk.LabelFrame(self.about_tab, text="Description")
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        desc_text = ("This mobile application allows you to receive real-time alerts "
                    "about your vehicle's health and potential issues. Stay informed "
                    "about engine, transmission, brakes, battery, and electrical "
                    "system problems before they cause damage.")
        
        desc = tk.Text(desc_frame, wrap=tk.WORD, height=6)
        desc.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        desc.insert(tk.END, desc_text)
        desc.config(state=tk.DISABLED)
        
        # Contact info
        contact_frame = ttk.LabelFrame(self.about_tab, text="Contact Information")
        contact_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(contact_frame, text="Support Email: support@vehiclealerts.example.com").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(contact_frame, text="Website: https://www.vehiclealerts.example.com").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(contact_frame, text="Phone: +1-555-VEHICLE").pack(anchor=tk.W, padx=5, pady=2)
    
    def _connect(self):
        """Connect to the alert server"""
        if not self.client.connected:
            if self.client.connect():
                self.conn_status.config(text="Status: Connected")
                self.conn_button.config(text="Disconnect", command=self._disconnect)
        else:
            logger.warning("Already connected to server")
    
    def _disconnect(self):
        """Disconnect from the alert server"""
        if self.client.connected:
            if self.client.disconnect():
                self.conn_status.config(text="Status: Disconnected")
                self.conn_button.config(text="Connect", command=self._connect)
        else:
            logger.warning("Not connected to server")
    
    def _apply_filter(self):
        """Apply filter to alerts list"""
        filter_value = self.filter_var.get()
        self._refresh_alerts(filter_value)
    
    def _clear_alerts(self):
        """Clear all alerts"""
        if messagebox.askyesno("Clear Alerts", "Are you sure you want to clear all alerts?"):
            self.client.clear_alerts()
            self._refresh_alerts()
    
    def _refresh_alerts(self, filter_level="all"):
        """Refresh the alerts list"""
        # Clear current alerts
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get filtered alerts
        if filter_level == "all":
            alerts = self.client.get_alerts()
        else:
            alerts = self.client.get_alerts(filter_level)
        
        # Display empty message if no alerts
        if not alerts:
            self.empty_label = ttk.Label(self.scrollable_frame, text="No alerts to display")
            self.empty_label.pack(pady=20)
            return
        
        # Display alerts
        for alert in reversed(alerts):  # Newest first
            self._add_alert_widget(alert)
    
    def _add_alert_widget(self, alert):
        """Add an alert widget to the list"""
        # Create frame for this alert
        level = alert['alert_level']
        bg_color = {
            'high': '#FFDDDD',
            'medium': '#FFFFDD',
            'low': '#DDDDFF'
        }.get(level, '#FFFFFF')
        
        frame = ttk.Frame(self.scrollable_frame, style=f'{level}.TFrame')
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Apply custom style based on level
        try:
            style = ttk.Style()
            style.configure(f'{level}.TFrame', background=bg_color)
        except:
            # If style fails, continue anyway
            pass
        
        # Alert icon based on level
        icon_text = {
            'high': '🔴',
            'medium': '🟠',
            'low': '🟡'
        }.get(level, '⚪')
        
        icon_label = ttk.Label(frame, text=icon_text, font=("Arial", 16))
        icon_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
        
        # Component name
        component_name = alert['component'].replace('_', ' ').title()
        component_label = ttk.Label(frame, text=component_name, font=("Arial", 12, "bold"))
        component_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Alert level and probability
        level_text = level.title()
        prob_text = f"{alert['probability']:.1%}"
        level_label = ttk.Label(frame, text=f"{level_text} Risk: {prob_text}")
        level_label.grid(row=0, column=2, sticky=tk.E, padx=5, pady=2)
        
        # Alert message
        message_label = ttk.Label(frame, text=alert['message'], wraplength=300)
        message_label.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        # Timestamp
        try:
            timestamp = datetime.fromisoformat(alert['timestamp'])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = str(alert['timestamp'])
            
        time_label = ttk.Label(frame, text=time_str, font=("Arial", 8))
        time_label.grid(row=2, column=1, columnspan=2, sticky=tk.E, padx=5, pady=2)
        
        # Add separator
        ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=1)
    
    def _on_alert_received(self, alert):
        """Callback when new alert is received"""
        # Check if we should display low priority alerts
        if alert['alert_level'] == 'low' and not self.client.settings.get('show_low_priority', True):
            return
            
        # Refresh the alerts list
        self._refresh_alerts(self.filter_var.get())
        
        # Show notification
        level_emoji = {
            'high': '🔴',
            'medium': '🟠',
            'low': '🟡'
        }.get(alert['alert_level'], '⚪')
        
        component_name = alert['component'].replace('_', ' ').title()
        
        # On Windows, use system notification
        if os.name == 'nt':
            # This requires win10toast library
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    f"{level_emoji} Vehicle Alert: {component_name}",
                    alert['message'],
                    duration=5,
                    threaded=True
                )
            except:
                # Fall back to messagebox if win10toast not available
                messagebox.showinfo(
                    f"{level_emoji} Vehicle Alert: {component_name}",
                    alert['message']
                )
        else:
            # On other platforms, use Tkinter messagebox
            messagebox.showinfo(
                f"{level_emoji} Vehicle Alert: {component_name}",
                alert['message']
            )
    
    def _save_settings(self):
        """Save user settings"""
        # Update user info
        self.client.user_info.update({
            "user_name": self.name_var.get(),
            "phone_number": self.phone_var.get(),
            "email": self.email_var.get()
        })
        
        # Update settings
        new_settings = {
            "notification_sound": self.sound_var.get(),
            "vibration": self.vibration_var.get(),
            "show_low_priority": self.show_low_var.get(),
            "auto_connect": self.auto_connect_var.get()
        }
        
        self.client.update_settings(new_settings)
        messagebox.showinfo("Settings", "Settings saved successfully")
    
    def _register_device(self):
        """Register device with the server"""
        user_info = {
            "user_name": self.name_var.get(),
            "phone_number": self.phone_var.get(),
            "email": self.email_var.get()
        }
        
        if self.client.register_device(user_info):
            messagebox.showinfo("Registration", "Device registered successfully")
        else:
            messagebox.showerror("Registration", "Failed to register device")
    
    def _unregister_device(self):
        """Unregister device from the server"""
        if messagebox.askyesno("Unregister", "Are you sure you want to unregister this device?\nYou will no longer receive alerts."):
            if self.client.unregister_device():
                messagebox.showinfo("Unregister", "Device unregistered successfully")
            else:
                messagebox.showerror("Unregister", "Failed to unregister device")


def main():
    """Main function to start the mobile app client"""
    # Create root window
    root = tk.Tk()
    
    # Create client
    client = MobileAppClient()
    
    # Create GUI
    app = MobileAppGUI(root, client)
    
    # Start main loop
    root.mainloop()


if __name__ == '__main__':
    main()