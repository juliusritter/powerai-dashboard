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
                <b>{equipment['product_name']}</b><br>
                ID: {equipment['product_id']}<br>
                Risk Score: {equipment['risk_score']:.2f}<br>
                Customers: {equipment['customer_impact']}
            """

            # Add marker
            folium.CircleMarker(
                location=[equipment['latitude'], equipment['longitude']],
                radius=8,
                popup=folium.Popup(popup_content, max_width=300),
                color=color,
                fill=True,
                fill_color=color
            ).add_to(m)

        return m

    except Exception as e:
        raise Exception(f"Error creating map: {str(e)}")