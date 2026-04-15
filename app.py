import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ Tactical Command", layout="wide")

# --- DATASETIN SIMULAATIO ---
def get_mission_g(t):
    # Vaihteleva profiili: rullaus -> dogfight -> tasainen -> kova kaarto
    if t < 20: return 1.0 
    elif t < 60: return 3.0 + 2.0 * np.sin(t/5)
    elif t < 100: return 1.5 
    elif t < 160: return 6.5 + 2.5 * np.sin(t/8)
    else: return 4.0 + np.cos(t/10)

# --- APUFUNKTIO VÄREILLE (Heatmap) ---
def get_color(val):
    # Palauttaa värin vihreästä punaiseen (val 0-100)
    r = int(np.clip((val / 50) * 255, 0, 255))
    g = int(np.clip(255 - ((val - 50) / 50) * 255 if val > 50 else 255, 0, 255))
    return f"rgb({r}, {g}, 0)"

st.title("🛡️ NeuroFlight™ Tactical Command")
st.write("Live Bio-Telemetry: Pilot Physiological Integrity")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Biological Heatmap")
    # Luodaan visuaalinen heatmap-lista (tämä korvaa kuvan, jos se pätkii)
    heat_placeholders = {
        "Neck": st.empty(),
        "Back": st.empty(),
        "Core": st.empty(),
        "Glutes": st.empty(),
        "Quads": st.empty()
    }
    st.markdown("---")
    g_metric = st.empty()

with col2:
    st.subheader("Dual-Axis Mission Data")
    # Streamlitin natiivi chart on kaikkein sulavin striimaukseen
    chart_placeholder = st.empty()
    # Alustetaan dataframe
    df_history = pd.DataFrame(columns=["G-Force", "Muscle Load %"])

# --- ANIMATION LOOP ---
if st.button('▶️ START REAL-TIME TELEMETRY'):
    history_data = []
    
    for t in range(200):
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

        # 1. PÄIVITETÄÄN HEATMAP (Visuaaliset palikat)
        for muscle, val in strains.items():
            color = get_color(val)
            heat_placeholders[muscle].markdown(
                f"""<div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="width: 20px; height: 20px; background-color: {color}; border-radius: 50%; margin-right: 10px; border: 1px solid white;"></div>
                    <div style="flex-grow: 1;"><b>{muscle}: {val}%</b></div>
                </div>""", unsafe_allow_html=True
            )

        # 2. PÄIVITETÄÄN KAAVIO (SULAVA)
        # Käytetään kahta eri saraketta, jotta ne näkyvät eri väreillä
        new_row = {"G-Force": current_g, "Muscle Load %": strains["Back"] / 10.0}
        history_data.append(new_row)
        
        # Piirretään koko historia kerralla uudestaan tyhjään tilaan, mutta natiivilla chartilla
        chart_placeholder.line_chart(pd.DataFrame(history_data), height=400)

        # 3. METRIIKKA
        g_metric.metric("Current Load", f"{current_g:.1f} G", delta=f"{strains['Back']}% Strain")

        time.sleep(0.1) # 10Hz päivitys on silmälle miellyttävä
