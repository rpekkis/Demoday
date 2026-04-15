import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import os

st.set_page_config(page_title="NeuroFlight™ Tactical Command", layout="wide", initial_sidebar_state="collapsed")

# --- KONFIGURAATIO ---
MISSION_DURATION_SECS = 180  # Lyhennetty demoa varten (3 min)
UPDATE_SPEED_HZ = 0.1       # Päivitysnopeus (sekunteina)
BODY_IMAGE_FILE = "body_outline.png" # Tallenna kuva tällä nimellä!

# --- REALISTINEN LENTOPROFIILI ---
def get_mission_g(t):
    if t < 15: return 1.0 # Taxi
    elif t < 40: return 3.5 + 1.2 * np.sin(t/3) # Basic Maneuvers
    elif t < 70: return 1.5 # Level Flight
    elif t < 110: return 6.5 + 2.5 * np.sin(t/8) # Combat (4-9G)
    elif t < 150: return 5.0 # Sustained High-G Turn
    elif t < 170: return 9.0 - (t-150)*0.2 # G-Onset Peak to descent
    else: return 1.2 # Approach

# --- WEARABLE SENSORI-SIMULAATIO ---
def get_muscle_data(current_g):
    # Lihasrasitus kasvaa jyrkästi (kaava: G^1.8 * kerroin)
    base = (current_g ** 1.8) * 1.5
    
    # Pakotetaan arvot välille 0-100
    strains = {
        "Neck": int(np.clip(base * 1.3 + np.random.randint(-2, 2), 0, 100)),
        "Back": int(np.clip(base * 1.1 + np.random.randint(-1, 2), 0, 100)),
        "Core": int(np.clip(base * 1.0 + np.random.randint(-3, 5), 0, 100)),
        "Glutes": int(np.clip(base * 0.9 + np.random.randint(-2, 2), 0, 100)),
        "Quads": int(np.clip(base * 1.2 + np.random.randint(-2, 4), 0, 100))
    }
    return strains

# --- HEATMAP VÄRILOGIIKKA ---
def get_heatmap_color(strain_percent):
    # Vihreä (0, 255, 0) -> Keltainen (255, 255, 0) -> Punainen (255, 0, 0)
    if strain_percent < 50:
        # 0% (Vihreä) -> 50% (Keltainen)
        r = int((strain_percent / 50) * 255)
        g = 255
        b = 0
    else:
        # 50% (Keltainen) -> 100% (Punainen)
        r = 255
        g = int(255 - ((strain_percent - 50) / 50) * 255)
        b = 0
    return f'rgb({r}, {g}, {b})'

# --- UI LAYOUT ---
st.title("🛡️ NeuroFlight™ Tactical Command Center")
st.write("Live Physiological Telemetry from Smart-FR Layer™ vs. Aircraft Dynamics")

col1, col2 = st.columns([1.2, 2])

with col1:
    st.subheader("Biological Heatmap")
    body_placeholder = st.empty() # Placeholder vartalolle
    
    st.markdown("---")
    st.subheader("Physical Strain (%)")
    # Palkit ja tekstit
    n_l = st.empty(); n_b = st.progress(0.0)
    b_l = st.empty(); b_b = st.progress(0.0)
    c_l = st.empty(); c_b = st.progress(0.0)
    g_l = st.empty(); g_b = st.progress(0.0)
    q_l = st.empty(); q_b = st.progress(0.0)

with col2:
    st.subheader("Tactical Mission Data (Dual Axis)")
    telemetry_placeholder = st.empty() # Placeholder G-käyrälle
    
    st.markdown("---")
    st.subheader("Current Status")
    g_metric = st.empty()
    alert_status = st.empty()

# --- ANIMATION LOOP ---
if st.button('▶️ START REAL-TIME MISSION TELEMETRY'):
    # Alustetaan histogrammin data
    time_hist = []
    g_hist = []
    back_emg_hist = []

    # Ladataan vartalokuva (jos olemassa)
    if os.path.exists(BODY_IMAGE_FILE):
        img_outline = Image.open(BODY_IMAGE_FILE)
    else:
        st.error(f"Error: {BODY_IMAGE_FILE} not found. Dynamic Heatmap disabled.")
        img_outline = None

    for t in range(MISSION_DURATION_SECS):
        current_g = get_mission_g(t)
        strains = get_muscle_data(current_g)
        
        # Päivitetään historiadata
        time_hist.append(t)
        g_hist.append(current_g)
        back_emg_hist.append(strains["Back"])

        # 1. PÄIVITETÄÄN VARTALO-HEATMAP (Plotly go.Image + go.Scatter overlays)
        if img_outline:
            heatmap_fig = go.Figure()
            
            # Lisätään pohjapiirros
            heatmap_fig.add_trace(go.Image(z=np.array(img_outline)))
            
            # Lisätään lihashatmap-kerrokset (ympyrät, jotka muuttavat väriä)
            # Koordinaatit (x, y) pitää säätää vastaamaan body_outline.png:tä!
            muscle_locs = {
                "Neck": [250, 80], "Back": [250, 220], "Core": [250, 180],
                "Glutes": [250, 280], "Quads": [250, 380]
            }
            
            for muscle, loc in muscle_locs.items():
                strain = strains[muscle]
                heatmap_fig.add_trace(go.Scatter(
                    x=[loc[0]], y=[loc[1]],
                    mode='markers',
                    marker=dict(size=40, color=get_heatmap_color(strain), line=dict(width=2, color='black')),
                    name=f"{muscle} Heatmap"
                ))
            
            heatmap_fig.update_layout(
                template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, autorange='reversed')
            )
            body_placeholder.plotly_chart(heatmap_fig, use_container_width=True)

        # 2. PÄIVITETÄÄN PALKIT (Numeeriset prosentin 0-100)
        n_l.write(f"Cervical (Neck): **{strains['Neck']}%**"); n_b.progress(strains['Neck'] / 100.0)
        b_l.write(f"Lumbar (Lower Back): **{strains['Back']}%**"); b_b.progress(strains['Back'] / 100.0)
        c_l.write(f"Abdominal (Core): **{strains['Core']}%**"); c_b.progress(strains['Core'] / 100.0)
        g_l.write(f"Gluteus (Buttocks): **{strains['Glutes']}%**"); g_b.progress(strains['Glutes'] / 100.0)
        q_l.write(f"Quadriceps (Thighs): **{s['Quads']}%**"); q_b.progress(strains['Quads'] / 100.0)
        
        # 3. PÄIVITETÄÄN KAKSI-AKSELINEN G-KÄYRÄ (Plotly Subplots)
        tele_fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # G-voima (Vasen akseli, Syaani viiva)
        tele_fig.add_trace(go.Scatter(x=time_hist, y=g_hist, name="Aircraft G-Load", line=dict(color='cyan', width=2)), secondary_y=False)
        
        # Lihasrasitus (Oikea akseli, Punainen viiva)
        tele_fig.add_trace(go.Scatter(x=time_hist, y=back_emg_hist, name="Lower Back EMG (%)", line=dict(color='red', dash='dot')), secondary_y=True)
        
        # Asetukset akseleille
        tele_fig.update_layout(template="plotly_dark", height=450, xaxis_title="Mission Time (s)")
        tele_fig.update_yaxes(title_text="G-Force (G)", range=[0.5, 9.5], secondary_y=False, tickfont=dict(color='cyan'))
        tele_fig.update_yaxes(title_text="Muscle Activation (% MVC)", range=[0, 105], secondary_y=True, tickfont=dict(color='red'))
        
        telemetry_placeholder.plotly_chart(tele_fig, use_container_width=True)

        # 4. METRIIKAT JA HÄLYTYKSET
        g_metric.metric("G-FORCE", f"{current_g:.1f} G", delta=f"T+{t}s")
        
        if stains['Back'] > 85:
            alert_status.error(f"⚠️ CRITICAL: Spinal Load >85%. G-LOC Risk: HIGH.")
        elif current_g > 7:
            alert_status.warning(f"⚡ WARNING: Sustained High G-Load.")
        else:
            alert_status.success(f"✅ Physiological State: Stable.")

        time.sleep(UPDATE_SPEED_HZ)
else:
    st.info("System Ready. Smart-FR Layer™ Connected (Simulated).")
