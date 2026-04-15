import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ - Tactical Analytics", layout="wide")

# --- REALISTINEN LENTOPROFIILI (Pehmeät kaarrot) ---
def generate_flight_profile():
    t = np.arange(0, 200)
    g = np.ones(200)
    g[30:70] = 1.0 + 4.0 * np.sin(np.linspace(0, np.pi, 40)) 
    g[100:150] = 3.0 + 5.5 * np.sin(np.linspace(0, np.pi, 50))**2 
    return np.clip(g, 1.0, 9.0)

flight_data = generate_flight_profile()

# --- APUFUNKTIO VÄRIPALKEILLE ---
def render_custom_bar(label, value):
    r = int(np.clip((value / 50) * 255, 0, 255))
    g_val = int(np.clip(255 - ((value - 50) / 50) * 255 if value > 50 else 255, 0, 255))
    color = f"rgb({r}, {g_val}, 0)"
    
    st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                <span style="font-size: 13px; font-weight: bold; color: #ddd;">{label.upper()}</span>
                <span style="font-size: 13px; color: #eee;">{value}%</span>
            </div>
            <div style="background-color: #333; border-radius: 4px; width: 100%; height: 10px;">
                <div style="background-color: {color}; width: {value}%; height: 10px; border-radius: 4px; transition: width 0.2s;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.title("🛡️ NeuroFlight™ Sensor Diagnostics")
st.write("Real-time EMG Noise Filtering & G-Load Telemetry")

# --- VALINTA ---
c1, c2 = st.columns(2)
start_opt = c1.button("🚀 Start Optimal Mission (Expert)", use_container_width=True)
start_sub = c2.button("⚠️ Start Suboptimal Mission (Trainee)", use_container_width=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Live Muscle Load")
    placeholders = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}
    st.markdown("---")
    g_metric = st.empty()
    status_msg = st.empty()

with col2:
    # Lisätty yksiköt otsikoihin (G ja % MVC)
    st.subheader("Aircraft Dynamics (Unit: G)")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force (G)"]), height=220)
    
    st.subheader("Neuro-Muscular Response (Unit: % MVC)")
    emg_chart = st.line_chart(pd.DataFrame(columns=["Core/Lower Body (%)", "Neck Strain (%)"]), height=220)

# --- SIMULAATIO ---
if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        future_g = flight_data[min(i + 8, len(flight_data)-1)]
        
        # Lisätään sensorikohinaa (Noise)
        noise = lambda: np.random.normal(0, 1.8) # Gaussian noise
        
        if mode == "OPTIMAL":
            prep = max(current_g, future_g)
            strains = {
                "Neck": int(np.clip((current_g**1.5) * 1.5 + noise(), 5, 65)),
                "Back": int(np.clip((prep**1.7) * 1.4 + noise(), 10, 88)),
                "Core": int(np.clip((prep**1.9) * 1.2 + noise(), 10, 96)),
                "Glutes": int(np.clip((prep**2.0) * 1.1 + noise(), 15, 100)),
                "Quads": int(np.clip((prep**2.0) * 1.1 + noise(), 15, 100))
            }
            status_msg.success("ANTICIPATORY AGSM ACTIVE")
        else:
            strains = {
                "Neck": int(np.clip((current_g**2.1) * 1.8 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.8) * 1.5 + noise(), 0, 92)),
                "Core": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 65)),
                "Glutes": int(np.clip((current_g**1.4) * 1.0 + noise(), 0, 55)),
                "Quads": int(np.clip((current_g**1.4) * 1.0 + noise(), 0, 55))
            }
            status_msg.error("REACTIVE - HIGH RISK")

        # 1. Palkit
        for m, val in strains.items():
            with placeholders[m]:
                render_custom_bar(m, val)

        # 2. Kaaviot (Kohinalla varustettuna)
        # G-voimassa on vain vähän kohinaa (instrumental), EMG:ssä paljon (biological)
        g_chart.add_rows(pd.DataFrame({"G-Force (G)": [current_g + np.random.normal(0, 0.05)]}))
        
        emg_chart.add_rows(pd.DataFrame({
            "Core/Lower Body (%)": [float((strains["Core"] + strains["Quads"])/2)],
            "Neck Strain (%)": [float(strains["Neck"])]
        }))

        # 3. Metriikka
        g_metric.metric("G-LOAD (G)", f"{current_g:.1f}", delta=mode)
        
        time.sleep(0.15)
