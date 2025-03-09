import numpy as np
from datetime import datetime
from utils.weather_utils import calculate_weather_risk_factor

def calculate_risk_score(equipment, weather_data=None):
    """
    Calculate risk score based on various factors including weather
    Returns a value between 0 and 1
    """
    try:
        # Weight factors
        age_weight = 0.25
        maintenance_weight = 0.20
        weather_weight = 0.25
        vegetation_weight = 0.15
        customer_weight = 0.15

        # Age score (0-1)
        age_score = min(equipment['age'] / 20, 1)  # Assume 20 years is maximum age

        # Maintenance score (0-1)
        maintenance_score = min(equipment['days_since_maintenance'] / 365, 1)

        # Weather score (0-1)
        if weather_data:
            weather_score = calculate_weather_risk_factor(weather_data)
        else:
            weather_score = min(
                (equipment['temperature'] - 70) ** 2 / 1000 +
                equipment['precipitation_forecast'] / 100,
                1
            )

        # Vegetation score (0-1)
        vegetation_score = 1 if equipment['vegetation_proximity'] else 0

        # Customer impact score (0-1)
        customer_score = min(equipment['customer_impact'] / 1000, 1)

        # Calculate weighted risk score
        risk_score = (
            age_score * age_weight +
            maintenance_score * maintenance_weight +
            weather_score * weather_weight +
            vegetation_score * vegetation_weight +
            customer_score * customer_weight
        )

        return min(max(risk_score, 0), 1)

    except Exception as e:
        print(f"Error calculating risk score: {str(e)}")
        return 0.5  # Default to medium risk on error

def get_risk_level(risk_score):
    """Convert risk score to risk level"""
    if risk_score < 0.3:
        return "Low"
    elif risk_score < 0.5:
        return "Medium"
    elif risk_score < 0.7:
        return "High"
    else:
        return "Critical"