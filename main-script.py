#!/usr/bin/env python3
"""
Vehicle Predictive Maintenance System with Mobile Alerts
Main script that integrates all components of the system.
"""

import os
import time
import logging
import threading
import argparse
from datetime import datetime

# Import components
from vehicle_predictive_maintenance import VehiclePredictiveMaintenance
from vehicle_synthetic_data import VehicleSyntheticDataGenerator, generate_synthetic_datasets
from vehicle_alert_system import VehicleAlertSystem, MockTelemetryProvider, DriverAlertInterface
from mobile_alert_system import MobileAlertSystem, MobileAppIntegration

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/vehicle_system.log')
    ]
)
logger = logging.getLogger(__name__)

class VehicleMonitoringSystem:
    """
    Main class that integrates all components of the vehicle predictive maintenance system
    """
    def __init__(self, data_dir='data/raw', model_dir='models', config_dir='config', 
                 use_synthetic_data=True, use_mobile_alerts=True):
        """
        Initialize the vehicle monitoring system
        
        Args:
            data_dir (str): Directory containing telemetry data
            model_dir (str): Directory to save trained models
            config_dir (str): Directory for configuration files
            use_synthetic_data (bool): Whether to use synthetic data generator
            use_mobile_alerts (bool): Whether to enable mobile alerts
        """
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.config_dir = config_dir
        self.use_synthetic_data = use_synthetic_data
        self.use_mobile_alerts = use_mobile_alerts
        
        # Create directories
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(config_dir, exist_ok=True)
        
        # Initialize components
        self.predictive_maintenance = None
        self.alert_system = None
        self.driver_interface = None
        self.mobile_alert_system = None
        self.mobile_app_integration = None
        self.telemetry_provider = None
        
        # Runtime state
        self.running = False
        self.model_training_complete = False
        self.monitoring_thread = None
    
    def initialize_components(self):
        """Initialize all system components"""
        logger.info("Initializing system components...")
        
        # If using synthetic data and no data files exist, generate them
        if self.use_synthetic_data and not any(f.endswith('.csv') for f in os.listdir(self.data_dir)):
            logger.info("Generating synthetic telemetry data...")
            generate_synthetic_datasets(output_dir=self.data_dir)
        
        # Initialize predictive maintenance system
        self.predictive_maintenance = VehiclePredictiveMaintenance(
            data_dir=self.data_dir,
            model_dir=self.model_dir
        )
        
        # Initialize alert system
        self.alert_system = VehicleAlertSystem(model_dir=self.model_dir)
        
        # Initialize driver interface
        self.driver_interface = DriverAlertInterface(self.alert_system)
        
        # Initialize telemetry provider
        if self.use_synthetic_data:
            self.telemetry_provider = MockTelemetryProvider(failure_probability=0.3)
        else:
            # In a real implementation, you would use a real telemetry provider here
            self.telemetry_provider = MockTelemetryProvider(failure_probability=0.3)
        
        # Initialize mobile alert system if enabled
        if self.use_mobile_alerts:
            self.mobile_alert_system = MobileAlertSystem(self.alert_system)
            self.mobile_app_integration = MobileAppIntegration(self.mobile_alert_system)
            
            # Register a test device
            self.mobile_app_integration.mock_app_registration()
        
        logger.info("All components initialized successfully")
    
    def train_models(self):
        """Train predictive maintenance models"""
        logger.info("Starting model training...")
        
        # Run the predictive maintenance pipeline
        self.predictive_maintenance.run_predictive_maintenance_pipeline()
        
        self.model_training_complete = True
        logger.info("Model training completed")
    
    def start_monitoring(self):
        """Start vehicle monitoring"""
        if self.running:
            logger.warning("Monitoring is already running")
            return
            
        if not self.model_training_complete:
            logger.warning("Models not trained yet, training now...")
            self.train_models()
        
        logger.info("Starting vehicle monitoring...")
        self.running = True
        
        # Start driver interface
        self.driver_interface.start_monitoring(
            telemetry_source=self.telemetry_provider.get_telemetry,
            interval=2.0
        )
        
        # Start mobile alerts if enabled
        if self.use_mobile_alerts and self.mobile_alert_system:
            self.mobile_alert_system.start_monitoring(interval=5.0)
            logger.info("Mobile alert system monitoring started")
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("Vehicle monitoring started")
    
    def stop_monitoring(self):
        """Stop vehicle monitoring"""
        if not self.running:
            logger.warning("Monitoring is not running")
            return
            
        logger.info("Stopping vehicle monitoring...")
        self.running = False
        
        # Stop driver interface
        self.driver_interface.stop_monitoring()
        
        # Stop mobile alerts if enabled
        if self.use_mobile_alerts and self.mobile_alert_system:
            self.mobile_alert_system.stop_monitoring()
        
        # Wait for monitoring thread to stop
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        logger.info("Vehicle monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # In a real system, this would perform additional functions
                # like sending telemetry data to a cloud service
                
                # Sleep for a short period
                time.sleep(5.0)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)
    
    def run_server(self, port=5000):
        """
        Run a web server for mobile app connections
        In a real implementation, this would be a proper web server
        
        Args:
            port (int): Port to run the server on
        """
        if not self.use_mobile_alerts or not self.mobile_app_integration:
            logger.warning("Mobile alerts not enabled, cannot run server")
            return
            
        logger.info(f"Starting mobile app integration server on port {port}...")
        
        # This is just a placeholder for a real implementation
        self.mobile_app_integration.start_rest_api()
        
        logger.info("Mobile app integration server started")


def main():
    """Main function to run the vehicle monitoring system"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Vehicle Predictive Maintenance System')
    parser.add_argument('--data-dir', default='data/raw', help='Directory for telemetry data')
    parser.add_argument('--model-dir', default='models', help='Directory for trained models')
    parser.add_argument('--config-dir', default='config', help='Directory for configuration files')
    parser.add_argument('--no-synthetic', action='store_true', help='Disable synthetic data generation')
    parser.add_argument('--no-mobile', action='store_true', help='Disable mobile alerts')
    parser.add_argument('--train-only', action='store_true', help='Train models and exit')
    parser.add_argument('--server-port', type=int, default=5000, help='Port for mobile app server')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Vehicle Predictive Maintenance System")
    print("=" * 50)
    
    # Initialize system
    system = VehicleMonitoringSystem(
        data_dir=args.data_dir,
        model_dir=args.model_dir,
        config_dir=args.config_dir,
        use_synthetic_data=not args.no_synthetic,
        use_mobile_alerts=not args.no_mobile
    )
    
    try:
        # Initialize components
        system.initialize_components()
        
        # Train models
        system.train_models()
        
        # Exit if train-only
        if args.train_only:
            print("Model training completed. Exiting.")
            return
        
        # Start monitoring
        system.start_monitoring()
        
        # Start server if mobile alerts enabled
        if not args.no_mobile:
            system.run_server(port=args.server_port)
        
        print("\nSystem is now running. Press Ctrl+C to exit.")
        
        # Main loop
        while True:
            cmd = input().strip().lower()
            
            if cmd == 'q' or cmd == 'quit' or cmd == 'exit':
                break
            elif cmd == 'status':
                print(f"System status: {'Running' if system.running else 'Stopped'}")
            elif cmd == 'help':
                print("Available commands:")
                print("  status - Show system status")
                print("  quit   - Exit the application")
                print("  help   - Show this help message")
    
    except KeyboardInterrupt:
        print("\nExiting Vehicle Monitoring System...")
    finally:
        # Stop monitoring
        system.stop_monitoring()
        print("System stopped.")


if __name__ == '__main__':
    main()