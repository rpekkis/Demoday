import streamlit as st
import numpy as np
import time
import pandas as pd
import base64
import os

st.set_page_config(page_title="NeuroFlight™ - Tactical Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- KONFIGURAATIO JA LENTOPROFIILI (SÄILYTETTY) ---
def generate_aggressive_profile():
    t = np.arange(0, 300)
    g = np.ones(300)
    g[40:45] = np.linspace(1.0, 7.0, 5) 
    g[45:55] = 7.0 + np.random.normal(0, 0.1, 10)
    g[55:58] = np.linspace(7.0, 1.0, 3) 
    g[100:104] = np.linspace(1.0, 9.0, 4)
    g[104:115] = 9.0 + np.random.normal(0, 0.1, 11)
    g[115:118] = np.linspace(9.0, 1.0, 3) 
    return np.clip(g + np.random.normal(0, 0.03, 300), 1.0, 9.5)

flight_data = generate_aggressive_profile()

# --- APUFUNKTIOT VISUALISOINTIIN (SÄILYTETTY) ---
def get_h_color(val):
    r = int(np.clip((val / 50) * 255, 0, 255))
    g = int(np.clip(255 - ((val - 50) / 50) * 255 if val > 50 else 255, 0, 255))
    return f'rgb({r}, {g}, 0)'

def render_bar(label, value):
    color = get_h_color(value)
    st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                <span style="font-size: 13px; font-weight: bold; color: #ddd;">{label.upper()}</span>
                <span style="font-size: 13px; color: #eee;">{value}% MVC</span>
            </div>
            <div style="background-color: #333; border-radius: 4px; width: 100%; height: 10px;">
                <div style="background-color: {color}; width: {value}%; height: 10px; border-radius: 4px;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- SENSORIPALLOJEN HTML (VAKAA, EI VILKU) ---
def get_sensor_html(strains):
    # Koordinaatit [% ylhäältä, % vasemmalta]
    locs = {
        "Neck": [12, 50], "Back": [38, 50], "Core": [50, 50],
        "Glutes": [62, 50], "Quads": [82, 50]
    }
    html = ""
    for m, pos in locs.items():
        val = strains[m]
        color = get_h_color(val)
        # Pallo muuttaa väriä, mutta div-elementti pysyy vakaana
        html += f"""<div style="position: absolute; top: {pos[0]}%; left: {pos[1]}%; 
                    transform: translate(-50%, -50%); width: 22px; height: 22px; 
                    background-color: {color}; border-radius: 50%; border: 2px solid white; 
                    box-shadow: 0 0 12px {color};"></div>"""
    return html

st.title("🛡️ NeuroFlight™ Sensor Diagnostics")
st.write("Aggressive G-Dynamics & Anticipatory Bio-Response")

c1, c2 = st.columns(2)
start_opt = c1.button("🚀 Start Optimal Mission (Expert)", use_container_width=True)
start_sub = c2.button("⚠️ Start Suboptimal Mission (Trainee)", use_container_width=True)

col_heat, col_charts = st.columns([1.2, 2])

with col_heat:
    st.subheader("Anatomical Heatmap")
    heatmap_placeholder = st.empty() 
    st.markdown("---")
    bars = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}

with col_charts:
    st.subheader("Flight Telemetry (Unit: G & % MVC)")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force (G)"]), height=220)
    
    st.subheader("Neuro-Muscular Response (Unit: % MVC)")
    emg_chart = st.line_chart(pd.DataFrame(columns=["Lower Body Activation (%)", "Neck Strain (%)"]), height=220)
    g_metric = st.empty()

# --- SIMULAATIO ---
if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    img_path = "body.png"
    
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode()
            img_src = f"data:image/png;base64,{b64_img}"
    else:
        st.error("body.png missing! Tallenna kuva koodin kanssa samaan kansioon.")
        st.stop()
    
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        future_g = flight_data[min(i + 8, len(flight_data)-1)]
        noise = lambda: np.random.normal(0, 1.8)
        
        if mode == "OPTIMAL":
            prep = max(current_g, future_g)
            strains = {
                "Neck": int(np.clip((current_g**1.5) * 1.5 + noise(), 5, 60)),
                "Back": int(np.clip((prep**1.7) * 1.4 + noise(), 10, 85)),
                "Core": int(np.clip((prep**1.9) * 1.2 + noise(), 10, 95)),
                "Glutes": int(np.clip((prep**2.0) * 1.1 + noise(), 15, 100)),
                "Quads": int(np.clip((prep**2.0) * 1.1 + noise(), 15, 100))
            }
        else:
            strains = {
                "Neck": int(np.clip((current_g**2.3) * 1.9 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.9) * 1.6 + noise(), 0, 90)),
                "Core": int(np.clip((current_g**1.6) * 1.2 + noise(), 0, 62)),
                "Glutes": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 52)),
                "Quads": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 52))
            }

        # --- TÄMÄ ON SE VAKAA RAKENNE ---
        # Käytetään flex-boxia ja suhteellista asemointia, jotta kuva ei ole "zoomattu"
        heatmap_placeholder.markdown(f"""
            <div style="display: flex; justify-content: center; background-color: #0e1117; padding: 10px; border-radius: 10px;">
                <div style="position: relative; width: 100%; max-width: 300px;">
                    <img src="{img_src}" style="width: 100%; display: block; opacity: 0.5;">
                    {get_sensor_html(strains)}
                </div>
            </div>
        """, unsafe_allow_html=True)

        for m, val in strains.items():
            with bars[m]:
                render_bar(m, val)

        g_chart.add_rows(pd.DataFrame({"G-Force (G)": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({
            "Lower Body Activation (%)": [float((strains["Core"] + strains["Quads"])/2)],
            "Neck Strain (%)": [float(strains["Neck"])]
        }))
        g_metric.metric("G-LOAD", f"{current_g:.1f} G", delta=f"{mode}")
        
        time.sleep(0.12)
