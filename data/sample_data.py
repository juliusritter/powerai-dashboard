import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(n_samples=100):
    """Generate sample equipment data for demonstration"""
    np.random.seed(42)
    
    # Generate random dates
    current_date = datetime.now()
    
    # Create sample data
    data = {
        'product_id': [f'EQ{i:03d}' for i in range(n_samples)],
        'product_name': np.random.choice(
            ['Transformer', 'Power Pole', 'Switch Gear', 'Circuit Breaker'],
            n_samples
        ),
        'latitude': np.random.uniform(37.7, 37.9, n_samples),  # San Francisco area
        'longitude': np.random.uniform(-122.5, -122.4, n_samples),
        'installation_date': [
            current_date - timedelta(days=np.random.randint(365, 3650))
            for _ in range(n_samples)
        ],
        'last_maintenance_date': [
            current_date - timedelta(days=np.random.randint(0, 365))
            for _ in range(n_samples)
        ],
        'temperature': np.random.uniform(60, 90, n_samples),
        'precipitation_forecast': np.random.uniform(0, 50, n_samples),
        'vegetation_proximity': np.random.choice([True, False], n_samples),
        'customer_impact': np.random.randint(50, 1000, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Calculate age and days since maintenance
    df['age'] = (current_date - df['installation_date']).dt.days / 365
    df['days_since_maintenance'] = (current_date - df['last_maintenance_date']).dt.days
    
    # Calculate risk score
    df['risk_score'] = (
        df['age'] / 20 * 0.3 +
        df['days_since_maintenance'] / 365 * 0.25 +
        (df['temperature'] - 70) ** 2 / 1000 * 0.2 +
        df['vegetation_proximity'].astype(int) * 0.15 +
        df['customer_impact'] / 1000 * 0.1
    ).clip(0, 1)
    
    return df
