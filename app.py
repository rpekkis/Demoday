import streamlit as st
import numpy as np
import time
import pandas as pd

st.set_page_config(page_title="NeuroFlight™ Mission Analytics", layout="wide")

# --- DATASETIN SIMULAATIO ---
def generate_mission_data():
    seconds = np.arange(0, 301)
    # Luodaan realistinen G-profiili
    g_profile = 1.0 + 0.5 * np.sin(seconds / 15)
    g_profile[40:70] += 5.5   # Dogfight 1
    g_profile[150:190] += 7.0  # High-G Turn
    g_profile[240:270] += 3.0  # Intercept
    return seconds, np.clip(g_profile, 1.0, 9.0)

time_steps, g_values = generate_mission_data()

st.title("🛡️ NeuroFlight™: Mission Replay")
st.write("Real-time bio-telemetry showing muscle engagement vs. aircraft G-load.")

# --- UI ELEMENTIT ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Biological Load")
    # Käytetään progress baria heatmapin sijaan, koska se on kevyempi ja sulavampi demossa
    st.write("Neck Strain")
    neck_bar = st.progress(0)
    st.write("Lower Back (L1-L5)")
    back_bar = st.progress(0)
    st.write("Core/Abs")
    core_bar = st.progress(0)
    
    st.markdown("---")
    g_display = st.empty() # Tähän tulee iso G-luku

with col2:
    st.subheader("Live Telemetry Stream")
    # Luodaan tyhjä viivakaavio valmiiksi
    chart_data = pd.DataFrame(columns=["G-Load", "Muscle Stress %"])
    line_chart = st.line_chart(chart_data)

# --- ANIMATION LOOP ---
if st.button('▶️ Start Mission Analysis'):
    for t in range(len(time_steps)):
        current_g = g_values[t]
        
        # Simuloidaan lihasrasitusta (%)
        back_strain = min(100, int((current_g * 10) + np.random.randint(-2, 2)))
        neck_strain = min(100, int((current_g * 11) + np.random.randint(-3, 3)))
        core_strain = min(100, int((current_g * 7) + np.random.randint(-1, 5)))

        # 1. Päivitetään palkit (ei vilku)
        neck_bar.progress(neck_strain / 100)
        back_bar.progress(back_strain / 100)
        core_bar.progress(core_strain / 100)
        
        # 2. Päivitetään iso G-lukema
        g_display.metric("Current Load", f"{current_g:.1f} G", 
                         delta=f"{back_strain}% Strain", delta_color="inverse")

        # 3. Lisätään uusi datapiste viivakaavioon (SULAVA PÄIVITYS)
        new_data = pd.DataFrame({
            "G-Load": [current_g],
            "Muscle Stress %": [back_strain / 10] # Skaalataan käyrälle sopivaksi
        })
        line_chart.add_rows(new_data)

        # Säädetään nopeutta (0.1s on erittäin smooth, kokeile mikä tuntuu hyvältä)
        time.sleep(0.1)
else:
    st.info("Ready for deployment. Click 'Start' to begin telemetry stream.")
