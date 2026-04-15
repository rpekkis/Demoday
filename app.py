import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ Tactical Analytics", layout="wide")

# --- REALISTINEN LENTOPROFIILI ---
def get_mission_g(t):
    if t < 20: return 1.0 
    elif t < 60: return 3.0 + 1.0 * np.sin(t/5)
    elif t < 100: return 1.5 
    elif t < 160: return 6.0 + 2.5 * np.sin(t/10)
    elif t < 200: return 4.5 
    elif t < 250: return 8.5 - (t-220)*0.1 
    else: return 1.2 

st.title("🛡️ NeuroFlight™ Tactical Analytics")
st.write("Live Bio-Telemetry: Pilot Musculoskeletal Load vs. Flight Dynamics")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Physical Strain (%)")
    # Placeholderit labelille ja palkille
    n_l = st.empty(); n_b = st.progress(0.0)
    b_l = st.empty(); b_b = st.progress(0.0)
    c_l = st.empty(); c_b = st.progress(0.0)
    g_l = st.empty(); g_b = st.progress(0.0)
    q_l = st.empty(); q_b = st.progress(0.0)
    
    st.markdown("---")
    g_metric = st.empty()

with col2:
    st.subheader("Mission Data Stream")
    line_chart = st.line_chart(pd.DataFrame(columns=["Aircraft G-Load", "Muscle Stress (normalized)"]))

# --- ANIMATION LOOP ---
if st.button('▶️ START MISSION TELEMETRY'):
    for t in range(300):
        current_g = get_mission_g(t)
        
        # Kaava: G-voima potenssiin 1.8 (fyysinen rasitus nousee jyrkästi)
        base = (current_g ** 1.8) * 1.5
        
        # Lasketaan raaka-arvot (0-100) ja pakotetaan ne välille 0-100 np.clipillä
        s = {
            "Neck": int(np.clip(base * 1.3 + np.random.randint(-2, 2), 0, 100)),
            "Back": int(np.clip(base * 1.1 + np.random.randint(-1, 2), 0, 100)),
            "Core": int(np.clip(base * 1.0 + np.random.randint(-3, 5), 0, 100)),
            "Glutes": int(np.clip(base * 0.9 + np.random.randint(-2, 2), 0, 100)),
            "Quads": int(np.clip(base * 1.2 + np.random.randint(-2, 4), 0, 100))
        }

        # PÄIVITYKSET (progress vaatii arvon 0.0 - 1.0)
        n_l.write(f"Cervical (Neck): **{s['Neck']}%**")
        n_b.progress(s['Neck'] / 100.0)
        
        b_l.write(f"Lumbar (Lower Back): **{s['Back']}%**")
        b_b.progress(s['Back'] / 100.0)
        
        c_l.write(f"Abdominal (Core): **{s['Core']}%**")
        c_b.progress(s['Core'] / 100.0)
        
        g_l.write(f"Gluteus (Buttocks): **{s['Glutes']}%**")
        g_b.progress(s['Glutes'] / 100.0)
        
        q_l.write(f"Quadriceps (Thighs): **{s['Quads']}%**")
        q_b.progress(s['Quads'] / 100.0)
        
        g_metric.metric("G-FORCE", f"{current_g:.1f} G", delta=f"T+{t}s")

        # Viivakaavio (add_rows on smoothimpi)
        line_chart.add_rows(pd.DataFrame({
            "Aircraft G-Load": [current_g],
            "Muscle Stress (normalized)": [s['Back'] / 10.0] 
        }))

        time.sleep(0.1)
else:
    st.info("System Ready. Smart-FR Layer Connected.")
