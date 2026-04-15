import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import pandas as pd

# Sivun asetukset
st.set_page_config(page_title="NeuroFlight™ Analytics Demo", layout="wide")

st.title("🚀 NeuroFlight™ Analytics - Real-time Bio-Monitoring")
st.subheader("Human Attrition & G-Load Diagnostics")

# Sivupalkki ohjausta varten
st.sidebar.header("Simulation Controls")
g_force = st.sidebar.slider("G-Force Load", 1.0, 9.0, 1.0, 0.5)
is_flying = st.sidebar.checkbox("Live Telemetry Stream", value=True)

# Simuloidaan lihasryhmiä
muscle_groups = [
    'Lower Back (L1-L5)', 'Upper Back (Trapezius)', 
    'Neck (Cervical)', 'Quads (Left)', 'Quads (Right)', 'Core/Abs'
]

# Funktio heatmapin luomiseen
def create_heatmap(g_load):
    # Simuloidaan rasitusta: Base strain + (G-force * kerroin) + kohina
    strain_values = [
        min(100, (g_load * 10) + np.random.randint(5, 15)) if i == 0 else # Selkä kovemmilla
        min(100, (g_load * 8) + np.random.randint(2, 10)) 
        for i in range(len(muscle_groups))
    ]
    
    fig = go.Figure(data=[go.Bar(
        x=muscle_groups,
        y=strain_values,
        marker=dict(
            color=strain_values,
            colorscale='YlOrRd', # Keltainen -> Oranssi -> Punainen
            showscale=True,
            cmin=0,
            cmax=100
        )
    )])
    
    fig.update_layout(
        title=f"Muscle Activation Intensity at {g_load}G",
        yaxis=dict(title="Activation Level (%)", range=[0, 110]),
        template="plotly_dark",
        height=400
    )
    return fig, strain_values

# Dashboardin asettelu
col1, col2 = st.columns([2, 1])

with col1:
    heatmap_placeholder = st.empty()
    chart_placeholder = st.empty()

with col2:
    st.metric("System Status", "ACTIVE", delta="FR-Layer Connected")
    st.metric("Pilot Fatigue Index", f"{int(g_force * 11)}%", delta="High Risk" if g_force > 6 else "Optimal")
    
    st.write("### Critical Alerts")
    if g_force > 7:
        st.error("⚠️ CRITICAL: Lower Back Strain exceeding 85%")
    elif g_force > 5:
        st.warning("⚡ WARNING: Sustained High G-Load")
    else:
        st.success("✅ Pilot physiological state: Stable")

# Simulaatio-looppi
history = []

for i in range(100 if is_flying else 1):
    fig, current_values = create_heatmap(g_force)
    
    with heatmap_placeholder:
        st.plotly_chart(fig, use_container_width=True)
    
    # Historiadata käyrää varten
    history.append(current_values[0]) # Seurataan alaselkää
    if len(history) > 20: history.pop(0)
    
    with chart_placeholder:
        st.line_chart(pd.DataFrame(history, columns=["Lower Back EMG Signal"]))
    
    if is_flying:
        time.sleep(0.5)
    else:
        break
