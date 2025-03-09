import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import numpy as np

from utils.data_processing import load_and_process_data
from utils.predictions import calculate_risk_score, get_risk_level
from utils.cost_analysis import calculate_cost_impact
from utils.map_utils import create_equipment_map
from utils.chatbot import get_chatbot_response
from data.sample_data import generate_sample_data

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Utility Preventative Maintenance System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = generate_sample_data()
if 'selected_equipment' not in st.session_state:
    st.session_state.selected_equipment = None
if 'technicians_deployed' not in st.session_state:
    st.session_state.technicians_deployed = 25
if 'crews_deployed' not in st.session_state:
    st.session_state.crews_deployed = 3

# Header with metrics
st.title("⚡ Utility Preventative Maintenance System")

# Top metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_equipment = len(st.session_state.data)
    st.metric("Total Equipment", f"{total_equipment:,}")

with col2:
    # Set network resilience to fixed 70%
    st.metric("Network Resilience", "70.0%")

with col3:
    avg_age = st.session_state.data['age'].mean()
    st.metric("Average Equipment Age", f"{avg_age:.1f} years")

with col4:
    total_customers = st.session_state.data['customer_impact'].sum()
    st.metric("Total Customer Coverage", f"{total_customers:,}")

# Add maintenance crews row
st.markdown("---")
crew1, crew2 = st.columns(2)
with crew1:
    st.metric("Technicians Deployed", str(st.session_state.technicians_deployed))
with crew2:
    st.metric("Crews Deployed", str(st.session_state.crews_deployed))
st.markdown("---")

# Main layout
left_col, right_col = st.columns([1,1])

# Left Panel - Data Overview
with left_col:
    # Search functionality for table
    search = st.text_input("🔍 Search Equipment", placeholder="Enter ID or name to filter the table...")

    # Filter data based on search
    filtered_data = st.session_state.data[
        st.session_state.data['product_name'].str.contains(search, case=False) |
        st.session_state.data['product_id'].str.contains(search, case=False)
    ] if search else st.session_state.data

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