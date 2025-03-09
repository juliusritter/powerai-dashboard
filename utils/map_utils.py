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

            # Create popup content
            popup_content = f"""
            <div style='font-family: Arial, sans-serif; min-width: 150px;'>
                <strong>{equipment['product_name']}</strong><br>
                ID: {equipment['product_id']}<br>
                Risk Score: {equipment['risk_score']:.2f}
            </div>
            """

            # Add marker using Marker instead of CircleMarker
            folium.Marker(
                location=[equipment['latitude'], equipment['longitude']],
                popup=popup_content,
                icon=folium.Icon(color=color, icon='info-sign'),
            ).add_to(m)

        return m

    except Exception as e:
        raise Exception(f"Error creating map: {str(e)}")