import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import os

st.set_page_config(page_title="NeuroFlight™ Tactical Command", layout="wide")

# --- REALISTINEN AGGRESSIIVINEN G-PROFIILI ---
def generate_dogfight_profile():
    t = np.arange(0, 200)
    g = np.ones(200)
    
    # Veto 1: Nopea nousu 7G ja ROMAHTAVA pudotus
    g[30:35] = np.linspace(1.0, 7.0, 5) 
    g[35:50] = 7.0 + np.random.normal(0, 0.1, 15)
    g[50:53] = np.linspace(7.0, 1.0, 3) # Äkkipudotus
    
    # Veto 2: Rajumpi veto 9G ja raju pudotus 3G:hen
    g[90:94] = np.linspace(1.0, 9.0, 4)
    g[94:110] = 9.0 + np.random.normal(0, 0.1, 16)
    g[110:113] = np.linspace(9.0, 3.0, 3) # Äkkikevennys
    g[113:140] = 3.0 + np.random.normal(0, 0.05, 27)
    g[140:143] = np.linspace(3.0, 1.0, 3) # Äkkilopetus
    
    return np.clip(g + np.random.normal(0, 0.05, 200), 0.8, 9.5)

flight_data = generate_dogfight_profile()

def get_h_color(val):
    r = int(np.clip((val / 50) * 255, 0, 255))
    g = int(np.clip(255 - ((val - 50) / 50) * 255 if val > 50 else 255, 0, 255))
    return f'rgb({r}, {g}, 0)'

st.title("🛡️ NeuroFlight™ Tactical Analytics")
st.write("Aggressive G-Dynamics & Anticipatory Bio-Response")

c1, c2 = st.columns(2)
start_opt = c1.button("🚀 Start Optimal Mission (Expert)", use_container_width=True)
start_sub = c2.button("⚠️ Start Suboptimal Mission (Trainee)", use_container_width=True)

col1, col2 = st.columns([1.2, 2])

with col1:
    st.subheader("Anatomical Heatmap")
    body_placeholder = st.empty()
    st.markdown("---")
    # Palkit dynaamisilla väreillä HTML-muodossa
    bar_placeholders = {m: st.empty() for m in ["Neck", "Back", "Core", "Glutes", "Quads"]}

with col2:
    st.subheader("Tactical Data (G vs. % MVC)")
    chart_placeholder = st.empty()
    g_metric = st.empty()

if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    time_hist, g_hist, core_hist, neck_hist = [], [], [], []
    
    img_path = "body_outline.png"
    has_image = os.path.exists(img_path)
    img = Image.open(img_path) if has_image else None

    for i in range(len(flight_data)):
        current_g = flight_data[i]
        future_g = flight_data[min(i + 8, len(flight_data)-1)]
        noise = lambda: np.random.normal(0, 2.0)
        
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
                "Neck": int(np.clip((current_g**2.2) * 1.8 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.8) * 1.5 + noise(), 0, 90)),
                "Core": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 60)),
                "Glutes": int(np.clip((current_g**1.4) * 1.0 + noise(), 0, 50)),
                "Quads": int(np.clip((current_g**1.4) * 1.0 + noise(), 0, 50))
            }

        # 1. HEATMAP (Lisätty key=f"body_{i}" virheen estämiseksi)
        fig_body = go.Figure()
        if has_image:
            fig_body.add_trace(go.Image(z=np.array(img)))
        
        locs = {"Neck": [450, 150], "Back": [780, 450], "Core": [450, 400], "Glutes": [780, 580], "Quads": [450, 750]}
        for m, loc in locs.items():
            fig_body.add_trace(go.Scatter(x=[loc[0]], y=[loc[1]], mode='markers',
                marker=dict(size=45, color=get_h_color(strains[m]), line=dict(width=2, color='white')), showlegend=False))
        
        fig_body.update_layout(template="plotly_dark", height=550, margin=dict(l=0,r=0,t=0,b=0),
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, autorange='reversed'))
        body_placeholder.plotly_chart(fig_body, use_container_width=True, key=f"body_{i}")

        # 2. KAAVIO (Lisätty key=f"chart_{i}")
        time_hist.append(i); g_hist.append(current_g)
        core_hist.append((strains["Core"] + strains["Quads"])/2)
        neck_hist.append(strains["Neck"])

        fig_data = go.Figure()
        fig_data.add_trace(go.Scatter(x=time_hist, y=g_hist, name="G-Force (G)", line=dict(color='cyan', width=2)))
        fig_data.add_trace(go.Scatter(x=time_hist, y=core_hist, name="Core %", line=dict(color='orange', dash='dot')))
        fig_data.add_trace(go.Scatter(x=time_hist, y=neck_hist, name="Neck %", line=dict(color='red', dash='dot')))
        
        fig_data.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig_data.update_yaxes(range=[0, 10], title="Value")
        chart_placeholder.plotly_chart(fig_data, use_container_width=True, key=f"chart_{i}")

        # 3. METRIIKAT
        g_metric.metric("AIRCRAFT LOAD", f"{current_g:.1f} G", delta=f"{mode}")
        
        time.sleep(0.12)
