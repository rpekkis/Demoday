import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ Tactical Command", layout="wide", initial_sidebar_state="collapsed")

# --- REALISTINEN LENTOPROFIILI (Mission Scenarios) ---
def get_mission_g(t):
    if t < 20: return 1.0 # Taxi & Takeoff
    elif t < 60: return 3.0 + 1.0 * np.sin(t/5) # Basic Maneuvers (3-4G)
    elif t < 100: return 1.5 # Straight & Level
    elif t < 160: return 6.0 + 2.5 * np.sin(t/10) # High-G Combat (4-8.5G)
    elif t < 200: return 4.5 # Sustained Turn (4-5G)
    elif t < 250: return 8.5 - (t-220)*0.1 # G-Onset Test
    else: return 1.2 # Landing approach

# --- UI ASETUKSET ---
st.title("🛡️ NeuroFlight™ Tactical Analytics")
st.write("Live Bio-Telemetry: Pilot Musculoskeletal Load vs. Flight Dynamics")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Physical Strain (%)")
    # Luodaan placeholderit kaikille lihasryhmille
    neck_label = st.empty()
    neck_bar = st.progress(0)
    
    back_label = st.empty()
    back_bar = st.progress(0)
    
    core_label = st.empty()
    core_bar = st.progress(0)
    
    glute_label = st.empty()
    glute_bar = st.progress(0)
    
    quad_label = st.empty()
    quad_bar = st.progress(0)
    
    st.markdown("---")
    g_metric = st.empty()

with col2:
    st.subheader("Mission Data Stream")
    # Alustetaan tyhjä dataikkuna
    chart_data = pd.DataFrame(columns=["Aircraft G-Load", "Muscle Activation (%)"])
    line_chart = st.line_chart(chart_data)
    
    st.info("💡 Technical Note: EMG signals are normalized to Pilot's Maximum Voluntary Contraction (MVC).")

# --- ANIMATION LOOP ---
if st.button('▶️ START MISSION TELEMETRY'):
    # Luodaan lista historiadataa varten, jotta se piirtyy nätisti
    history = []
    
    for t in range(300): # 5 minuutin simulaatio
        current_g = get_mission_g(t)
        
        # Realistinen lihas-aktivointi logiikka (EMG % MVC)
        # G-voima vaatii eksponentiaalisesti enemmän työtä korkeilla tasoilla
        base_strain = (current_g ** 1.8) * 1.5 
        
        # Lihaskohtaiset kertoimet + pieni satunnaisvaihtelu
        strains = {
            "Neck": min(100, int(base_strain * 1.3 + np.random.randint(-2, 2))),
            "Back": min(100, int(base_strain * 1.1 + np.random.randint(-1, 2))),
            "Core": min(100, int(base_strain * 1.0 + np.random.randint(-3, 5))),
            "Glutes": min(100, int(base_strain * 0.9 + np.random.randint(-2, 2))),
            "Quads": min(100, int(base_strain * 1.2 + np.random.randint(-2, 4)))
        }

        # 1. Päivitetään Numeeriset tekstit ja Mittarit (Asteikko 0-100%)
        neck_label.write(f"Cervical (Neck): **{strains['Neck']}%**")
        neck_bar.progress(strains['Neck'] / 100)
        
        back_label.write(f"Lumbar (Lower Back): **{strains['Back']}%**")
        back_bar.progress(strains['Back'] / 100)
        
        core_label.write(f"Abdominal (Core): **{strains['Core']}%**")
        core_bar.progress(strains['Core'] / 100)
        
        glute_label.write(f"Gluteus (Buttocks): **{strains['Glutes']}%**")
        glute_bar.progress(strains['Glutes'] / 100)
        
        quad_label.write(f"Quadriceps (Thighs): **{strains['Quads']}%**")
        quad_bar.progress(strains['Quads'] / 100)
        
        # 2. Päivitetään G-mittari
        g_metric.metric("G-FORCE", f"{current_g:.1f} G", delta=f"{t}s Mission Time")

        # 3. Päivitetään viivakaavio (Line Chart)
        # Skaalataan lihasdata välille 0-10 (jotta se näkyy samalla asteikolla G-voiman kanssa)
        new_entry = pd.DataFrame({
            "Aircraft G-Load": [current_g],
            "Muscle Activation (%)": [strains['Back'] / 10] 
        })
        line_chart.add_rows(new_entry)

        # Simulaation nopeus (0.1s = 10Hz päivitys, tuntuu erittäin sulavalta)
        time.sleep(0.1)
else:
    st.warning("Awaiting Signal from Smart-FR Layer... Click Start.")
