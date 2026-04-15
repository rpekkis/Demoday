import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ - Mission Diagnostics", layout="wide")

# --- REALISTINEN LENTOPROFIILI ---
def generate_flight_profile():
    t = np.arange(0, 200)
    g = np.ones(200)
    g[30:70] = 1.0 + 4.0 * np.sin(np.linspace(0, np.pi, 40)) # 5G kaarto
    g[100:150] = 3.0 + 5.5 * np.sin(np.linspace(0, np.pi, 50))**2 # 8.5G piikki
    return np.clip(g, 1.0, 9.0)

flight_data = generate_flight_profile()

# --- APUFUNKTIO VÄRIPALKEILLE ---
def render_custom_bar(label, value):
    # Väri muuttuu: 0-50 (Vihreä-Kelta), 50-100 (Kelta-Punainen)
    r = int(np.clip((value / 50) * 255, 0, 255))
    g_val = int(np.clip(255 - ((value - 50) / 50) * 255 if value > 50 else 255, 0, 255))
    color = f"rgb({r}, {g_val}, 0)"
    
    st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                <span style="font-size: 14px; font-weight: bold;">{label}</span>
                <span style="font-size: 14px;">{value}%</span>
            </div>
            <div style="background-color: #333; border-radius: 5px; width: 100%; height: 12px;">
                <div style="background-color: {color}; width: {value}%; height: 12px; border-radius: 5px; transition: width 0.3s;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.title("🛡️ NeuroFlight™ Mission Diagnostics")
st.write("Comparing Physiological Tactical Readiness: Optimal vs. Suboptimal AGSM")

# --- VALINTA ---
col_btn1, col_btn2 = st.columns(2)
start_optimal = col_btn1.button("🚀 Start Optimal Mission Analysis", use_container_width=True)
start_suboptimal = col_btn2.button("⚠️ Start Suboptimal Mission Analysis", use_container_width=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Bio-Mechanical Load")
    muscle_placeholders = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}
    st.markdown("---")
    g_metric = st.empty()
    status_msg = st.empty()

with col2:
    st.subheader("Tactical Telemetry")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force"]), height=220)
    emg_chart = st.line_chart(pd.DataFrame(columns=["Core/Lower Body %", "Neck Strain %"]), height=220)

# --- SIMULAATIO ---
if start_optimal or start_suboptimal:
    mode = "OPTIMAL" if start_optimal else "SUBOPTIMAL"
    
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        # Katsotaan tulevaa G-voimaa (ennakointi)
        future_g = flight_data[min(i + 8, len(flight_data)-1)]
        
        if mode == "OPTIMAL":
            # Ennakoiva aktivaatio (AGSM alkaa ennen G:tä)
            prep = max(current_g, future_g)
            # Fokus jaloissa ja coressa, niska pidetään stabiilina mutta ei ylijännitetä
            strains = {
                "Neck": int(np.clip((current_g**1.5) * 1.5, 5, 60)),
                "Back": int(np.clip((prep**1.7) * 1.4, 10, 85)),
                "Core": int(np.clip((prep**1.9) * 1.2, 10, 95)),
                "Glutes": int(np.clip((prep**2.0) * 1.1, 15, 100)),
                "Quads": int(np.clip((prep**2.0) * 1.1, 15, 100))
            }
            msg = "PRE-EMPTIVE AGSM ACTIVE" if future_g > current_g else "OPTIMAL FLOW"
            status_msg.success(msg)
        else:
            # Viivästynyt aktivaatio (Reaktiivinen, alkaa vasta kun G tuntuu)
            # Fokus siirtyy niskaan (huono asento), jalat "unohdetaan"
            strains = {
                "Neck": int(np.clip((current_g**2.1) * 1.8, 0, 100)), # Niska joutuu koville
                "Back": int(np.clip((current_g**1.8) * 1.5, 0, 90)),
                "Core": int(np.clip((current_g**1.5) * 1.1, 0, 60)), # Core "vuotaa"
                "Glutes": int(np.clip((current_g**1.4) * 1.0, 0, 50)),
                "Quads": int(np.clip((current_g**1.4) * 1.0, 0, 50))
            }
            msg = "REACTIVE ENGAGEMENT - RISK" if current_g > 3 else "SUBOPTIMAL PREP"
            status_msg.error(msg)

        # 1. Päivitetään väripalkit
        for m, val in strains.items():
            with muscle_placeholders[m]:
                render_custom_bar(m, val)

        # 2. Päivitetään kaaviot (EMG ei seuraa G:tä täydellisesti)
        g_chart.add_rows(pd.DataFrame({"G-Force": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({
            "Core/Lower Body %": [float((strains["Core"] + strains["Quads"])/2)],
            "Neck Strain %": [float(strains["Neck"])]
        }))

        # 3. Metriikka
        g_metric.metric("AIRCRAFT LOAD", f"{current_g:.1f} G", delta=mode)
        
        time.sleep(0.18)
