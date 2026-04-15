import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import os

st.set_page_config(page_title="NeuroFlight™ Tactical Command Center", layout="wide", initial_sidebar_state="collapsed")

# --- KONFIGURAATIO ---
MISSION_DURATION_SECS = 180  # Lyhennetty demoa varten (3 min)
UPDATE_SPEED_HZ = 0.1       # Päivitysnopeus (10Hz)
BODY_IMAGE_FILE = "body_outline.png" # MUISTA TALLENTAA KUVA TÄLLÄ NIMELLÄ!

# --- REALISTINEN LENTOPROFIILI (Mission Scenarios) ---
def get_mission_g(t):
    if t < 15: return 1.0 # Taxi
    elif t < 40: return 3.5 + 1.2 * np.sin(t/3) # Basic Maneuvers
    elif t < 70: return 1.5 # Level Flight
    elif t < 110: return 6.5 + 2.5 * np.sin(t/8) # Combat (4-9G)
    elif t < 150: return 5.0 # Sustained High-G Turn
    elif t < 170: return 8.5 - (t-150)*0.2 # G-Onset Peak to descent
    else: return 1.2 # Approach

# --- HEATMAP VÄRILOGIIKKA (Vihreä -> Keltainen -> Punainen) ---
def get_heatmap_color(strain_percent):
    if strain_percent < 50:
        # Vihreä (0,255,0) -> Keltainen (255,255,0)
        r = int((strain_percent / 50) * 255)
        g = 255
    else:
        # Keltainen (255,255,0) -> Punainen (255,0,0)
        r = 255
        g = int(255 - ((strain_percent - 50) / 50) * 255)
    return f'rgb({r}, {g}, 0)'

# --- UI LAYOUT ---
st.title("🛡️ NeuroFlight™ Tactical Command Center")
st.write("Live Physiological Telemetry from Smart-FR Layer™ vs. Aircraft Dynamics")

col1, col2 = st.columns([1.2, 2]) # Vartalo vasemmalle, data oikealle

with col1:
    st.subheader("Biological Heatmap")
    body_placeholder = st.empty() # Placeholder isolle dynaamiselle vartalolle

with col2:
    st.subheader("Tactical Mission Data (Dual Axis)")
    telemetry_placeholder = st.empty() # Placeholder kaksiakseliselle G-käyrälle
    
    st.markdown("---")
    # Alhaalla metriikat
    m_col1, m_col2, m_col3 = st.columns(3)
    g_metric = m_col1.empty()
    back_metric = m_col2.empty()
    status_metric = m_col3.empty()

# --- ANIMATION LOOP ---
if st.button('▶️ START REAL-TIME MISSION TELEMETRY'):
    # Alustetaan historiadata
    time_hist, g_hist, back_emg_hist = [], [], []
    
    # Ladataan vartalokuva (jos olemassa)
    if os.path.exists(BODY_IMAGE_FILE):
        img_outline = Image.open(BODY_IMAGE_FILE)
        img_width, img_height = img_outline.size
    else:
        st.error(f"Error: {BODY_IMAGE_FILE} not found. Please save the diagram first.")
        st.stop() # Pysäytetään, jos kuvaa ei löydy

    # Alustetaan Plotly Figure (Kaksiakselinen)
    tele_fig = make_subplots(specs=[[{"secondary_y": True}]])
    tele_fig.update_layout(template="plotly_dark", height=450, xaxis_title="Mission Time (s)")
    tele_fig.update_yaxes(title_text="G-Force (G)", range=[0, 10], secondary_y=False, tickfont=dict(color='cyan'))
    tele_fig.update_yaxes(title_text="Muscle Activation (%)", range=[0, 105], secondary_y=True, tickfont=dict(color='red'))

    for t in range(MISSION_DURATION_SECS):
        current_g = get_mission_g(t)
        
        # WEARABLE SENSORI-SIMULAATIO
        base = (current_g ** 1.8) * 1.5
        strains = {
            "Neck": int(np.clip(base * 1.3 + np.random.randint(-2, 2), 0, 100)),
            "Back": int(np.clip(base * 1.1 + np.random.randint(-1, 2), 0, 100)),
            "Core": int(np.clip(base * 1.0 + np.random.randint(-3, 5), 0, 100)),
            "Glutes": int(np.clip(base * 0.9 + np.random.randint(-2, 2), 0, 100)),
            "Quads": int(np.clip(base * 1.2 + np.random.randint(-2, 4), 0, 100))
        }
        
        # Päivitetään historiadata
        time_hist.append(t); g_hist.append(current_g); back_emg_hist.append(strains["Back"])

        # 1. PÄIVITETÄÄN DYNAAMINEN VARTALO-HEATMAP
        heatmap_fig = go.Figure()
        heatmap_fig.add_trace(go.Image(z=np.array(img_outline))) # Pohjakuva
        
        # Lihaskoordinaatit (x, y) - Säädä nämä vastaamaan body_outline.png:tä!
        muscle_locs = {
            "Neck": [450, 150], "Back": [780, 450], "Core": [450, 400],
            "Glutes": [780, 580], "Quads": [450, 750]
        }
        
        for muscle, loc in muscle_locs.items():
            strain = strains[muscle]
            heatmap_fig.add_trace(go.Scatter(
                x=[loc[0]], y=[loc[1]],
                mode='markers',
                marker=dict(size=50, color=get_heatmap_color(strain), line=dict(width=2, color='white')),
                showlegend=False
            ))
        
        # Heatmap-asetukset
        heatmap_fig.update_layout(
            template="plotly_dark", height=600, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, autorange='reversed')
        )
        body_placeholder.plotly_chart(heatmap_fig, use_container_width=True)

        # 2. PÄIVITETÄÄN DYNAAMINEN KAKSI-AKSELINEN G-KÄYRÄ (Optimoidusti)
        # Poistetaan vanhat ja lisätään uudet, jotta vilkkuminen minimoidaan
        tele_fig.data = [] 
        tele_fig.add_trace(go.Scatter(x=time_hist, y=g_hist, name="Aircraft G-Load", line=dict(color='cyan', width=2.5)), secondary_y=False)
        tele_fig.add_trace(go.Scatter(x=time_hist, y=back_emg_hist, name="Lower Back EMG (%)", line=dict(color='red', dash='dot')), secondary_y=True)
        telemetry_placeholder.plotly_chart(tele_fig, use_container_width=True)

        # 3. METRIIKAT JA HÄLYTYKSET
        g_metric.metric("Current Load", f"{current_g:.1f} G", delta=f"T+{t}s")
        back_metric.metric("Lower Back EMG", f"{strains['Back']}%", delta=f"{current_g:.1f}G Load", delta_color="inverse")
        
        if strains['Back'] > 85:
            status_metric.error("⚠️ CRITICAL: Spinal Load >85%.")
        elif current_g > 7:
            status_metric.warning("⚡ WARNING: Sustained High G.")
        else:
            status_metric.success("✅ Physiological State: Stable.")

        time.sleep(UPDATE_SPEED_HZ)
else:
    st.info("System Ready. Smart-FR Layer™ Connected (Simulated). Click Start.")
