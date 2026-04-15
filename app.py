import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go
import base64
from PIL import Image
import os

st.set_page_config(page_title="NeuroFlight™ - Tactical Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- AGGRESSIIVINEN G-PROFIILI ---
def generate_aggressive_profile():
    t = np.arange(0, 300)
    g = np.ones(300)
    # Veto 1 + Äkkipudotus
    g[40:45] = np.linspace(1.0, 7.5, 5) 
    g[45:55] = 7.5 + np.random.normal(0, 0.1, 10)
    g[55:58] = np.linspace(7.5, 1.0, 3) # Pystysuora drop
    # Veto 2 + Äkkipudotus
    g[100:104] = np.linspace(1.0, 9.0, 4)
    g[104:115] = 9.0 + np.random.normal(0, 0.1, 11)
    g[115:118] = np.linspace(9.0, 1.0, 3) # Pystysuora drop
    return np.clip(g + np.random.normal(0, 0.03, 300), 1.0, 9.5)

flight_data = generate_aggressive_profile()

def get_color(val):
    r = int(np.clip((val / 50) * 255, 0, 255))
    g = int(np.clip(255 - ((val - 50) / 50) * 255 if val > 50 else 255, 0, 255))
    return f"rgb({r}, {g}, 0)"

# --- KUVA-APURI ---
def get_base64_img(path):
    with open(path, "rb") as f:
        return prefix + base64.b64encode(f.read()).decode()
prefix = "data:image/png;base64,"

st.title("🛡️ NeuroFlight™ Sensor Diagnostics")

c1, c2 = st.columns(2)
start_opt = c1.button("🚀 Start Optimal Mission", use_container_width=True)
start_sub = c2.button("⚠️ Start Suboptimal Mission", use_container_width=True)

col_heat, col_charts = st.columns([1.2, 2])

with col_heat:
    st.subheader("Anatomical Heatmap")
    heatmap_placeholder = st.empty()
    placeholders = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}

with col_charts:
    st.subheader("Flight Telemetry (Unit: G & % MVC)")
    g_chart = st.line_chart(pd.DataFrame(columns=["G-Force (G)"]), height=220)
    emg_chart = st.line_chart(pd.DataFrame(columns=["Lower Body Activation (%)", "Neck Strain (%)"]), height=220)
    g_metric = st.empty()

# --- ANIMATION LOOP ---
if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    img_path = "body.png" # VARMISTA ETTÄ TÄMÄ ON KANSIOSSA
    
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        future_g = flight_data[min(i + 6, len(flight_data)-1)]
        noise = lambda: np.random.normal(0, 1.5)
        
        if mode == "OPTIMAL":
            prep = max(current_g, future_g)
            strains = {
                "Neck": int(np.clip((current_g**1.4)*1.5 + noise(), 5, 55)),
                "Back": int(np.clip((prep**1.7)*1.4 + noise(), 10, 85)),
                "Core": int(np.clip((prep**2.0)*1.3 + noise(), 10, 95)),
                "Glutes": int(np.clip((prep**2.1)*1.2 + noise(), 15, 100)),
                "Quads": int(np.clip((prep**2.1)*1.2 + noise(), 15, 100))
            }
        else:
            strains = {
                "Neck": int(np.clip((current_g**2.2)*1.8 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.7)*1.5 + noise(), 0, 85)),
                "Core": int(np.clip((current_g**1.4)*1.1 + noise(), 0, 60)),
                "Glutes": int(np.clip((current_g**1.3)*1.0 + noise(), 0, 50)),
                "Quads": int(np.clip((current_g**1.3)*1.0 + noise(), 0, 50))
            }

        # --- HEATMAP PLOTLY ---
        fig = go.Figure()
        
        # Sijoitetaan lihakset (0-100 koordinaatistossa)
        # Säädä näitä jos pallo on väärässä kohdassa kuvaa
        muscle_coords = {
            "Neck": [50, 85], "Back": [50, 70], "Core": [50, 55],
            "Glutes": [50, 40], "Quads": [50, 20]
        }
        
        for m, pos in muscle_coords.items():
            val = strains[m]
            fig.add_trace(go.Scatter(
                x=[pos[0]], y=[pos[1]],
                mode="markers",
                marker=dict(size=25 + (val/3), color=get_color(val), line=dict(width=2, color="white")),
                hoverinfo="text", text=f"{m}: {val}%", showlegend=False
            ))

        # Ladataan taustakuva jos olemassa
        if os.path.exists(img_path):
            encoded_image = get_base64_img(img_path)
            fig.add_layout_image(
                dict(
                    source=encoded_image, x=50, y=50, sizex=100, sizey=100,
                    xanchor="center", yanchor="middle", sizing="contain", layer="below"
                )
            )

        fig.update_layout(
            template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        
        heatmap_placeholder.plotly_chart(fig, use_container_width=True, key=f"h_{i}", config={'displayModeBar': False})

        # --- PÄIVITETÄÄN MUUT ---
        g_chart.add_rows(pd.DataFrame({"G-Force (G)": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({
            "Lower Body Activation (%)": [float((strains["Core"] + strains["Quads"])/2)],
            "Neck Strain (%)": [float(strains["Neck"])]
        }))
        g_metric.metric("G-LOAD", f"{current_g:.1f} G", delta=f"{mode}")
        time.sleep(0.15)
