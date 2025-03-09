import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime
import numpy as np

from utils.data_processing import load_and_process_data
from utils.predictions import calculate_risk_score
from utils.cost_analysis import calculate_cost_impact
from utils.map_utils import create_equipment_map
from data.sample_data import generate_sample_data

# Page config
st.set_page_config(
    page_title="Utility Preventative Maintenance System",
    page_icon="⚡",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = generate_sample_data()

# Header
col1, col2, col3 = st.columns([2,1,1])
with col1:
    st.title("Utility Preventative Maintenance System")
with col2:
    st.write(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
with col3:
    st.write("Weather Alert: Clear ☀️")

# Main layout
left_col, right_col = st.columns([3,2])

# Left Panel - Data Overview
with left_col:
    st.subheader("Equipment Overview")
    
    # Search and filter
    search = st.text_input("Search Equipment", "")
    
    # Filter data based on search
    filtered_data = st.session_state.data[
        st.session_state.data['product_name'].str.contains(search, case=False) |
        st.session_state.data['product_id'].str.contains(search, case=False)
    ]
    
    # Sort options
    sort_col = st.selectbox("Sort by", filtered_data.columns)
    sort_order = st.radio("Sort order", ["Ascending", "Descending"], horizontal=True)
    filtered_data = filtered_data.sort_values(
        by=sort_col, 
        ascending=sort_order=="Ascending"
    )
    
    # Display data table
    st.dataframe(
        filtered_data.style.applymap(
            lambda x: 'background-color: #ffcccb' if isinstance(x, (int, float)) and x > 0.7 else None,
            subset=['risk_score']
        ),
        height=400
    )
    
    # Export buttons
    if st.button("Export to CSV"):
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="equipment_data.csv",
            mime="text/csv"
        )

# Right Panel - Map
with right_col:
    st.subheader("Equipment Location Map")
    map_data = create_equipment_map(filtered_data)
    folium_static(map_data)

# Detail Panel
st.subheader("Equipment Details")
selected_id = st.selectbox(
    "Select Equipment ID",
    options=filtered_data['product_id'].unique()
)

if selected_id:
    equipment = filtered_data[filtered_data['product_id'] == selected_id].iloc[0]
    
    # Equipment details in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Equipment Specifications**")
        st.write(f"Product Name: {equipment['product_name']}")
        st.write(f"Installation Date: {equipment['installation_date']}")
        st.write(f"Last Maintenance: {equipment['last_maintenance_date']}")
        
    with col2:
        st.write("**Risk Assessment**")
        st.write(f"Risk Score: {equipment['risk_score']:.2f}")
        st.write(f"Vegetation Proximity: {'Yes' if equipment['vegetation_proximity'] else 'No'}")
        st.write(f"Customer Impact: {equipment['customer_impact']} customers")
        
    with col3:
        st.write("**Cost Analysis**")
        cost_impact = calculate_cost_impact(equipment)
        st.write(f"Preventative Maintenance: ${cost_impact['preventative_cost']:,.2f}")
        st.write(f"Potential Repair Cost: ${cost_impact['repair_cost']:,.2f}")
        st.write(f"Potential Savings: ${cost_impact['savings']:,.2f}")
    
    # Historical trend
    st.subheader("Risk Score Trend")
    trend_data = pd.DataFrame({
        'date': pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D'),
        'risk_score': np.random.normal(equipment['risk_score'], 0.1, 30).clip(0, 1)
    })
    fig = px.line(trend_data, x='date', y='risk_score',
                  title='30-Day Risk Score Trend')
    st.plotly_chart(fig)
