import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ Mission Analytics", layout="wide")

# --- DATASETIN SIMULAATIO (5 minuutin taistelu) ---
def generate_mission_data():
    # 300 sekuntia (5 min), päivitys 1s välein
    seconds = np.arange(0, 301)
    # G-voimat: Partiointi (1G), Takaa-ajo (4-6G), Tiukka kaarto (7-9G)
    g_profile = 1.0 + 1.5 * np.sin(seconds / 20) + 0.5 * np.random.normal(0, 0.2, len(seconds))
    # Lisätään muutama "High-G spike" (Dogfight)
    g_profile[40:60] += 5.0
    g_profile[120:160] += 6.5
    g_profile[220:250] += 4.0
    return seconds, np.clip(g_profile, 1.0, 9.0)

time_steps, g_values = generate_mission_data()

# --- UI ELEMENTIT ---
st.title("🛡️ NeuroFlight™: Mission Replay Analysis")
st.write("Automatic monitoring of Pilot Physiological Integrity during Air Combat Maneuvers (ACM).")

col1, col2 = st.columns([1, 2])

# Simuloidaan lihasryhmiä
muscle_groups = ['Neck', 'Upper Traps', 'Lower Back', 'Core', 'Left Quad', 'Right Quad']

def get_muscle_strain(g_load):
    # Eri lihakset reagoivat eri tavalla
    neck = min(100, (g_load * 12) + np.random.randint(-5, 5))
    back = min(100, (g_load * 10) + np.random.randint(-3, 3))
    others = min(100, (g_load * 8) + np.random.randint(-2, 2))
    return [neck, others, back, others, others, others]

# --- ANIMATION LOOP ---
if st.button('▶️ Start Mission Playback'):
    progress_bar = st.progress(0)
    status_text = st.empty()
    chart_placeholder = st.empty()
    
    # Placeholderit heatmapille ja vartalolle
    with col1:
        st.info("Biological Heatmap")
        body_placeholder = st.empty()
        
    with col2:
        st.info("Live G-Load & EMG Telemetry")
        telemetry_placeholder = st.empty()

    for t in range(len(time_steps)):
        current_g = g_values[t]
        strains = get_muscle_strain(current_g)
        
        # Päivitetään edistyminen
        progress_bar.progress(t / len(time_steps))
        status_text.text(f"Mission Time: {t}s | Current Load: {current_g:.1f} G")

        # 1. Heatmap (Palkit edustavat lihaksia)
        fig = go.Figure(go.Bar(
            x=muscle_groups,
            y=strains,
            marker=dict(color=strains, colorscale='Reds', cmin=0, cmax=100)
        ))
        fig.update_layout(template="plotly_dark", height=300, yaxis_range=[0,105])
        body_placeholder.plotly_chart(fig, use_container_width=True)

        # 2. Telemetria-käyrä (G-voima ja Selän EMG rinnakkain)
        tele_fig = go.Figure()
        tele_fig.add_trace(go.Scatter(x=time_steps[:t], y=g_values[:t], name="G-Load", line=dict(color='cyan')))
        tele_fig.add_trace(go.Scatter(x=time_steps[:t], y=[get_muscle_strain(g)[2] for g in g_values[:t]], 
                                     name="Lower Back EMG (%)", line=dict(color='red', dash='dot')))
        
        tele_fig.update_layout(template="plotly_dark", height=400, title="Real-time Flight Data")
        telemetry_placeholder.plotly_chart(tele_fig, use_container_width=True)

        # Hidastetaan päivitystä (esim. 0.3s välein on silmälle miellyttävä)
        time.sleep(0.3)
else:
    st.write("Click 'Start' to visualize the simulated 5-minute combat engagement.")
