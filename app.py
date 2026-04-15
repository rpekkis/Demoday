import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ - G-Ready Telemetry", layout="wide")

# --- REALISTINEN LENTOPROFIILI (Pehmeät siirtymät) ---
def generate_flight_profile():
    t = np.arange(0, 300)
    g = np.ones(300)
    
    # 1. Alkuverkka (Pehmeä nousu 3G:hen)
    g[20:50] = 1.0 + 2.0 * np.sin(np.linspace(0, np.pi, 30))
    
    # 2. Pitkäkestoinen 5G rasitus (Sustained Load)
    g[70:110] = 5.0 + 0.3 * np.cos(np.linspace(0, 4*np.pi, 40)) 
    
    # 3. Dogfight-liikkeet (Ei pystysuoria droppeja)
    g[130:180] = 4.0 + 4.5 * np.sin(np.linspace(0, 2*np.pi, 50))**2
    
    # 4. Loppuliuku
    g[220:260] = np.linspace(g[219], 1.2, 40)
    
    return np.clip(g, 1.0, 9.0)

flight_data = generate_flight_profile()

st.title("🛡️ NeuroFlight™ Physiological Readiness")
st.write("Anticipatory Muscle Engagement & Fluid G-Dynamics")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Physical Activation")
    # Luodaan paikat tekstille ja palkille
    muscle_ui = {}
    for m in ["Neck", "Back", "Core", "Glutes", "Quads"]:
        muscle_ui[m] = {"text": st.empty(), "bar": st.empty()}
    
    st.markdown("---")
    g_metric = st.empty()
    status_msg = st.empty()

with col2:
    st.subheader("Tactical Flight Data")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force"]), height=250)
    emg_chart = st.line_chart(pd.DataFrame(columns=["Total Muscle Prep %"]), height=250)

# --- ANIMATION LOOP ---
if st.button('▶️ START MISSION ANALYSIS'):
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        
        # ENNAKOIVA LOGIIKKA: Katsotaan tulevaa G-voimaa (1 sekunti eteenpäin)
        future_g = flight_data[min(i + 10, len(flight_data)-1)]
        
        # Lihasaktivaatio reagoi enemmän tulevaan G-voimaan (valmistautuminen)
        prep_factor = max(current_g, future_g)
        base_strain = (prep_factor ** 1.8) * 1.5
        
        strains = {
            "Neck": int(np.clip(base_strain * 1.3, 0, 100)),
            "Back": int(np.clip(base_strain * 1.1, 0, 100)),
            "Core": int(np.clip(base_strain * 1.4, 0, 100)), # Core jännittyy kovaa
            "Glutes": int(np.clip(base_strain * 1.2, 0, 100)),
            "Quads": int(np.clip(base_strain * 1.2, 0, 100))
        }

        # 1. PÄIVITETÄÄN TÄYTTYVÄT PALKIT (Progress bars)
        for m, val in strains.items():
            muscle_ui[m]["text"].write(f"**{m}**: {val}%")
            # st.progress vaatii arvon 0.0 - 1.0
            muscle_ui[m]["bar"].progress(val / 100.0)

        # 2. PÄIVITETÄÄN KAAVIOT
        g_chart.add_rows(pd.DataFrame({"G-Force": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({"Total Muscle Prep %": [float(strains["Core"])]}))

        # 3. METRIIKAT
        g_metric.metric("LIVE LOAD", f"{current_g:.1f} G")
        
        # Statusteksti ennakoivasta tilasta
        if future_g > current_g + 0.5:
            status_msg.info("PREPARING FOR G-ONSET")
        elif current_g > 4.5:
            status_msg.error("SUSTAINED LOAD")
        else:
            status_msg.success("OPTIMAL")

        # Hidastettu tempo (0.15s - 0.2s antaa aikaa selittää)
        time.sleep(0.15)
