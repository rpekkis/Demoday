import streamlit as st
import numpy as np
import time
import pandas as pd
import base64
import os

st.set_page_config(page_title="NeuroFlight™ - Fluid Diagnostics", layout="wide", initial_sidebar_state="collapsed")

# --- REALISTINEN LENTOPROFIILI (Dynaaminen Dogfight) ---
def generate_aggressive_profile():
    t = np.arange(0, 300)
    g = np.ones(300)
    g[10:30] = np.linspace(1.0, 3.0, 20)
    start_pull = 40
    g[start_pull:start_pull+5] = np.linspace(g[start_pull-1], 7.0, 5) 
    g[start_pull+5:start_pull+15] = 7.0 + np.random.normal(0, 0.1, 10)
    g[start_pull+15:start_pull+20] = np.linspace(7.0, 1.0, 5) # RAJU PUDOTUS
    start_pull2 = 100
    g[start_pull2:start_pull2+3] = np.linspace(g[start_pull2-1], 9.0, 3) 
    g[start_pull2+3:start_pull2+15] = 9.0 + np.random.normal(0, 0.1, 12)
    g[start_pull2+15:start_pull2+18] = np.linspace(9.0, 1.0, 3) # RAJU PUDOTUS
    return np.clip(g + np.random.normal(0, 0.03, 300), 1.0, 9.5)

flight_data = generate_aggressive_profile()

# --- APUFUNKTIOT VISUALISOINTIIN ---
def get_h_color(val):
    r = int(np.clip((val / 50) * 255, 0, 255))
    g = int(np.clip(255 - ((val - 50) / 50) * 255 if val > 50 else 255, 0, 255))
    return f'rgb({r}, {g}, 0)'

# --- HTML HEATMAP SENSORIPALLOT (Vakaat koordinaatit) ---
def get_sensor_html(strains):
    # Absoluuttiset koordinaatit (top%, left%) suhteessa body.png:hen
    locs = {
        "Neck": [10, 50], "Back": [35, 50], "Core": [45, 50],
        "Glutes": [55, 50], "Quads": [75, 50]
    }
    
    sensors_html = ""
    for m, pos in locs.items():
        val = strains[m]
        color = get_h_color(val)
        sensors_html += f"""
        <div style="
            position: absolute;
            top: {pos[0]}%;
            left: {pos[1]}%;
            transform: translate(-50%, -50%);
            width: 20px; height: 20px;
            background-color: {color};
            border-radius: 50%;
            border: 2px solid white;
            box-shadow: 0 0 10px {color};
            transition: background-color 0.1s;
        "></div>
        """
    return sensors_html

st.title("🛡️ NeuroFlight™ Sensor Diagnostics")
st.write("Live Bio-Telemetry: Pilot Physiological Integrity")

c1, c2 = st.columns(2)
start_opt = c1.button("🚀 Start Optimal Mission (Expert)", use_container_width=True)
start_sub = c2.button("⚠️ Start Suboptimal Mission (Trainee)", use_container_width=True)

col_heat, col_charts = st.columns([1, 2])

with col_heat:
    st.subheader("Anatomical Heatmap")
    heatmap_placeholder = st.empty()
    st.markdown("---")
    bars = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}

with col_charts:
    st.subheader("Tactical Data (G-Load & EMG)")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force (G)"]), height=250)
    emg_chart = st.line_chart(pd.DataFrame(columns=["Core/Lower Body (%)", "Neck Strain (%)"]), height=250)
    g_metric = st.empty()

# --- ANIMATION LOOP ---
if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    
    # Ladataan kuva vain kerran ja koodataan Base64
    img_path = "body.png"
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode()
            img_prefix = "data:image/png;base64,"
    else:
        st.error(f"Error: {img_path} not found. Please save the diagram first.")
        st.stop()

    for i in range(len(flight_data)):
        current_g = flight_data[i]
        future_g = flight_data[min(i + 5, len(flight_data)-1)]
        noise = lambda: np.random.normal(0, 1.6)
        
        if mode == "OPTIMAL":
            prep = max(current_g, future_g)
            strains = {
                "Neck": int(np.clip((current_g**1.5) * 1.5 + noise(), 5, 60)),
                "Back": int(np.clip((prep**1.7) * 1.4 + noise(), 10, 85)),
                "Core": int(np.clip((prep**2.1) * 1.3 + noise(), 10, 96)),
                "Glutes": int(np.clip((prep**2.1) * 1.1 + noise(), 15, 100)),
                "Quads": int(np.clip((prep**2.1) * 1.1 + noise(), 15, 100))
            }
        else:
            strains = {
                "Neck": int(np.clip((current_g**2.3) * 1.9 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.9) * 1.6 + noise(), 0, 92)),
                "Core": int(np.clip((current_g**1.6) * 1.2 + noise(), 0, 65)),
                "Glutes": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 55)),
                "Quads": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 55))
            }

        # 1. SULAVA HTML HEATMAP (Ei välkkymistä)
        sensors_html = get_sensor_html(strains)
        
        heatmap_placeholder.markdown(
            f"""
            <div style="position: relative; width: 100%; max-width: 400px; margin: auto;">
                <img src="{img_prefix}{encoded_image}" style="width: 100%; display: block; opacity: 0.1;">
                {sensors_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. PÄIVITETÄÄN KAAVIOT
        g_chart.add_rows(pd.DataFrame({"G-Force (G)": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({
            "Core/Lower Body (%)": [float((strains["Core"] + strains["Quads"])/2)],
            "Neck Strain (%)": [float(strains["Neck"])]
        }))

        g_metric.metric("G-LOAD (G)", f"{current_g:.1f}", delta=mode)
        time.sleep(0.16)
