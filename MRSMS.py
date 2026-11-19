"""
Mine Rescue & Safety Monitoring System (MRSMS)
Surface Control Station - Python Streamlit Interactive 3D Dashboard

Author: nirmal-mugunth
Designed for: Industrial Visualization & Mine Rescue Telemetry Operations
Compliant with: OSHA & MSHA Title 30 Underground Standards
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Import local helper modules
from prediction_engine import THRESHOLDS, calculate_safety_index, forecast_gas
from simulator import generate_initial_history, step_simulation, DEFAULT_SECTORS

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MRSMS - Mine Rescue & Safety Monitoring System",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM INDUSTRIAL DARK STYLING ---
st.markdown("""
<style>
    /* Dark industrial background */
    .stApp {
        background-color: #080c14;
        color: #e2e8f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Top title styling */
    .mrsms-header {
        background: linear-gradient(90deg, #0b1220 0%, #0e1a2f 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .mrsms-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: #f8fafc;
        margin: 0;
    }
    
    .mrsms-badge {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-family: monospace;
        font-weight: 700;
        margin-left: 8px;
    }
    
    /* Metric cards */
    .metric-card {
        background: #0d1526;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    
    .metric-value-safe { color: #10b981; font-size: 26px; font-weight: 800; font-family: monospace; }
    .metric-value-caution { color: #f59e0b; font-size: 26px; font-weight: 800; font-family: monospace; }
    .metric-value-critical { color: #ef4444; font-size: 26px; font-weight: 800; font-family: monospace; animation: blink 1s infinite; }
    
    /* SOS Emergency Alert Bar */
    .sos-banner {
        background: linear-gradient(90deg, #991b1b 0%, #dc2626 50%, #991b1b 100%);
        border: 2px solid #ef4444;
        border-radius: 10px;
        padding: 14px 20px;
        color: white;
        font-weight: 800;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
    }
</style>
""", unsafe_allow_html=True)


# --- 3. SESSION STATE INITIALIZATION ---
if 'history' not in st.session_state:
    st.session_state.history = generate_initial_history(40)

if 'scenario' not in st.session_state:
    st.session_state.scenario = 'NORMAL'

if 'audio_muted' not in st.session_state:
    st.session_state.audio_muted = False

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = '3D Cave Disaster'

if 'alerts' not in st.session_state:
    st.session_state.alerts = []


# --- 4. STEP SIMULATION UPDATE ---
latest = st.session_state.history[-1]
safety_index = calculate_safety_index(latest)

# Check for Critical Gas Breaches for Auto-SOS
is_ch4_crit = latest['ch4_ppm'] >= THRESHOLDS['ch4_critical']
is_co_crit = latest['co_ppm'] >= THRESHOLDS['co_critical']
is_so2_crit = latest['so2_ppm'] >= THRESHOLDS['so2_critical']
is_o2_crit = latest['o2_percent'] <= THRESHOLDS['o2_critical']
is_dist_crit = latest['distance_cm'] < THRESHOLDS['dist_critical']

sos_active = is_ch4_crit or is_co_crit or is_so2_crit or is_o2_crit or is_dist_crit

# Automatically record alert if not already logged
if sos_active:
    crit_msg = []
    if is_ch4_crit: crit_msg.append(f"Methane {latest['ch4_ppm']} ppm (≥10,000 ppm)")
    if is_co_crit: crit_msg.append(f"Carbon Monoxide {latest['co_ppm']} ppm (≥100 ppm)")
    if is_so2_crit: crit_msg.append(f"Sulphur Dioxide {latest['so2_ppm']} ppm (≥20 ppm)")
    if is_o2_crit: crit_msg.append(f"Oxygen Deficient {latest['o2_percent']}% (≤16.0%)")
    if is_dist_crit: crit_msg.append(f"Roof Convergence {latest['distance_cm']} cm (<100 cm)")
    
    alert_entry = {
        'timestamp': latest['timestamp'],
        'sector': latest['sector_name'],
        'node_id': latest['node_id'],
        'hazard': ", ".join(crit_msg),
        'severity': 'CRITICAL',
        'status': 'ACTIVE'
    }
    if not any(a['hazard'] == alert_entry['hazard'] and a['status'] == 'ACTIVE' for a in st.session_state.alerts):
        st.session_state.alerts.insert(0, alert_entry)


# --- 5. AUDIO ALARM (AMBULANCE SIREN GENERATOR) ---
# Uses Web Audio API to procedurally generate a high-pitch 650Hz <-> 1050Hz two-tone wail
if sos_active and not st.session_state.audio_muted:
    st.components.v1.html("""
    <script>
    (function() {
        try {
            var AudioContext = window.AudioContext || window.webkitAudioContext;
            var ctx = new AudioContext();
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.type = 'sawtooth';
            
            var now = ctx.currentTime;
            osc.frequency.setValueAtTime(650, now);
            osc.frequency.linearRampToValueAtTime(1050, now + 0.55);
            osc.frequency.linearRampToValueAtTime(650, now + 1.1);
            
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 1.15);
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 1.2);
        } catch(e) {}
    })();
    </script>
    """, height=0)


# --- 6. TOP CONTROL HEADER ---
st.markdown(f"""
<div class="mrsms-header">
    <div>
        <h1 class="mrsms-title">⛏️ MRSMS <span class="mrsms-badge">SURFACE CONTROL STATION</span></h1>
        <div style="font-size: 12px; color: #94a3b8; font-family: monospace; margin-top: 4px;">
            MINE RESCUE & SAFETY MONITORING SYSTEM • SHAFT COMPLEX #4 • ELEVATION -420M
        </div>
    </div>
    <div style="text-align: right; font-family: monospace; font-size: 12px; color: #94a3b8;">
        <div>SYSTEM STATUS: <span style="color: {'#ef4444' if sos_active else '#10b981'}; font-weight: 800;">
            {'🚨 EMERGENCY SOS ACTIVE' if sos_active else '✅ NORMAL MONITORING'}
        </span></div>
        <div>SAFETY INDEX: <span style="color: {'#ef4444' if safety_index < 40 else '#f59e0b' if safety_index < 70 else '#10b981'}; font-weight: 800; font-size: 16px;">
            {safety_index} / 100
        </span></div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- 7. AUTO-SOS EMERGENCY BANNER ---
if sos_active:
    st.markdown("""
    <div class="sos-banner">
        <div>
            <span style="font-size: 22px; margin-right: 10px;">🚨</span>
            <span style="letter-spacing: 1px; font-size: 15px;">CRITICAL GAS LEAK DETECTED — AMBULANCE SIREN BROADCAST ACTIVE</span>
            <div style="font-size: 12px; opacity: 0.9; font-family: monospace; font-weight: normal; margin-top: 3px;">
                Sector 4 Sub-level B • High-pitch evacuation protocol initiated • All personnel evacuate to Surface
            </div>
        </div>
        <div style="font-size: 12px; font-family: monospace;">
            OSHA / MSHA TITLE 30 MANDATORY ACTION
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- 8. SIDEBAR CONTROLS & SIMULATION ---
with st.sidebar:
    st.subheader("⚙️ Control Console")
    
    # Active Sector Selector
    selected_sector = st.selectbox(
        "Active Underground Node",
        [f"{s['node_id']} - {s['sector_name'].split('-')[0]} ({s['elevation_m']}m)" for s in DEFAULT_SECTORS]
    )
    
    st.markdown("---")
    st.subheader("🧪 Hazard Simulator")
    scenario_choice = st.radio(
        "Simulation Scenario Preset",
        ["NORMAL", "METHANE_SURGE", "FIRE_OUTBREAK", "CAVE_IN"],
        index=["NORMAL", "METHANE_SURGE", "FIRE_OUTBREAK", "CAVE_IN"].index(st.session_state.scenario)
    )
    st.session_state.scenario = scenario_choice
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        if st.button("▶️ Step Simulation", use_container_width=True):
            next_sample = step_simulation(st.session_state.history[-1], scenario=st.session_state.scenario)
            st.session_state.history.append(next_sample)
            if len(st.session_state.history) > 100:
                st.session_state.history.pop(0)
            st.rerun()
            
    with col_sim2:
        if st.button("🔄 Reset Data", use_container_width=True):
            st.session_state.history = generate_initial_history(40)
            st.session_state.alerts = []
            st.rerun()

    st.markdown("---")
    st.subheader("🔊 Audio Alarm")
    st.session_state.audio_muted = st.toggle("Mute Siren", value=st.session_state.audio_muted)
    if st.session_state.audio_muted:
        st.caption("🔇 Siren muted.")
    else:
        st.caption("🔊 High-pitch siren armed on hazard breach.")


# --- 9. TOP NAVIGATION TABS ---
tab_3d, tab_trends, tab_sensing, tab_incidents = st.tabs([
    "🏔️ 3D Cave Disaster Management",
    "📊 Predictions & Trends",
    "🧪 Gas Sensing Grid",
    "🚨 Incident Protocol & Leak Locations"
])


# ==============================================================================
# TAB 1: 3D CAVE DISASTER MANAGEMENT
# ==============================================================================
with tab_3d:
    st.markdown("### 3D Subsurface Cave Disaster & Gas Leak Tracking")
    st.caption("Interactive 3D spatial perspective of underground tunnel drift, methane leak fracture point, real-time gas diffusion cloud, and emergency ventilation paths.")

    # Generate 3D Cave Tunnel Coordinates
    # Tunnel geometry: Length X (-20 to 80), Width Y (-10 to 10), Height Z (-5 to 5)
    tunnel_x = np.linspace(0, 100, 30)
    
    # Gas leak origin (wall crack)
    leak_x, leak_y, leak_z = 65, 8, 0

    # Animated stochastic gas particles around leak
    np.random.seed(42)
    n_particles = 120
    cloud_intensity = latest['ch4_ppm'] / 10000.0  # relative intensity
    cloud_x = leak_x - np.random.exponential(15, n_particles) * min(2.0, cloud_intensity)
    cloud_y = leak_y + np.random.normal(-5, 4, n_particles)
    cloud_z = leak_z + np.random.normal(0, 3, n_particles)

    # 3D Plotly Figure
    fig3d = go.Figure()

    # 1. Tunnel Floor & Ceiling Rails
    fig3d.add_trace(go.Scatter3d(
        x=[0, 100, 100, 0, 0],
        y=[-10, -10, 10, 10, -10],
        z=[-5, -5, -5, -5, -5],
        mode='lines',
        line=dict(color='#334155', width=5),
        name='Tunnel Floor Boundary'
    ))
    fig3d.add_trace(go.Scatter3d(
        x=[0, 100, 100, 0, 0],
        y=[-10, -10, 10, 10, -10],
        z=[5, 5, 5, 5, 5],
        mode='lines',
        line=dict(color='#1e293b', width=4),
        name='Tunnel Ceiling Crown'
    ))

    # 2. Structural Stalactite / Convergence Points
    fig3d.add_trace(go.Scatter3d(
        x=[20, 45, 75],
        y=[0, -2, 3],
        z=[5 - (latest['distance_cm'] / 40.0) for _ in range(3)],
        mode='markers+text',
        marker=dict(size=8, color='#f59e0b', symbol='diamond'),
        text=['Roof Convergence Gauge', '', ''],
        name='Ultrasonic Clearance Probes'
    ))

    # 3. Gas Leak Rupture Source
    fig3d.add_trace(go.Scatter3d(
        x=[leak_x], y=[leak_y], z=[leak_z],
        mode='markers+text',
        marker=dict(size=14, color='#ef4444', symbol='cross'),
        text=['💥 GAS LEAK SOURCE (SECTOR 4)'],
        textposition='top center',
        name='Gas Rupture Point'
    ))

    # 4. Multi-layered Gas Dispersion Cloud
    gas_color = '#ef4444' if latest['ch4_ppm'] >= THRESHOLDS['ch4_critical'] else '#f59e0b' if latest['ch4_ppm'] >= THRESHOLDS['ch4_caution'] else '#10b981'
    fig3d.add_trace(go.Scatter3d(
        x=cloud_x, y=cloud_y, z=cloud_z,
        mode='markers',
        marker=dict(
            size=6 + (cloud_intensity * 4),
            color=gas_color,
            opacity=0.45
        ),
        name=f"Gas Cloud ({latest['ch4_ppm']} ppm CH4)"
    ))

    # 5. Gas Escape Route (Cyan dashed line)
    fig3d.add_trace(go.Scatter3d(
        x=[leak_x, 40, 20, 0],
        y=[leak_y, 0, -2, -5],
        z=[leak_z, 2, 4, 5],
        mode='lines+markers',
        line=dict(color='#22d3ee', width=4, dash='dash'),
        name='Gas Escape Tracking Vector'
    ))

    # 6. Ventilation Fix Resolution Path (Green)
    fig3d.add_trace(go.Scatter3d(
        x=[10, 30, 50, leak_x],
        y=[-8, -6, 0, leak_y],
        z=[-4, -2, 0, leak_z],
        mode='lines+markers',
        line=dict(color='#10b981', width=5),
        name='Ventilation Resolution Jet'
    ))

    # 7. Rescue Teams Positions
    teams_x = [15, 35, 10]
    teams_y = [-4, 5, 2]
    teams_z = [-4.5, -4.5, -4.5]
    teams_labels = ['Alpha Search & Rescue', 'Bravo Shoring Unit', 'Charlie Med Evac']
    teams_colors = ['#60a5fa', '#c084fc', '#34d399']
    
    for tx, ty, tz, lbl, col in zip(teams_x, teams_y, teams_z, teams_labels, teams_colors):
        fig3d.add_trace(go.Scatter3d(
            x=[tx], y=[ty], z=[tz],
            mode='markers+text',
            marker=dict(size=9, color=col),
            text=[f"👷 {lbl}"],
            textposition='bottom center',
            name=lbl
        ))

    # Layout styling for crisp dark 3D visualization
    fig3d.update_layout(
        scene=dict(
            xaxis=dict(title='Tunnel Drift (meters)', backgroundcolor='#080c14', gridcolor='#1e293b', showbackground=True),
            yaxis=dict(title='Cross Drift (meters)', backgroundcolor='#080c14', gridcolor='#1e293b', showbackground=True),
            zaxis=dict(title='Elevation Height (m)', backgroundcolor='#080c14', gridcolor='#1e293b', showbackground=True),
            camera=dict(eye=dict(x=-1.6, y=-1.8, z=1.2))
        ),
        paper_bgcolor='#0b1120',
        margin=dict(l=0, r=0, t=20, b=0),
        height=550,
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, font=dict(size=11, color='#94a3b8'))
    )

    st.plotly_chart(fig3d, use_container_width=True)

    # 3D Legend Bar
    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    col_l1.markdown("🔴 **Gas Rupture:** Wall fissure at +65m")
    col_l2.markdown("🔵 **Cyan Vector:** Atmospheric migration route")
    col_l3.markdown("🟢 **Green Jet:** Positive-pressure air fan")
    col_l4.markdown("👷 **Blue/Purple:** Subsurface rescue personnel")


# ==============================================================================
# TAB 2: PREDICTIONS & TRENDS
# ==============================================================================
with tab_trends:
    st.markdown("### Multi-Gas Concentration & 10-Minute Predictive Forecast")
    st.caption("Solid lines represent real-time sensor recordings. Dashed lines project 10-minute forward accumulation curves.")

    selected_gas_view = st.selectbox(
        "Select Gas or Parameter to Inspect",
        ["Methane (CH4)", "Carbon Monoxide (CO)", "Sulphur Dioxide (SO2)", "Carbon Dioxide (CO2)", "Oxygen (O2)", "Roof Clearance (Ultrasonic)"]
    )

    # Convert session history to DataFrame
    df_hist = pd.DataFrame(st.session_state.history)

    fig_trend = go.Figure()

    if selected_gas_view == "Methane (CH4)":
        pred_ch4 = forecast_gas(st.session_state.history, 'ch4_ppm', THRESHOLDS['ch4_caution'], THRESHOLDS['ch4_critical'], False)
        
        # Real-time recorded trace
        fig_trend.add_trace(go.Scatter(
            x=df_hist['timestamp'], y=df_hist['ch4_ppm'],
            mode='lines+markers', name='CH4 Recorded (ppm)',
            line=dict(color='#f59e0b', width=3)
        ))
        
        # Projected forward points
        last_time = df_hist['timestamp'].iloc[-1]
        proj_x = [f"+{p['minute']}m" for p in pred_ch4['projected_points']]
        proj_y = [p['predicted_value'] for p in pred_ch4['projected_points']]
        
        fig_trend.add_trace(go.Scatter(
            x=[last_time] + proj_x,
            y=[latest['ch4_ppm']] + proj_y,
            mode='lines+markers', name='CH4 10m Forecast Curve',
            line=dict(color='#fbbf24', width=3, dash='dash')
        ))
        
        # Threshold Reference Lines
        fig_trend.add_hline(y=THRESHOLDS['ch4_caution'], line_dash="dot", line_color="#f59e0b", annotation_text="10% LEL Caution (5k ppm)")
        fig_trend.add_hline(y=THRESHOLDS['ch4_critical'], line_dash="dash", line_color="#ef4444", annotation_text="20% LEL Evacuation (10k ppm)")

    elif selected_gas_view == "Carbon Monoxide (CO)":
        pred_co = forecast_gas(st.session_state.history, 'co_ppm', THRESHOLDS['co_caution'], THRESHOLDS['co_critical'], False)
        fig_trend.add_trace(go.Scatter(
            x=df_hist['timestamp'], y=df_hist['co_ppm'],
            mode='lines+markers', name='CO Recorded (ppm)',
            line=dict(color='#f43f5e', width=3)
        ))
        proj_x = [f"+{p['minute']}m" for p in pred_co['projected_points']]
        proj_y = [p['predicted_value'] for p in pred_co['projected_points']]
        fig_trend.add_trace(go.Scatter(
            x=[df_hist['timestamp'].iloc[-1]] + proj_x,
            y=[latest['co_ppm']] + proj_y,
            mode='lines+markers', name='CO 10m Forecast Curve',
            line=dict(color='#fb7185', width=3, dash='dash')
        ))
        fig_trend.add_hline(y=THRESHOLDS['co_caution'], line_dash="dot", line_color="#f59e0b", annotation_text="35 ppm 8-hr TWA")
        fig_trend.add_hline(y=THRESHOLDS['co_critical'], line_dash="dash", line_color="#ef4444", annotation_text="100 ppm Lethal Ceiling")

    elif selected_gas_view == "Sulphur Dioxide (SO2)":
        pred_so2 = forecast_gas(st.session_state.history, 'so2_ppm', THRESHOLDS['so2_caution'], THRESHOLDS['so2_critical'], False)
        fig_trend.add_trace(go.Scatter(
            x=df_hist['timestamp'], y=df_hist['so2_ppm'],
            mode='lines+markers', name='SO2 Recorded (ppm)',
            line=dict(color='#fb923c', width=3)
        ))
        proj_x = [f"+{p['minute']}m" for p in pred_so2['projected_points']]
        proj_y = [p['predicted_value'] for p in pred_so2['projected_points']]
        fig_trend.add_trace(go.Scatter(
            x=[df_hist['timestamp'].iloc[-1]] + proj_x,
            y=[latest['so2_ppm']] + proj_y,
            mode='lines+markers', name='SO2 Forecast',
            line=dict(color='#fdba74', width=3, dash='dash')
        ))
        fig_trend.add_hline(y=THRESHOLDS['so2_caution'], line_dash="dot", line_color="#f59e0b", annotation_text="5 ppm Caution")
        fig_trend.add_hline(y=THRESHOLDS['so2_critical'], line_dash="dash", line_color="#ef4444", annotation_text="20 ppm IDLH")

    elif selected_gas_view == "Oxygen (O2)":
        pred_o2 = forecast_gas(st.session_state.history, 'o2_percent', THRESHOLDS['o2_caution'], THRESHOLDS['o2_critical'], True)
        fig_trend.add_trace(go.Scatter(
            x=df_hist['timestamp'], y=df_hist['o2_percent'],
            mode='lines+markers', name='O2 Recorded (%)',
            line=dict(color='#14b8a6', width=3)
        ))
        fig_trend.add_hline(y=THRESHOLDS['o2_caution'], line_dash="dot", line_color="#f59e0b", annotation_text="19.5% Minimum Safe Breathable")
        fig_trend.add_hline(y=THRESHOLDS['o2_critical'], line_dash="dash", line_color="#ef4444", annotation_text="16.0% Asphyxiation Hazard")

    elif selected_gas_view == "Roof Clearance (Ultrasonic)":
        pred_dist = forecast_gas(st.session_state.history, 'distance_cm', THRESHOLDS['dist_caution'], THRESHOLDS['dist_critical'], True)
        fig_trend.add_trace(go.Scatter(
            x=df_hist['timestamp'], y=df_hist['distance_cm'],
            mode='lines+markers', name='Clearance Distance (cm)',
            line=dict(color='#38bdf8', width=3)
        ))
        fig_trend.add_hline(y=THRESHOLDS['dist_caution'], line_dash="dot", line_color="#f59e0b", annotation_text="180 cm Convergence Warning")
        fig_trend.add_hline(y=THRESHOLDS['dist_critical'], line_dash="dash", line_color="#ef4444", annotation_text="100 cm Imminent Collapse Limit")

    fig_trend.update_layout(
        paper_bgcolor='#0b1120',
        plot_bgcolor='#070b13',
        font=dict(color='#94a3b8', family='monospace'),
        height=400,
        margin=dict(l=30, r=30, t=30, b=30),
        xaxis=dict(gridcolor='#1e293b'),
        yaxis=dict(gridcolor='#1e293b')
    )
    st.plotly_chart(fig_trend, use_container_width=True)


# ==============================================================================
# TAB 3: GAS SENSING GRID
# ==============================================================================
with tab_sensing:
    st.markdown("### Multi-Gas Environmental Monitoring Panel")
    
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    # 1. Methane CH4
    ch4_val = latest['ch4_ppm']
    ch4_class = "metric-value-critical" if ch4_val >= THRESHOLDS['ch4_critical'] else "metric-value-caution" if ch4_val >= THRESHOLDS['ch4_caution'] else "metric-value-safe"
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #94a3b8; font-family: monospace;">METHANE (CH4)</div>
            <div class="{ch4_class}">{ch4_val:,.1f} <span style="font-size: 14px;">ppm</span></div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">{latest['ch4_lel_percent']}% LEL • Evac: 10,000 ppm</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. Carbon Monoxide CO
    co_val = latest['co_ppm']
    co_class = "metric-value-critical" if co_val >= THRESHOLDS['co_critical'] else "metric-value-caution" if co_val >= THRESHOLDS['co_caution'] else "metric-value-safe"
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #94a3b8; font-family: monospace;">CARBON MONOXIDE (CO)</div>
            <div class="{co_class}">{co_val:.1f} <span style="font-size: 14px;">ppm</span></div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">TWA: 35 ppm • Ceiling: 100 ppm</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Sulphur Dioxide SO2
    so2_val = latest['so2_ppm']
    so2_class = "metric-value-critical" if so2_val >= THRESHOLDS['so2_critical'] else "metric-value-caution" if so2_val >= THRESHOLDS['so2_caution'] else "metric-value-safe"
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #94a3b8; font-family: monospace;">SULPHUR DIOXIDE (SO2)</div>
            <div class="{so2_class}">{so2_val:.1f} <span style="font-size: 14px;">ppm</span></div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Caution: 5 ppm • IDLH: 20 ppm</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Carbon Dioxide CO2
    co2_val = latest['co2_ppm']
    co2_class = "metric-value-critical" if co2_val >= THRESHOLDS['co2_critical'] else "metric-value-caution" if co2_val >= THRESHOLDS['co2_caution'] else "metric-value-safe"
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #94a3b8; font-family: monospace;">CARBON DIOXIDE (CO2)</div>
            <div class="{co2_class}">{co2_val:.0f} <span style="font-size: 14px;">ppm</span></div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Baseline: 400 • Limit: 5,000 ppm</div>
        </div>
        """, unsafe_allow_html=True)

    # 5. Oxygen O2
    o2_val = latest['o2_percent']
    o2_class = "metric-value-critical" if o2_val <= THRESHOLDS['o2_critical'] else "metric-value-caution" if o2_val <= THRESHOLDS['o2_caution'] else "metric-value-safe"
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #94a3b8; font-family: monospace;">OXYGEN (O2)</div>
            <div class="{o2_class}">{o2_val:.2f} <span style="font-size: 14px;">%</span></div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Min Breathable: 19.5% Vol</div>
        </div>
        """, unsafe_allow_html=True)

    # 6. Ultrasonic Roof Clearance
    dist_val = latest['distance_cm']
    dist_class = "metric-value-critical" if dist_val < THRESHOLDS['dist_critical'] else "metric-value-caution" if dist_val < THRESHOLDS['dist_caution'] else "metric-value-safe"
    with col6:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #94a3b8; font-family: monospace;">TUNNEL ROOF CLEARANCE</div>
            <div class="{dist_class}">{dist_val:.1f} <span style="font-size: 14px;">cm</span></div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">Caution: &lt;180cm • Collapse: &lt;100cm</div>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# TAB 4: INCIDENT PROTOCOL & LEAK LOCATIONS
# ==============================================================================
with tab_incidents:
    st.markdown("### Active Incident Protocol & Subsurface Gas Leak Locations")

    # Real-time Location Cards
    st.subheader("📍 Detected Subsurface Fracture Locations")
    
    loc_col1, loc_col2 = st.columns(2)
    with loc_col1:
        st.markdown(f"""
        <div style="background: #111a2e; border: 1px solid {'#ef4444' if sos_active else '#1e293b'}; border-radius: 10px; padding: 14px;">
            <div style="color: {'#ef4444' if sos_active else '#10b981'}; font-weight: bold; font-family: monospace;">
                PRIMARY FRACTURE: SECTOR 4 SUB-LEVEL B
            </div>
            <div style="font-size: 12px; color: #94a3b8; font-family: monospace; margin-top: 6px;">
                • Elevation Depth: -420 meters<br>
                • Associated Node: NODE-01<br>
                • Detected Gas: Combustible Methane (CH4) & Monoxide (CO)<br>
                • Mitigation Protocol: High-volume ventilation exhaust bypass #4
            </div>
        </div>
        """, unsafe_allow_html=True)

    with loc_col2:
        st.markdown("""
        <div style="background: #111a2e; border: 1px solid #1e293b; border-radius: 10px; padding: 14px;">
            <div style="color: #38bdf8; font-weight: bold; font-family: monospace;">
                SECONDARY DRIFT: SECTOR 2 LEVEL 300
            </div>
            <div style="font-size: 12px; color: #94a3b8; font-family: monospace; margin-top: 6px;">
                • Elevation Depth: -300 meters<br>
                • Associated Node: NODE-02<br>
                • Status: Shore shoring operations underway by Team Bravo<br>
                • Atmospheric Condition: Nominal (20.88% O2)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Incident Event Log")

    if st.session_state.alerts:
        df_alerts = pd.DataFrame(st.session_state.alerts)
        st.dataframe(df_alerts, use_container_width=True)
        
        # CSV Export Option
        csv_data = df_alerts.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Incident Log (CSV)",
            data=csv_data,
            file_name=f"MRSMS_Incident_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No active hazardous incident alerts logged. Mine atmospheric state is within safe standard thresholds.")
