import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ High-Speed Telemetry", layout="wide")

# --- REALISTINEN LENTOPROFIILI ---
def get_mission_g(t):
    if t < 20: return 1.0 
    elif t < 60: return 3.0 + 2.0 * np.sin(t/5)
    elif t < 100: return 1.5 
    elif t < 160: return 6.5 + 2.5 * np.sin(t/8)
    else: return 4.0 + np.cos(t/10)

def get_color(val):
    r = int(np.clip((val / 50) * 255, 0, 255))
    g = int(np.clip(255 - ((val - 50) / 50) * 255 if val > 50 else 255, 0, 255))
    return f"rgb({r}, {g}, 0)"

st.title("🛡️ NeuroFlight™ Real-Time Mission Control")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Biological Heatmap")
    # Luodaan visuaaliset "sensoripisteet" isolla fontilla
    h_places = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}
    st.markdown("---")
    g_metric = st.empty()
    status_msg = st.empty()

with col2:
    st.subheader("Flight Dynamics (G-Load)")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force"]), height=250)
    
    st.subheader("Physiological Response (EMG %)")
    emg_chart = st.line_chart(pd.DataFrame(columns=["Muscle Activation %"]), height=250)

# --- ANIMATION LOOP ---
if st.button('▶️ START SUPER-SMOOTH TELEMETRY'):
    # Käytetään listoja keräämään dataa
    for t in range(250):
        current_g = get_mission_g(t)
        
        # Lihasrasituskaava
        base = (current_g ** 1.8) * 1.5
        strains = {
            "Neck": int(np.clip(base * 1.3, 0, 100)),
            "Back": int(np.clip(base * 1.1, 0, 100)),
            "Core": int(np.clip(base * 1.0, 0, 100)),
            "Glutes": int(np.clip(base * 0.9, 0, 100)),
            "Quads": int(np.clip(base * 1.2, 0, 100))
        }

        # 1. PÄIVITETÄÄN HEATMAP (HTML on nopein)
        for muscle, val in strains.items():
            color = get_color(val)
            h_places[muscle].markdown(
                f"""<div style="background-color: #1e1e1e; padding: 10px; border-radius: 10px; border-left: 10px solid {color}; margin-bottom: 5px;">
                    <span style="font-size: 14px; color: gray;">{muscle.upper()}</span><br>
                    <span style="font-size: 24px; font-weight: bold; color: white;">{val}%</span>
                </div>""", unsafe_allow_html=True
            )

        # 2. PÄIVITETÄÄN KAAVIOT (add_rows on Streamlitin nopein tapa)
        # Nämä piirtyvät pikkuhiljaa vasemmalta oikealle täysin sulavasti
        g_chart.add_rows(pd.DataFrame({"G-Force": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({"Muscle Activation %": [float(strains["Back"])]}))

        # 3. METRIIKAT
        g_metric.metric("LIVE G-LOAD", f"{current_g:.1f} G")
        
        if strains['Back'] > 85:
            status_msg.error("CRITICAL STRAIN")
        elif current_g > 7:
            status_msg.warning("HIGH G-LOAD")
        else:
            status_msg.success("STABLE")

        # 0.05s - 0.1s on optimaalinen "smooth" efekti
        time.sleep(0.08)
