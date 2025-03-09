import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import numpy as np
import requests

from utils.data_processing import load_and_process_data
from utils.predictions import calculate_risk_score, get_risk_level
from utils.cost_analysis import calculate_cost_impact
from utils.map_utils import create_equipment_map
from utils.chatbot import get_chatbot_response
from data.sample_data import generate_sample_data
from utils.weather_utils import fetch_noaa_weather

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Power.AI - Grid Infrastructure",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background-color: #000000;
    }

    /* Headers */
    h1, h2, h3 {
        color: #FFDC3C !important;
        font-family: 'SF Pro Display', sans-serif;
    }

    /* Metrics */
    .stMetric {
        background-color: #111111;
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255, 220, 60, 0.1);
    }
    .stMetric:hover {
        border: 1px solid rgba(255, 220, 60, 0.3);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    .stMetric label {
        color: #CCCCCC !important;
    }
    .stMetric .metric-value {
        color: #FFDC3C !important;
        font-weight: bold;
    }

    /* Buttons */
    .stButton button {
        background-color: #FFDC3C !important;
        color: #000000 !important;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #FFE461 !important;
        transform: translateY(-1px);
        transition: all 0.2s ease;
    }

    /* Input fields */
    .stTextInput input {
        background-color: #111111;
        border: 1px solid rgba(255, 220, 60, 0.2);
        border-radius: 10px;
        color: white;
    }
    .stTextInput input:focus {
        border-color: #FFDC3C;
        box-shadow: 0 0 0 2px rgba(255, 220, 60, 0.2);
    }

    /* DataFrames */
    .dataframe {
        background-color: #111111 !important;
        border-radius: 10px;
        border: 1px solid rgba(255, 220, 60, 0.1);
    }

    /* Custom logo and title */
    .logo-title {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    .logo-title img {
        width: 50px;
        height: 50px;
    }
    .tagline {
        color: #CCCCCC;
        font-size: 0.9rem;
        letter-spacing: 2px;
        margin-bottom: 2rem;
    }
</style>

<!-- Logo and Title -->
<div class="logo-title">
    <svg width="50" height="50" viewBox="0 0 50 50">
        <path d="M25 2L10 40H24L20 48L40 18H26L35 2H25Z" 
              fill="#FFDC3C" 
              stroke="#FFDC3C" 
              stroke-width="2"/>
    </svg>
    <h1>Power.AI</h1>
</div>
<div class="tagline">
    EARLY WARNING SYSTEM FOR GRID INFRASTRUCTURE
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = generate_sample_data()
if 'selected_equipment' not in st.session_state:
    st.session_state.selected_equipment = None
if 'technicians_deployed' not in st.session_state:
    st.session_state.technicians_deployed = 25
if 'crews_deployed' not in st.session_state:
    st.session_state.crews_deployed = 3
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = fetch_noaa_weather(37.7749, -122.4194)

# Update weather every 30 minutes
if 'last_weather_update' not in st.session_state:
    st.session_state.last_weather_update = datetime.now()
elif (datetime.now() - st.session_state.last_weather_update).total_seconds() > 1800:
    st.session_state.weather_data = fetch_noaa_weather(37.7749, -122.4194)
    st.session_state.last_weather_update = datetime.now()

# Top metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_equipment = len(st.session_state.data)
    st.metric("Total Equipment", f"{total_equipment:,}")

with col2:
    st.metric("Network Resilience", "70.0%")

with col3:
    avg_age = st.session_state.data['age'].mean()
    st.metric("Average Equipment Age", f"{avg_age:.1f} years")

with col4:
    total_customers = st.session_state.data['customer_impact'].sum()
    st.metric("Total Customer Coverage", f"{total_customers:,}")

# Add maintenance crews row
st.markdown("---")
crew1, crew2, weather = st.columns([1,1,1.5], gap="small")
with crew1:
    st.metric("Technicians Deployed", str(st.session_state.technicians_deployed))
with crew2:
    st.metric("Crews Deployed", str(st.session_state.crews_deployed))
with weather:
    weather_text = f"{st.session_state.weather_data['forecast']} ({st.session_state.weather_data['temperature']} {st.session_state.weather_data['temperature_unit']})"
    st.metric("Weather conditions", weather_text)
st.markdown("---")

# Main layout
left_col, right_col = st.columns([1,1])

# Left Panel - Data Overview
with left_col:
    # Search functionality for table
    search = st.text_input("🔍 Search Equipment", placeholder="Enter ID or name to filter the table...")

    # Filter data based on search
    filtered_data = st.session_state.data.copy() #create a copy to avoid modifying original data
    if search:
        filtered_data = filtered_data[
            filtered_data['product_name'].str.contains(search, case=False) |
            filtered_data['product_id'].str.contains(search, case=False)
        ]

    # Update risk calculations in the data processing
    for idx, row in filtered_data.iterrows():
        filtered_data.at[idx, 'risk_score'] = calculate_risk_score(row, st.session_state.weather_data)


    # Display data table
    st.dataframe(
        filtered_data,
        height=600,
        use_container_width=True
    )

# Right Panel - Map
with right_col:
    st.subheader("📍 Equipment Location Map")

    # Create and display the map with click events
    map_data = create_equipment_map(st.session_state.data)  # Use full dataset for map
    map_events = st_folium(
        map_data,
        height=600,
        width=None,
        returned_objects=["last_clicked"]
    )

    # Handle map click events
    if map_events["last_clicked"] and isinstance(map_events["last_clicked"], dict):
        clicked_content = map_events["last_clicked"].get("popup", "")
        if "ID:" in clicked_content:
            equipment_id = clicked_content.split("ID:")[1].split("<br>")[0].strip()
            if equipment_id != st.session_state.selected_equipment:
                st.session_state.selected_equipment = equipment_id
                st.rerun()

# Chatbot section after the main layout
st.markdown("---")
user_input = st.text_input("🤖 Chatbot", placeholder="Ask me anything about the network...")

# Process chatbot input
if user_input:
    try:
        # Get AI response
        response = get_chatbot_response(user_input, st.session_state.data)

        # Display response in a nice format
        st.info(response["recommendation"])

        # Add 10 technicians after receiving the response
        st.session_state.technicians_deployed += 10

    except Exception as e:
        st.error(f"Error: {str(e)}")
        print(f"Chatbot error: {str(e)}")  # Add logging

# Sidebar for equipment details
if st.session_state.selected_equipment is not None:
    with st.sidebar:
        equipment = st.session_state.data[
            st.session_state.data['product_id'] == st.session_state.selected_equipment
        ].iloc[0]

        st.title(f"📋 Equipment Details")
        st.write(f"**ID:** {equipment['product_id']}")
        st.write(f"**Product Name:** {equipment['product_name']}")
        st.write(f"**Installation Date:** {equipment['installation_date'].strftime('%Y-%m-%d')}")
        st.write(f"**Last Maintenance:** {equipment['last_maintenance_date'].strftime('%Y-%m-%d')}")
        st.write(f"**Customer Impact:** {equipment['customer_impact']:,} customers")

        st.subheader("💰 Cost Analysis")
        cost_impact = calculate_cost_impact(equipment)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Preventative Cost",
                f"${cost_impact['preventative_cost']:,.0f}"
            )
        with col2:
            st.metric(
                "Repair Cost",
                f"${cost_impact['repair_cost']:,.0f}"
            )

        if st.button("Close Details"):
            st.session_state.selected_equipment = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #EEEEEE;'>Last updated: "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</div>",
    unsafe_allow_html=True
)