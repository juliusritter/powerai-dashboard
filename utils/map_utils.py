import folium
from branca.element import Figure

def create_equipment_map(data):
    """Create folium map with equipment markers"""
    try:
        # Calculate map center
        center_lat = data['latitude'].mean()
        center_lon = data['longitude'].mean()

        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )

        # Add markers for each equipment
        for _, equipment in data.iterrows():
            # Determine marker color based on risk score
            if equipment['risk_score'] < 0.3:
                color = 'green'
            elif equipment['risk_score'] < 0.5:
                color = 'yellow'
            elif equipment['risk_score'] < 0.7:
                color = 'orange'
            else:
                color = 'red'

            # Determine possible outage reason
            reasons = []
            if equipment['age'] > 15:
                reasons.append("Equipment Age")
            if equipment['days_since_maintenance'] > 180:
                reasons.append("Maintenance Overdue")
            if equipment['vegetation_proximity']:
                reasons.append("Vegetation Proximity")
            if equipment['temperature'] > 85:
                reasons.append("High Temperature")
            if equipment['precipitation_forecast'] > 30:
                reasons.append("Heavy Precipitation")

            outage_reason = " & ".join(reasons) if reasons else "No immediate risks"

            # Create popup content with HTML
            popup_content = f"""
            <div style='font-family: Arial, sans-serif; min-width: 200px;'>
                <strong style='font-size: 16px;'>{equipment['product_name']}</strong><br>
                <hr style='margin: 5px 0;'>
                <strong>Risk Score:</strong> {equipment['risk_score']:.2f}<br>
                <strong>Possible Outage:</strong> {outage_reason}<br>
                <strong>Customers Impacted:</strong> {equipment['customer_impact']:,}
            </div>
            """

            # Add marker
            folium.Marker(
                location=[equipment['latitude'], equipment['longitude']],
                popup=popup_content,
                icon=folium.Icon(color=color, icon='info-sign'),
            ).add_to(m)

        return m

    except Exception as e:
        raise Exception(f"Error creating map: {str(e)}")