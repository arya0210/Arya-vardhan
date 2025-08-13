#!/usr/bin/env python3
"""
Synthetic Data Generator for Vehicle Predictive Maintenance
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class VehicleSyntheticDataGenerator:
    def __init__(self, num_samples=1000, random_seed=42):
        """
        Initialize synthetic data generator
        
        Args:
            num_samples (int): Number of samples to generate
            random_seed (int): Random seed for reproducibility
        """
        np.random.seed(random_seed)
        self.num_samples = num_samples
        self.timestamp = self._generate_timestamps()
    
    def _generate_timestamps(self):
        """
        Generate sequential timestamps
        
        Returns:
            numpy.ndarray: Array of timestamps
        """
        start = datetime(2023, 1, 1)
        return [start + timedelta(minutes=10*i) for i in range(self.num_samples)]
    
    def generate_engine_data(self):
        """
        Generate synthetic engine telemetry data
        
        Returns:
            pandas.DataFrame: Engine telemetry dataset
        """
        # Normal vs Failure distribution
        failure_prob = 0.1  # 10% chance of failure
        
        # Generate features
        temperature = np.random.normal(90, 10, self.num_samples)
        rpm = np.random.normal(2500, 500, self.num_samples)
        oil_pressure = np.random.normal(50, 5, self.num_samples)
        vibration = np.abs(np.random.normal(0.05, 0.02, self.num_samples))
        
        # Introduce failure conditions
        engine_failure = np.random.choice([0, 1], self.num_samples, p=[1-failure_prob, failure_prob])
        
        # Modify features for failure cases
        temperature[engine_failure == 1] += np.random.normal(20, 5, sum(engine_failure))
        rpm[engine_failure == 1] += np.random.normal(500, 100, sum(engine_failure))
        oil_pressure[engine_failure == 1] -= np.random.normal(10, 3, sum(engine_failure))
        vibration[engine_failure == 1] *= 3
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': self.timestamp,
            'temperature': temperature,
            'rpm': rpm,
            'oil_pressure': oil_pressure,
            'vibration': vibration,
            'engine_failure': engine_failure
        })
        
        return df
    
    def generate_transmission_data(self):
        """
        Generate synthetic transmission telemetry data
        
        Returns:
            pandas.DataFrame: Transmission telemetry dataset
        """
        # Normal vs Failure distribution
        failure_prob = 0.08  # 8% chance of failure
        
        # Generate features
        gear_shifts = np.random.normal(50, 10, self.num_samples)
        transmission_temp = np.random.normal(85, 10, self.num_samples)
        fluid_level = np.random.normal(7, 0.5, self.num_samples)
        gear_ratio_variance = np.abs(np.random.normal(0.02, 0.01, self.num_samples))
        
        # Introduce failure conditions
        transmission_failure = np.random.choice([0, 1], self.num_samples, p=[1-failure_prob, failure_prob])
        
        # Modify features for failure cases
        transmission_temp[transmission_failure == 1] += np.random.normal(30, 5, sum(transmission_failure))
        gear_shifts[transmission_failure == 1] += np.random.normal(20, 10, sum(transmission_failure))
        fluid_level[transmission_failure == 1] -= np.random.normal(2, 0.5, sum(transmission_failure))
        gear_ratio_variance[transmission_failure == 1] *= 5
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': self.timestamp,
            'gear_shifts': gear_shifts,
            'transmission_temp': transmission_temp,
            'fluid_level': fluid_level,
            'gear_ratio_variance': gear_ratio_variance,
            'transmission_failure': transmission_failure
        })
        
        return df
    
    def generate_brakes_data(self):
        """
        Generate synthetic brake system telemetry data
        
        Returns:
            pandas.DataFrame: Brake system telemetry dataset
        """
        # Normal vs Failure distribution
        failure_prob = 0.06  # 6% chance of failure
        
        # Generate features
        pad_wear = np.random.normal(10, 2, self.num_samples)
        rotor_thickness = np.random.normal(25, 2, self.num_samples)
        brake_fluid_level = np.random.normal(80, 5, self.num_samples)
        brake_temperature = np.random.normal(100, 20, self.num_samples)
        
        # Introduce failure conditions
        brakes_failure = np.random.choice([0, 1], self.num_samples, p=[1-failure_prob, failure_prob])
        
        # Modify features for failure cases
        pad_wear[brakes_failure == 1] += np.random.normal(5, 2, sum(brakes_failure))
        rotor_thickness[brakes_failure == 1] -= np.random.normal(3, 1, sum(brakes_failure))
        brake_fluid_level[brakes_failure == 1] -= np.random.normal(20, 5, sum(brakes_failure))
        brake_temperature[brakes_failure == 1] += np.random.normal(50, 10, sum(brakes_failure))
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': self.timestamp,
            'pad_wear': pad_wear,
            'rotor_thickness': rotor_thickness,
            'brake_fluid_level': brake_fluid_level,
            'brake_temperature': brake_temperature,
            'brakes_failure': brakes_failure
        })
        
        return df
    
    def generate_battery_data(self):
        """
        Generate synthetic battery telemetry data
        
        Returns:
            pandas.DataFrame: Battery telemetry dataset
        """
        # Normal vs Failure distribution
        failure_prob = 0.07  # 7% chance of failure
        
        # Generate features
        voltage = np.random.normal(12.6, 0.5, self.num_samples)
        current = np.random.normal(10, 2, self.num_samples)
        temperature = np.random.normal(25, 5, self.num_samples)
        charge_cycles = np.random.normal(500, 100, self.num_samples)
        
        # Introduce failure conditions
        battery_failure = np.random.choice([0, 1], self.num_samples, p=[1-failure_prob, failure_prob])
        
        # Modify features for failure cases
        voltage[battery_failure == 1] -= np.random.normal(1, 0.3, sum(battery_failure))
        current[battery_failure == 1] += np.random.normal(5, 2, sum(battery_failure))
        temperature[battery_failure == 1] += np.random.normal(20, 5, sum(battery_failure))
        charge_cycles[battery_failure == 1] += np.random.normal(200, 50, sum(battery_failure))
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': self.timestamp,
            'voltage': voltage,
            'current': current,
            'temperature': temperature,
            'charge_cycles': charge_cycles,
            'battery_failure': battery_failure
        })
        
        return df
    
    def generate_electrical_data(self):
        """
        Generate synthetic electrical system telemetry data
        
        Returns:
            pandas.DataFrame: Electrical system telemetry dataset
        """
        # Normal vs Failure distribution
        failure_prob = 0.05  # 5% chance of failure
        
        # Generate features
        alternator_voltage = np.random.normal(14.2, 0.5, self.num_samples)
        wire_resistance = np.random.normal(0.1, 0.02, self.num_samples)
        ground_connection = np.random.normal(0.05, 0.01, self.num_samples)
        electrical_noise = np.random.normal(0.1, 0.05, self.num_samples)
        
        # Introduce failure conditions
        electrical_failure = np.random.choice([0, 1], self.num_samples, p=[1-failure_prob, failure_prob])
        
        # Modify features for failure cases
        alternator_voltage[electrical_failure == 1] -= np.random.normal(2, 0.5, sum(electrical_failure))
        wire_resistance[electrical_failure == 1] += np.random.normal(0.1, 0.05, sum(electrical_failure))
        ground_connection[electrical_failure == 1] += np.random.normal(0.1, 0.05, sum(electrical_failure))
        electrical_noise[electrical_failure == 1] *= 5
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': self.timestamp,
            'alternator_voltage': alternator_voltage,
            'wire_resistance': wire_resistance,
            'ground_connection': ground_connection,
            'electrical_noise': electrical_noise,
            'electrical_failure': electrical_failure
        })
        
        return df

def generate_synthetic_datasets(output_dir='data/raw', num_samples=1000):
    """
    Generate synthetic datasets for all vehicle components
    
    Args:
        output_dir (str): Directory to save generated datasets
        num_samples (int): Number of samples to generate
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize generator
    generator = VehicleSyntheticDataGenerator(num_samples=num_samples)
    
    # Generate and save datasets
    datasets = {
        'engine_telemetry.csv': generator.generate_engine_data(),
        'transmission_telemetry.csv': generator.generate_transmission_data(),
        'brakes_telemetry.csv': generator.generate_brakes_data(),
        'battery_telemetry.csv': generator.generate_battery_data(),
        'electrical_telemetry.csv': generator.generate_electrical_data()
    }
    
    # Save datasets
    for filename, dataset in datasets.items():
        filepath = os.path.join(output_dir, filename)
        dataset.to_csv(filepath, index=False)
        print(f"Generated {filename} with {len(dataset)} samples")

def main():
    generate_synthetic_datasets()

if __name__ == '__main__':
    main()