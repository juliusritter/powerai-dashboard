import requests
from datetime import datetime
import json

def fetch_noaa_weather(latitude, longitude):
    """
    Fetch weather data from NOAA API for given coordinates
    """
    try:
        # NOAA Weather API endpoint for points
        points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        
        # Get the forecast URL from points response
        response = requests.get(points_url)
        response.raise_for_status()
        forecast_url = response.json()['properties']['forecast']
        
        # Get the actual forecast
        forecast_response = requests.get(forecast_url)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Get current period's forecast
        current_weather = forecast_data['properties']['periods'][0]
        
        return {
            'temperature': current_weather['temperature'],
            'temperature_unit': current_weather['temperatureUnit'],
            'forecast': current_weather['shortForecast'],
            'wind_speed': current_weather['windSpeed'],
            'wind_direction': current_weather['windDirection'],
            'is_daytime': current_weather['isDaytime']
        }
        
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        # Return default values if API fails
        return {
            'temperature': 58,
            'temperature_unit': 'F',
            'forecast': 'mostly sunny',
            'wind_speed': '5 mph',
            'wind_direction': 'N',
            'is_daytime': True
        }

def calculate_weather_risk_factor(weather_data):
    """
    Calculate a risk factor (0-1) based on weather conditions
    """
    try:
        # Temperature risk (higher for extreme temperatures)
        temp = weather_data['temperature']
        temp_risk = min(1.0, abs(temp - 70) / 30)  # Higher risk as temperature deviates from 70°F
        
        # Weather condition risk
        condition = weather_data['forecast'].lower()
        condition_risk = 0.0
        
        if any(word in condition for word in ['storm', 'thunder', 'lightning']):
            condition_risk = 1.0
        elif any(word in condition for word in ['rain', 'snow', 'sleet']):
            condition_risk = 0.7
        elif any(word in condition for word in ['cloudy', 'overcast']):
            condition_risk = 0.3
        
        # Combine risks (weighted average)
        total_risk = (temp_risk * 0.4) + (condition_risk * 0.6)
        return min(1.0, total_risk)
        
    except Exception as e:
        print(f"Error calculating weather risk: {str(e)}")
        return 0.3  # Default moderate risk
