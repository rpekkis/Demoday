import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go
import base64
from PIL import Image
import os

st.set_page_config(page_title="NeuroFlight™ - Tactical Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- KONFIGURAATIO JA LENTOPROFIILI ---
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

# --- APUFUNKTIOT VISUALISOINTIIN ---
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
                <div style="background-color: {color}; width: {value}%; height: 10px; border-radius: 4px; transition: width 0.15s;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

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
    # Palkit lisätiedoksi
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

        # --- HEATMAP PLOTLY ---
        fig_body = go.Figure()
        
        # Sijoitetaan lihakset tarkasti (koordinaatit 0-100)
        locs = {
            "Neck": [50, 88], "Back": [50, 70], "Core": [50, 55],
            "Glutes": [50, 42], "Quads": [50, 25]
        }
        
        # PIIRRETÄÄN VARTALON SILUETTI (Tämä korvaa tekstin)
        fig_body.add_shape(type="path",
            path="M50,95 L55,92 L58,85 L58,75 L65,70 L65,50 L60,30 L55,10 L45,10 L40,30 L35,50 L35,70 L42,75 L42,85 L45,92 Z",
            fillcolor="rgba(255, 255, 255, 0.1)",
            line=dict(color="rgba(255, 255, 255, 0.3)", width=2),
            xref="x", yref="y"
        )

        for m, loc in locs.items():
            fig_body.add_trace(go.Scatter(
                x=[loc[0]], y=[loc[1]],
                mode='markers',
                marker=dict(size=40, color=get_h_color(strains[m]), line=dict(width=2, color='white')),
                showlegend=False, hoverinfo="none"
            ))

        fig_body.update_layout(
            template="plotly_dark", height=550, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False, autorange='reversed'),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        heatmap_placeholder.plotly_chart(fig_body, use_container_width=True, key=f"body_{i}")

        # --- PÄIVITETÄÄN PALKIT ---
        for m, val in strains.items():
            with bars[m]:
                render_bar(m, val)

        # --- PÄIVITETÄÄN KAAVIOT ---
        g_chart.add_rows(pd.DataFrame({"G-Force (G)": [current_g]}))
        emg_chart.add_rows(pd.DataFrame({
            "Lower Body Activation (%)": [float((strains["Core"] + strains["Quads"])/2)],
            "Neck Strain (%)": [float(strains["Neck"])]
        }))
        g_metric.metric("G-LOAD", f"{current_g:.1f} G", delta=f"{mode}")
        
        time.sleep(0.18)
