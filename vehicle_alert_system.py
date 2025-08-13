#!/usr/bin/env python3
"""
Vehicle Alert System
This module extends the Vehicle Predictive Maintenance system with
real-time alerts for drivers about potential vehicle faults.
"""

import os
import time
import json
import logging
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
import threading
# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/vehicle_alerts.log')
    ]
)
logger = logging.getLogger(__name__)

class VehicleAlertSystem:
    def __init__(self, model_dir='models', alert_config='config/alert_config.json'):
        """
        Initialize the vehicle alert system
        
        Args:
            model_dir (str): Directory containing trained models
            alert_config (str): Path to alert configuration file
        """
        self.model_dir = model_dir
        self.alert_config_path = alert_config
        self.models = {}
        self.scalers = {}
        self.alert_config = {}
        self.current_alerts = {}
        self.alert_history = []
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(alert_config), exist_ok=True)
        
        # Load models and scalers
        self._load_models()
        
        # Load or create alert configuration
        self._load_alert_config()
        
    def _load_models(self):
        """Load trained models and scalers from the model directory"""
        if not os.path.exists(self.model_dir):
            logger.error(f"Model directory {self.model_dir} not found")
            return
        
        components = ['engine', 'transmission', 'brakes', 'battery', 'electrical']
        
        for component in components:
            model_path = os.path.join(self.model_dir, f'{component}_model.joblib')
            scaler_path = os.path.join(self.model_dir, f'{component}_scaler.joblib')
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                try:
                    self.models[component] = joblib.load(model_path)
                    self.scalers[component] = joblib.load(scaler_path)
                    logger.info(f"Loaded model and scaler for {component}")
                except Exception as e:
                    logger.error(f"Error loading model for {component}: {e}")
            else:
                logger.warning(f"Model or scaler for {component} not found")
    
    def _load_alert_config(self):
        """Load alert configuration or create default if not exists"""
        if os.path.exists(self.alert_config_path):
            try:
                with open(self.alert_config_path, 'r') as f:
                    self.alert_config = json.load(f)
                logger.info(f"Loaded alert configuration from {self.alert_config_path}")
            except Exception as e:
                logger.error(f"Error loading alert configuration: {e}")
                self._create_default_alert_config()
        else:
            logger.info("Alert configuration not found, creating default")
            self._create_default_alert_config()
    
    def _create_default_alert_config(self):
        """Create default alert configuration"""
        self.alert_config = {
            "alert_thresholds": {
                "high": 0.7,  # High probability of failure (red alert)
                "medium": 0.4,  # Medium probability (orange alert)
                "low": 0.2     # Low probability (yellow alert)
            },
            "notification_settings": {
                "display_alerts": True,
                "enable_sound": True,
                "enable_mobile_notifications": False,
                "snooze_duration_minutes": 60
            },
            "component_priorities": {
                "engine": 5,       # Highest priority
                "brakes": 5,
                "transmission": 4,
                "electrical": 3,
                "battery": 2
            }
        }
        
        # Save default configuration
        try:
            with open(self.alert_config_path, 'w') as f:
                json.dump(self.alert_config, indent=4, fp=f)
            logger.info(f"Created default alert configuration at {self.alert_config_path}")
        except Exception as e:
            logger.error(f"Error saving default alert configuration: {e}")
    
    def process_telemetry_data(self, telemetry_data):
        """
        Process current vehicle telemetry data and generate alerts if needed
        
        Args:
            telemetry_data (dict): Dictionary with component names as keys and 
                                   feature dictionaries as values
        
        Returns:
            list: List of current alerts
        """
        current_time = datetime.now()
        alerts = []
        
        for component, data in telemetry_data.items():
            if component not in self.models or component not in self.scalers:
                logger.warning(f"No model available for component: {component}")
                continue
            
            try:
                # Convert data to DataFrame
                df = pd.DataFrame([data])
                
                # Scale features
                features_scaled = self.scalers[component].transform(df)
                
                # Predict failure probability
                failure_prob = self.models[component].predict_proba(features_scaled)[0, 1]
                
                # Determine alert level
                alert_level = self._determine_alert_level(failure_prob)
                
                # Create alert if probability exceeds threshold
                if alert_level:
                    alert = {
                        'component': component,
                        'probability': failure_prob,
                        'alert_level': alert_level,
                        'priority': self.alert_config['component_priorities'].get(component, 1),
                        'timestamp': current_time,
                        'message': self._generate_alert_message(component, alert_level, failure_prob)
                    }
                    
                    # Add to current alerts and history
                    self.current_alerts[component] = alert
                    self.alert_history.append(alert)
                    alerts.append(alert)
                    
                    logger.info(f"Alert generated: {component} - {alert_level} - {failure_prob:.2f}")
                elif component in self.current_alerts:
                    # Remove from current alerts if below threshold
                    del self.current_alerts[component]
            
            except Exception as e:
                logger.error(f"Error processing telemetry for {component}: {e}")
        
        return sorted(alerts, key=lambda x: (-x['priority'], -x['probability']))
    
    def _determine_alert_level(self, probability):
        """
        Determine alert level based on failure probability
        
        Args:
            probability (float): Failure probability
        
        Returns:
            str: Alert level or None if below threshold
        """
        thresholds = self.alert_config['alert_thresholds']
        
        if probability >= thresholds['high']:
            return 'high'
        elif probability >= thresholds['medium']:
            return 'medium'
        elif probability >= thresholds['low']:
            return 'low'
        return None
    
    def _generate_alert_message(self, component, level, probability):
        """
        Generate human-readable alert message
        
        Args:
            component (str): Vehicle component name
            level (str): Alert level (high, medium, low)
            probability (float): Failure probability
        
        Returns:
            str: Alert message
        """
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
    
    def get_current_alerts(self):
        """
        Get current active alerts
        
        Returns:
            list: List of current active alerts sorted by priority and probability
        """
        alerts = list(self.current_alerts.values())
        return sorted(alerts, key=lambda x: (-x['priority'], -x['probability']))
    
    def snooze_alert(self, component):
        """
        Snooze alert for a specific component
        
        Args:
            component (str): Component name to snooze alert for
            
        Returns:
            bool: True if alert was snoozed, False otherwise
        """
        if component in self.current_alerts:
            # Mark alert as snoozed for the configured duration
            snooze_minutes = self.alert_config['notification_settings']['snooze_duration_minutes']
            self.current_alerts[component]['snoozed_until'] = datetime.now() + timedelta(minutes=snooze_minutes)
            logger.info(f"Snoozed alert for {component} for {snooze_minutes} minutes")
            return True
        return False
    
    def get_alert_history(self, days=7):
        """
        Get alert history for the specified number of days
        
        Args:
            days (int): Number of days to retrieve history for
            
        Returns:
            list: List of historical alerts
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        return [alert for alert in self.alert_history 
                if alert['timestamp'] > cutoff_time]
    
    def update_alert_config(self, new_config):
        """
        Update alert configuration
        
        Args:
            new_config (dict): New configuration dictionary
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            # Update configuration
            self.alert_config.update(new_config)
            
            # Save to file
            with open(self.alert_config_path, 'w') as f:
                json.dump(self.alert_config, indent=4, fp=f)
                
            logger.info("Alert configuration updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating alert configuration: {e}")
            return False


class DriverAlertInterface:
    """
    Driver alert interface to display alerts to the driver
    This is a simplified version that would be replaced by a real UI in a production system
    """
    def __init__(self, alert_system):
        """
        Initialize the driver alert interface
        
        Args:
            alert_system (VehicleAlertSystem): Vehicle alert system instance
        """
        self.alert_system = alert_system
        self.running = False
        self.monitoring_thread = None
        
        # Alert display settings
        self.colors = {
            'high': '\033[91m',    # Red
            'medium': '\033[93m',  # Yellow
            'low': '\033[94m',     # Blue
            'reset': '\033[0m'     # Reset
        }
    
    def start_monitoring(self, telemetry_source, interval=1.0):
        """
        Start monitoring telemetry data and displaying alerts
        
        Args:
            telemetry_source: Function or object that provides telemetry data
            interval (float): Update interval in seconds
        """
        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(telemetry_source, interval)
        )
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logger.info("Driver alert monitoring started")
        
    def stop_monitoring(self):
        """Stop monitoring telemetry data"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        logger.info("Driver alert monitoring stopped")
    
    def _monitoring_loop(self, telemetry_source, interval):
        """
        Main monitoring loop
        
        Args:
            telemetry_source: Function or object that provides telemetry data
            interval (float): Update interval in seconds
        """
        while self.running:
            try:
                # Get telemetry data
                telemetry_data = telemetry_source()
                
                # Process telemetry and get alerts
                alerts = self.alert_system.process_telemetry_data(telemetry_data)
                
                # Display alerts if any
                if alerts and self.alert_system.alert_config['notification_settings']['display_alerts']:
                    self._display_alerts(alerts)
                
                # Sleep for the specified interval
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _display_alerts(self, alerts):
        """
        Display alerts to the driver
        
        Args:
            alerts (list): List of alert dictionaries
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n===== VEHICLE HEALTH ALERTS =====\n")
        
        for alert in alerts:
            level = alert['alert_level']
            color = self.colors.get(level, self.colors['reset'])
            
            print(f"{color}[{level.upper()}] {alert['message']}{self.colors['reset']}")
            print(f"Component: {alert['component']}, Risk: {alert['probability']:.1%}")
            print("-" * 50)
        
        print("\nPress 'S' + component name to snooze an alert (e.g., 'S engine')")
        print("Press 'Q' to quit")
    
    def handle_user_input(self, user_input):
        """
        Handle user input for alert interactions
        
        Args:
            user_input (str): User input string
            
        Returns:
            bool: True to continue, False to exit
        """
        if not user_input:
            return True
            
        cmd = user_input.strip().lower()
        
        if cmd == 'q':
            return False
        elif cmd.startswith('s '):
            # Snooze alert
            component = cmd[2:].strip()
            if self.alert_system.snooze_alert(component):
                print(f"Alert for {component} snoozed")
            else:
                print(f"No active alert for {component}")
        
        return True


# Example telemetry data provider for testing
class MockTelemetryProvider:
    """Mock telemetry provider for testing the alert system"""
    def __init__(self, failure_probability=0.3):
        """
        Initialize mock telemetry provider
        
        Args:
            failure_probability (float): Base probability of generating failure conditions
        """
        self.failure_probability = failure_probability
        
    def get_telemetry(self):
        """
        Get mock telemetry data for all vehicle components
        
        Returns:
            dict: Mock telemetry data
        """
        # Randomize failure probability slightly for variability
        actual_probability = self.failure_probability * np.random.uniform(0.5, 1.5)
        
        telemetry = {
            'engine': self._generate_engine_telemetry(actual_probability),
            'transmission': self._generate_transmission_telemetry(actual_probability),
            'brakes': self._generate_brakes_telemetry(actual_probability),
            'battery': self._generate_battery_telemetry(actual_probability),
            'electrical': self._generate_electrical_telemetry(actual_probability)
        }
        
        return telemetry
    
    def _generate_engine_telemetry(self, failure_prob):
        """Generate mock engine telemetry data"""
        # Normal values
        data = {
            'temperature': np.random.normal(90, 5),
            'rpm': np.random.normal(2500, 200),
            'oil_pressure': np.random.normal(50, 3),
            'vibration': np.abs(np.random.normal(0.05, 0.01))
        }
        
        # Introduce failure condition based on probability
        if np.random.random() < failure_prob:
            data['temperature'] += np.random.normal(15, 5)
            data['rpm'] += np.random.normal(300, 100)
            data['oil_pressure'] -= np.random.normal(10, 3)
            data['vibration'] *= 2.5
        
        return data
    
    def _generate_transmission_telemetry(self, failure_prob):
        """Generate mock transmission telemetry data"""
        # Normal values
        data = {
            'gear_shifts': np.random.normal(50, 5),
            'transmission_temp': np.random.normal(85, 5),
            'fluid_level': np.random.normal(7, 0.2),
            'gear_ratio_variance': np.abs(np.random.normal(0.02, 0.005))
        }
        
        # Introduce failure condition based on probability
        if np.random.random() < failure_prob:
            data['transmission_temp'] += np.random.normal(20, 5)
            data['gear_shifts'] += np.random.normal(15, 5)
            data['fluid_level'] -= np.random.normal(1.5, 0.5)
            data['gear_ratio_variance'] *= 4
        
        return data
    
    def _generate_brakes_telemetry(self, failure_prob):
        """Generate mock brake system telemetry data"""
        # Normal values
        data = {
            'pad_wear': np.random.normal(10, 1),
            'rotor_thickness': np.random.normal(25, 1),
            'brake_fluid_level': np.random.normal(80, 3),
            'brake_temperature': np.random.normal(100, 10)
        }
        
        # Introduce failure condition based on probability
        if np.random.random() < failure_prob:
            data['pad_wear'] += np.random.normal(4, 1)
            data['rotor_thickness'] -= np.random.normal(2, 0.5)
            data['brake_fluid_level'] -= np.random.normal(15, 5)
            data['brake_temperature'] += np.random.normal(40, 10)
        
        return data
    
    def _generate_battery_telemetry(self, failure_prob):
        """Generate mock battery telemetry data"""
        # Normal values
        data = {
            'voltage': np.random.normal(12.6, 0.2),
            'current': np.random.normal(10, 1),
            'temperature': np.random.normal(25, 3),
            'charge_cycles': np.random.normal(500, 50)
        }
        
        # Introduce failure condition based on probability
        if np.random.random() < failure_prob:
            data['voltage'] -= np.random.normal(0.8, 0.2)
            data['current'] += np.random.normal(3, 1)
            data['temperature'] += np.random.normal(15, 5)
            data['charge_cycles'] += np.random.normal(150, 50)
        
        return data
    
    def _generate_electrical_telemetry(self, failure_prob):
        """Generate mock electrical system telemetry data"""
        # Normal values
        data = {
            'alternator_voltage': np.random.normal(14.2, 0.2),
            'wire_resistance': np.random.normal(0.1, 0.01),
            'ground_connection': np.random.normal(0.05, 0.005),
            'electrical_noise': np.random.normal(0.1, 0.02)
        }
        
        # Introduce failure condition based on probability
        if np.random.random() < failure_prob:
            data['alternator_voltage'] -= np.random.normal(1.5, 0.5)
            data['wire_resistance'] += np.random.normal(0.08, 0.02)
            data['ground_connection'] += np.random.normal(0.08, 0.02)
            data['electrical_noise'] *= 4
        
        return data


# Main function to demonstrate the alert system
def main():
    """Main function to run the vehicle alert system demonstration"""
    print("Starting Vehicle Alert System...")
    
    # Initialize alert system
    alert_system = VehicleAlertSystem()
    
    # Initialize driver interface
    driver_interface = DriverAlertInterface(alert_system)
    
    # Initialize mock telemetry provider
    telemetry_provider = MockTelemetryProvider(failure_probability=0.4)
    
    try:
        # Start monitoring with mock telemetry
        driver_interface.start_monitoring(
            telemetry_source=telemetry_provider.get_telemetry,
            interval=2.0  # Update every 2 seconds
        )
        
        # Main input loop
        while True:
            user_input = input()
            if not driver_interface.handle_user_input(user_input):
                break
    
    except KeyboardInterrupt:
        print("\nExiting Vehicle Alert System...")
    finally:
        driver_interface.stop_monitoring()


if __name__ == '__main__':
    main()