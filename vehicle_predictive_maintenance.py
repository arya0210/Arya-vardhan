#!/usr/bin/env python3
"""
Vehicle Predictive Maintenance ML Pipeline
This script integrates machine learning for predictive maintenance 
and includes a notification system for vehicle damage alerts.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Add console output
        logging.FileHandler('predictive_maintenance.log')  # Log to file
    ]
)
logger = logging.getLogger(__name__)

class VehiclePredictiveMaintenance:
    def __init__(self, data_dir='data/raw', model_dir='models'):
        """
        Initialize the predictive maintenance system
        
        Args:
            data_dir (str): Directory containing raw telemetry data
            model_dir (str): Directory to save trained models
        """
        self.data_dir = data_dir
        self.model_dir = model_dir
        
        # Create directories if they don't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(model_dir, exist_ok=True)
        
        print(f"Data directory: {os.path.abspath(data_dir)}")
        print(f"Model directory: {os.path.abspath(model_dir)}")
    
    def load_and_preprocess_data(self):
        """
        Load and preprocess telemetry data from CSV files
        
        Returns:
            dict: Preprocessed datasets for each vehicle component
        """
        preprocessed_data = {}
        
        # List of telemetry files
        telemetry_files = [
            'engine_telemetry.csv',
            'transmission_telemetry.csv', 
            'brakes_telemetry.csv',
            'battery_telemetry.csv',
            'electrical_telemetry.csv'
        ]
        
        # Check if data directory exists and has files
        if not os.path.exists(self.data_dir):
            print(f"ERROR: Data directory {self.data_dir} does not exist!")
            return preprocessed_data
        
        available_files = os.listdir(self.data_dir)
        print(f"Files in data directory: {available_files}")
        
        for filename in telemetry_files:
            filepath = os.path.join(self.data_dir, filename)
            
            try:
                # Check if file exists
                if filename not in available_files:
                    print(f"WARNING: {filename} not found in data directory!")
                    continue
                
                # Read CSV file
                print(f"Reading file: {filepath}")
                df = pd.read_csv(filepath)
                print(f"Loaded {filename} with {len(df)} rows")
                
                # Identify failure column
                failure_column = [col for col in df.columns if col.endswith('_failure')]
                if not failure_column:
                    print(f"WARNING: No failure column found in {filename}")
                    continue
                failure_column = failure_column[0]
                
                # Select features (exclude timestamp and failure column)
                feature_columns = [col for col in df.columns 
                                   if col not in ['timestamp', failure_column]]
                
                # Prepare features and target
                X = df[feature_columns]
                y = df[failure_column]
                
                # Scale features
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Store preprocessed data
                preprocessed_data[filename] = {
                    'X': X_scaled,
                    'y': y,
                    'feature_names': feature_columns,
                    'scaler': scaler
                }
                
                logger.info(f"Preprocessed {filename}")
                print(f"Preprocessed {filename} successfully")
            
            except Exception as e:
                print(f"ERROR processing {filename}: {e}")
                logger.error(f"Error processing {filename}: {e}")
        
        return preprocessed_data
    
    def train_predictive_models(self, preprocessed_data):
        """
        Train machine learning models for each vehicle component
        
        Args:
            preprocessed_data (dict): Preprocessed telemetry datasets
        
        Returns:
            dict: Trained models for each vehicle component
        """
        trained_models = {}
        
        if not preprocessed_data:
            print("No preprocessed data available for model training!")
            return trained_models
        
        for filename, data in preprocessed_data.items():
            try:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    data['X'], data['y'], test_size=0.2, random_state=42
                )
                
                # Train Random Forest Classifier
                print(f"Training model for {filename}")
                model = RandomForestClassifier(
                    n_estimators=100, 
                    random_state=42, 
                    class_weight='balanced'
                )
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                print(f"Classification Report for {filename}:")
                print(classification_report(y_test, y_pred))
                
                # Save model and scaler
                component_name = filename.replace('_telemetry.csv', '')
                model_path = os.path.join(
                    self.model_dir, f'{component_name}_model.joblib'
                )
                scaler_path = os.path.join(
                    self.model_dir, f'{component_name}_scaler.joblib'
                )
                
                joblib.dump(model, model_path)
                joblib.dump(data['scaler'], scaler_path)
                
                trained_models[filename] = {
                    'model': model,
                    'feature_names': data['feature_names']
                }
                
                print(f"Saved model and scaler for {filename}")
                logger.info(f"Saved model and scaler for {filename}")
            
            except Exception as e:
                print(f"ERROR training model for {filename}: {e}")
                logger.error(f"Error training model for {filename}: {e}")
        
        return trained_models
    
    def run_predictive_maintenance_pipeline(self):
        """
        Run the complete predictive maintenance pipeline
        """
        print("Starting Predictive Maintenance Pipeline...")
        
        # Step 1: Preprocess data
        preprocessed_data = self.load_and_preprocess_data()
        
        # Check if we have preprocessed data
        if not preprocessed_data:
            print("No data could be preprocessed. Exiting.")
            return
        
        # Step 2: Train models
        trained_models = self.train_predictive_models(preprocessed_data)
        
        # Check if models were trained
        if not trained_models:
            print("No models could be trained. Exiting.")
            return
        
        print("Predictive Maintenance Pipeline Completed Successfully")
        logger.info("Predictive Maintenance Pipeline Completed Successfully")

def main():
    # Initialize and run predictive maintenance system
    maintenance_system = VehiclePredictiveMaintenance()
    maintenance_system.run_predictive_maintenance_pipeline()

if __name__ == '__main__':
    main()