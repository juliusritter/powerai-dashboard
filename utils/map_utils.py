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

            # Create popup content with HTML - keep ID format consistent for parsing
            popup_content = f"""
            <div style='font-family: Arial, sans-serif;'>
                <strong>{equipment['product_name']}</strong><br>
                <strong>ID:</strong> {equipment['product_id']}<br>
                <strong>Risk Score:</strong> {equipment['risk_score']:.2f}
            </div>
            """

            # Add marker with custom popup
            folium.CircleMarker(
                location=[equipment['latitude'], equipment['longitude']],
                radius=8,
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=f"{equipment['product_name']} - {equipment['product_id']}",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
            ).add_to(m)

        return m

    except Exception as e:
        raise Exception(f"Error creating map: {str(e)}")