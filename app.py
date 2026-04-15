import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="NeuroFlight™ - Tactical Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- REALISTINEN LENTOPROFIILI ---
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
def get_color(val):
    r = int(np.clip((val / 50) * 255, 0, 255))
    g = int(np.clip(255 - ((val - 50) / 50) * 255 if val > 50 else 255, 0, 255))
    return f"rgb({r}, {g}, 0)"

def render_custom_bar(label, value):
    color = get_color(value)
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

# --- UI LAYOUT ---
c1, c2 = st.columns(2)
start_opt = c1.button("🚀 Start Optimal Mission (Expert)", use_container_width=True)
start_sub = c2.button("⚠️ Start Suboptimal Mission (Trainee)", use_container_width=True)

col_heat, col_charts = st.columns([1.1, 2])

with col_heat:
    st.subheader("Anatomical Heatmap")
    heatmap_placeholder = st.empty()
    st.markdown("---")
    placeholders = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}

with col_charts:
    st.subheader("Tactical Data (G-Load & EMG)")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force (G)"]), height=250)
    emg_chart = st.line_chart(pd.DataFrame(columns=["Core/Lower Body (%)", "Neck Strain (%)"]), height=250)
    g_metric = st.empty()
    status_msg = st.empty()

# --- ANIMATION LOOP ---
if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        future_g = flight_data[min(i + 5, len(flight_data)-1)]
        noise = lambda: np.random.normal(0, 1.8)
        
        if mode == "OPTIMAL":
            prep = max(current_g, future_g)
            strains = {
                "Neck": int(np.clip((current_g**1.5) * 1.5 + noise(), 5, 60)),
                "Back": int(np.clip((prep**1.7) * 1.4 + noise(), 10, 85)),
                "Core": int(np.clip((prep**2.1) * 1.3 + noise(), 10, 96)),
                "Glutes": int(np.clip((prep**2.1) * 1.1 + noise(), 15, 100)),
                "Quads": int(np.clip((prep**2.1) * 1.1 + noise(), 15, 100))
            }
            status_msg.success("ANTICIPATORY AGSM ACTIVE")
        else:
            strains = {
                "Neck": int(np.clip((current_g**2.3) * 1.9 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.9) * 1.6 + noise(), 0, 92)),
                "Core": int(np.clip((current_g**1.6) * 1.2 + noise(), 0, 65)),
                "Glutes": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 55)),
                "Quads": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 55))
            }
            status_msg.error("REACTIVE - HIGH RISK")

        # 1. PÄIVITETÄÄN HEATMAP (Plotly Scatter over Image)
        # Sijoitetaan sensoripisteet anatomisille paikoille
        # (x ja y on normalisoitu 0-100 välille)
        muscle_coords = {
            "Neck": [50, 88], "Back": [50, 65], "Core": [50, 55],
            "Glutes": [50, 42], "Quads": [50, 25]
        }
        
        fig = go.Figure()
        # Lisätään sensoripisteet
        for m, pos in muscle_coords.items():
            val = strains[m]
            fig.add_trace(go.Scatter(
                x=[pos[0]], y=[pos[1]],
                mode="markers+text",
                text=[f"{val}%"], textposition="top center",
                marker=dict(size=20 + (val/4), color=get_color(val), 
                            line=dict(width=2, color="white"), opacity=0.8),
                showlegend=False
            ))
        
        fig.update_layout(
            template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        # Lisätään taustalle "haamukuva" (placeholder tekstinä, jos tiedostoa ei ole)
        fig.add_annotation(x=50, y=50, text="HUMAN DYNAMICS", font=dict(size=40, color="rgba(255,255,255,0.1)"), showarrow=False)
        
        heatmap_placeholder.plotly_chart(fig, use_container_width=True, key=f"heat_{i}")

        # 2. PÄIVITETÄÄN PALKIT
        for m, val in strains.items():
            with placeholders[m]:
                render_custom_bar(m, val)

        # 3. PÄIVITETÄÄN KAAVIOT
        g_chart.add_rows(pd.DataFrame({"G-Force (G)": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({
            "Core/Lower Body (%)": [float((strains["Core"] + strains["Quads"])/2)],
            "Neck Strain (%)": [float(strains["Neck"])]
        }))

        g_metric.metric("G-LOAD (G)", f"{current_g:.1f}", delta=mode)
        time.sleep(0.16)
