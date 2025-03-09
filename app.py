import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

from utils.data_processing import load_and_process_data
from utils.predictions import calculate_risk_score, get_risk_level
from utils.cost_analysis import calculate_cost_impact
from utils.map_utils import create_equipment_map
from data.sample_data import generate_sample_data

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Utility Preventative Maintenance System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Cards */
    div[data-testid="stMetric"] {
        background-color: #393E46;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Metric labels */
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #EEEEEE !important;
    }

    /* Metric values */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #00ADB5 !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: #EEEEEE !important;
        font-weight: 600 !important;
    }

    /* Tables */
    .stDataFrame {
        background-color: #393E46;
        border-radius: 10px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = generate_sample_data()

# Header with metrics
st.title("⚡ Utility Preventative Maintenance System")

# Top metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_equipment = len(st.session_state.data)
    st.metric("Total Equipment", f"{total_equipment:,}")

with col2:
    high_risk = len(st.session_state.data[st.session_state.data['risk_score'] >= 0.7])
    st.metric("High Risk Equipment", f"{high_risk:,}", delta=f"{high_risk/total_equipment:.1%}")

with col3:
    avg_age = st.session_state.data['age'].mean()
    st.metric("Average Equipment Age", f"{avg_age:.1f} years")

with col4:
    total_customers = st.session_state.data['customer_impact'].sum()
    st.metric("Total Customer Coverage", f"{total_customers:,}")

# Main layout
left_col, right_col = st.columns([2,1])

# Left Panel - Data Overview and Map
with left_col:
    # Search and filter
    search = st.text_input("🔍 Search Equipment", placeholder="Enter ID or name...")

    # Filter data based on search
    filtered_data = st.session_state.data[
        st.session_state.data['product_name'].str.contains(search, case=False) |
        st.session_state.data['product_id'].str.contains(search, case=False)
    ] if search else st.session_state.data

    # Risk level filter
    risk_levels = ['All'] + sorted(filtered_data['risk_score'].apply(get_risk_level).unique().tolist())
    selected_risk = st.selectbox("Filter by Risk Level", risk_levels)

    if selected_risk != 'All':
        filtered_data = filtered_data[filtered_data['risk_score'].apply(get_risk_level) == selected_risk]

    # Display data table with modern styling
    st.dataframe(
        filtered_data.style.map(
            lambda x: f'background-color: {"#2D4059" if x > 0.7 else "#395B64" if x > 0.5 else "#4F6F52"}' 
            if isinstance(x, float) and pd.notnull(x) else '',
            subset=['risk_score']
        ),
        height=300,
        use_container_width=True
    )

    # Map
    st.subheader("📍 Equipment Location Map")
    map_data = create_equipment_map(filtered_data)
    st_folium(map_data, height=400, width=None)

# Right Panel - Equipment Details and Analytics
with right_col:
    st.subheader("📊 Equipment Analysis")

    selected_id = st.selectbox(
        "Select Equipment ID",
        options=filtered_data['product_id'].unique(),
        format_func=lambda x: f"{x} - {filtered_data[filtered_data['product_id']==x].iloc[0]['product_name']}"
    )

    if selected_id:
        equipment = filtered_data[filtered_data['product_id'] == selected_id].iloc[0]

        # Risk score gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = equipment['risk_score'],
            gauge = {
                'axis': {'range': [0, 1], 'tickcolor': "#EEEEEE"},
                'bar': {'color': "#00ADB5"},
                'steps': [
                    {'range': [0, 0.3], 'color': "#4F6F52"},
                    {'range': [0.3, 0.7], 'color': "#395B64"},
                    {'range': [0.7, 1], 'color': "#2D4059"}
                ]
            },
            title = {'text': "Risk Score", 'font': {'color': "#EEEEEE"}}
        ))
        fig.update_layout(
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor = "rgba(0,0,0,0)",
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)

        # Equipment details in expandable sections
        with st.expander("📋 Equipment Details", expanded=True):
            st.write(f"**Product Name:** {equipment['product_name']}")
            st.write(f"**Installation Date:** {equipment['installation_date'].strftime('%Y-%m-%d')}")
            st.write(f"**Last Maintenance:** {equipment['last_maintenance_date'].strftime('%Y-%m-%d')}")
            st.write(f"**Customer Impact:** {equipment['customer_impact']:,} customers")

        with st.expander("💰 Cost Analysis", expanded=True):
            cost_impact = calculate_cost_impact(equipment)
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Preventative Cost",
                    f"${cost_impact['preventative_cost']:,.0f}",
                    delta="-"
                )
            with col2:
                st.metric(
                    "Repair Cost",
                    f"${cost_impact['repair_cost']:,.0f}",
                    delta=f"${cost_impact['savings']:,.0f} savings",
                    delta_color="inverse"
                )

        # Historical trend with improved styling
        st.subheader("📈 Risk Score Trend")
        trend_data = pd.DataFrame({
            'date': pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D'),
            'risk_score': np.random.normal(equipment['risk_score'], 0.1, 30).clip(0, 1)
        })

        fig = px.line(trend_data, x='date', y='risk_score')
        fig.update_layout(
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor = "rgba(0,0,0,0)",
            font = {'color': "#EEEEEE"},
            xaxis = {'gridcolor': "#393E46"},
            yaxis = {'gridcolor': "#393E46"}
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #EEEEEE;'>Last updated: "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</div>",
    unsafe_allow_html=True
)