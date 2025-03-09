import pandas as pd
from datetime import datetime, timedelta

def load_and_process_data(data):
    """Process and validate equipment data"""
    try:
        # Ensure required columns exist
        required_columns = [
            'product_id', 'product_name', 'latitude', 'longitude',
            'installation_date', 'last_maintenance_date', 'temperature',
            'precipitation_forecast', 'vegetation_proximity', 'customer_impact'
        ]
        
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Convert dates to datetime
        data['installation_date'] = pd.to_datetime(data['installation_date'])
        data['last_maintenance_date'] = pd.to_datetime(data['last_maintenance_date'])
        
        # Calculate equipment age in years
        data['age'] = (datetime.now() - data['installation_date']).dt.days / 365
        
        # Calculate days since last maintenance
        data['days_since_maintenance'] = (datetime.now() - data['last_maintenance_date']).dt.days
        
        return data
        
    except Exception as e:
        raise Exception(f"Error processing data: {str(e)}")

def validate_equipment_data(equipment):
    """Validate single equipment entry"""
    if not isinstance(equipment, pd.Series):
        raise ValueError("Equipment data must be a pandas Series")
        
    required_fields = [
        'product_id', 'product_name', 'installation_date',
        'last_maintenance_date', 'customer_impact'
    ]
    
    for field in required_fields:
        if field not in equipment:
            raise ValueError(f"Missing required field: {field}")
            
    return True
