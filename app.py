import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import os

st.set_page_config(page_title="NeuroFlight™ Tactical Command", layout="wide")

# --- ALUSTUS (Estää NameErrorit) ---
if 'strains' not in st.session_state:
    st.session_state['strains'] = {"Neck": 0, "Back": 0, "Core": 0, "Glutes": 0, "Quads": 0}

# --- REALISTINEN LENTOPROFIILI ---
def get_mission_g(t):
    if t < 15: return 1.0
    elif t < 40: return 3.5 + 1.2 * np.sin(t/3)
    elif t < 70: return 1.5
    elif t < 110: return 6.5 + 2.5 * np.sin(t/8)
    elif t < 150: return 5.0
    elif t < 170: return 9.0 - (t-150)*0.2
    else: return 1.2

# --- UI LAYOUT ---
st.title("🛡️ NeuroFlight™ Tactical Command Center")
col1, col2 = st.columns([1.2, 2])

with col1:
    st.subheader("Biological Heatmap")
    body_placeholder = st.empty()
    st.markdown("---")
    st.subheader("Physical Strain (%)")
    n_l = st.empty(); n_b = st.progress(0.0)
    b_l = st.empty(); b_b = st.progress(0.0)
    c_l = st.empty(); c_b = st.progress(0.0)
    g_l = st.empty(); g_b = st.progress(0.0)
    q_l = st.empty(); q_b = st.progress(0.0)

with col2:
    st.subheader("Tactical Mission Data (Dual Axis)")
    telemetry_placeholder = st.empty()
    st.markdown("---")
    st.subheader("Current Status")
    g_metric = st.empty()
    alert_status = st.empty()

# --- ANIMATION LOOP ---
if st.button('▶️ START REAL-TIME MISSION TELEMETRY'):
    time_hist, g_hist, back_emg_hist = [], [], []
    
    for t in range(180):
        current_g = get_mission_g(t)
        
        # Lasketaan uudet arvot
        base = (current_g ** 1.8) * 1.5
        strains = {
            "Neck": int(np.clip(base * 1.3 + np.random.randint(-2, 2), 0, 100)),
            "Back": int(np.clip(base * 1.1 + np.random.randint(-1, 2), 0, 100)),
            "Core": int(np.clip(base * 1.0 + np.random.randint(-3, 5), 0, 100)),
            "Glutes": int(np.clip(base * 0.9 + np.random.randint(-2, 2), 0, 100)),
            "Quads": int(np.clip(base * 1.2 + np.random.randint(-2, 4), 0, 100))
        }
        
        # Tallennetaan session_stateen, jotta NameError vältetään
        st.session_state['strains'] = strains
        time_hist.append(t); g_hist.append(current_g); back_emg_hist.append(strains["Back"])

        # 1. Päivitetään palkit
        n_l.write(f"Cervical (Neck): **{strains['Neck']}%**"); n_b.progress(strains['Neck'] / 100.0)
        b_l.write(f"Lumbar (Lower Back): **{strains['Back']}%**"); b_b.progress(strains['Back'] / 100.0)
        c_l.write(f"Abdominal (Core): **{strains['Core']}%**"); c_b.progress(strains['Core'] / 100.0)
        g_l.write(f"Gluteus (Buttocks): **{strains['Glutes']}%**"); g_b.progress(strains['Glutes'] / 100.0)
        q_l.write(f"Quadriceps (Thighs): **{strains['Quads']}%**"); q_b.progress(strains['Quads'] / 100.0)

        # 2. Plotly Subplot (Dual Axis)
        tele_fig = make_subplots(specs=[[{"secondary_y": True}]])
        tele_fig.add_trace(go.Scatter(x=time_hist, y=g_hist, name="G-Load", line=dict(color='cyan')), secondary_y=False)
        tele_fig.add_trace(go.Scatter(x=time_hist, y=back_emg_hist, name="Back EMG %", line=dict(color='red', dash='dot')), secondary_y=True)
        tele_fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=30,b=0))
        tele_fig.update_yaxes(title_text="G-Force", range=[0, 10], secondary_y=False)
        tele_fig.update_yaxes(title_text="EMG %", range=[0, 110], secondary_y=True)
        telemetry_placeholder.plotly_chart(tele_fig, use_container_width=True)

        # 3. Metriikat ja Hälytykset (Käytetään sanakirjaa turvallisesti)
        g_metric.metric("G-FORCE", f"{current_g:.1f} G", delta=f"T+{t}s")
        
        if strains['Back'] > 85:
            alert_status.error("⚠️ CRITICAL: Spinal Load >85%.")
        elif current_g > 7:
            alert_status.warning("⚡ WARNING: Sustained High G.")
        else:
            alert_status.success("✅ Physiological State: Stable.")

        time.sleep(0.1)
