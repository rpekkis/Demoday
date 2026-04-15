import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ - Tactical Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- REALISTINEN LENTOPROFIILI (Dynaaminen Dogfight) ---
def generate_aggressive_profile():
    t = np.arange(0, 300) # 5 min
    g = np.ones(300)
    
    # 1. Startti (Puhdas nousu 3G:hen)
    g[10:30] = np.linspace(1.0, 3.0, 20)
    
    # 2. Dogfight 1: NOPEA VETO 7G:HEN (Veto kestää 2s)
    start_pull = 40
    g[start_pull:start_pull+5] = np.linspace(g[start_pull-1], 7.0, 5) # 0.5s veto
    g[start_pull+5:start_pull+15] = 7.0 + np.random.normal(0, 0.1, 10) # 1s pito G:ssä
    
    # 3. Unload: Nopea pudotus 3.5G:hen (kerätään energiaa)
    g[start_pull+15:start_pull+20] = np.linspace(7.0, 3.5, 5) # 0.5s pudotus
    g[start_pull+20:start_pull+40] = 3.5 + np.random.normal(0, 0.05, 20) # 2s pito energiassa
    
    # 4. Dogfight 2: RAJU VETO MAX G:HEN (9G)
    start_pull2 = 100
    g[start_pull2:start_pull2+3] = np.linspace(g[start_pull2-1], 9.0, 3) # 0.3s veto
    g[start_pull2+3:start_pull2+15] = 9.0 + np.random.normal(0, 0.1, 12) # 1.2s pito max G:ssä
    
    # 5. Kevennys takaisin 5G:hen (Pehmeämpi lasku)
    g[start_pull2+15:start_pull2+25] = np.linspace(9.0, 5.0, 10) 
    g[start_pull2+25:start_pull2+60] = 5.0 + np.random.normal(0, 0.08, 35) # 3.5s pito 5G:ssä
    
    # 6. Rauhoittuminen (Loppuliuku)
    g[start_pull2+60:290] = np.linspace(5.0, 1.2, 290 - (start_pull2+60))
    
    # Lisätään instrumentaalista kohinaa koko käyrään
    return np.clip(g + np.random.normal(0, 0.03, 300), 1.0, 9.5)

flight_data = generate_aggressive_profile()

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
                <div style="background-color: {color}; width: {value}%; height: 10px; border-radius: 4px; transition: width 0.15s;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.title("🛡️ NeuroFlight™ Sensor Diagnostics")
st.write("Real-time Tactical Telemetry with High-Dynamic G-Dynamics")

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

# --- ANIMATION LOOP ---
if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    
    # Alustetaan historiadata
    time_hist, g_hist, core_hist, neck_hist = [], [], [], []
    
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        
        # Katsotaan tulevaa G-voimaa (ennakointi, lyhyempi ikkuna dogfightissa)
        future_g = flight_data[min(i + 5, len(flight_data)-1)]
        
        # Biologinen kohina
        noise = lambda: np.random.normal(0, 1.6)
        
        if mode == "OPTIMAL":
            # Optimaalisessa tilassa core/quads nousee agressiivisesti G:n mukana
            prep = max(current_g, future_g)
            strains = {
                "Neck": int(np.clip((current_g**1.6) * 1.6 + noise(), 5, 62)),
                "Back": int(np.clip((prep**1.8) * 1.5 + noise(), 10, 85)),
                "Core": int(np.clip((prep**2.1) * 1.3 + noise(), 10, 96)),
                "Glutes": int(np.clip((prep**2.1) * 1.1 + noise(), 15, 100)),
                "Quads": int(np.clip((prep**2.1) * 1.1 + noise(), 15, 100))
            }
            status_msg.success("ANTICIPATORY AGSM ACTIVE")
        else:
            # Suboptimaalisessa niska joutuu repivässä liikkeessä koville
            strains = {
                "Neck": int(np.clip((current_g**2.3) * 1.9 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.9) * 1.6 + noise(), 0, 90)),
                "Core": int(np.clip((current_g**1.6) * 1.2 + noise(), 0, 62)),
                "Glutes": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 52)),
                "Quads": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 52))
            }
            status_msg.error("REACTIVE - HIGH RISK")

        # Tallennetaan historiadata
        core_val = (strains["Core"] + strains["Quads"])/2
        neck_val = strains["Neck"]

        # 1. Palkit
        for m, val in strains.items():
            with placeholders[m]:
                render_custom_bar(m, val)

        # 2. Kaaviot (add_rows)
        g_chart.add_rows(pd.DataFrame({"G-Force (G)": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({
            "Core/Lower Body (%)": [float(core_val)],
            "Neck Strain (%)": [float(neck_val)]
        }))

        # 3. Metriikka
        g_metric.metric("G-LOAD (G)", f"{current_g:.1f}", delta=mode)
        
        # Pidetään nopeus rauhallisena (0.15s - 0.2s), jotta veto erottuu
        time.sleep(0.18)
