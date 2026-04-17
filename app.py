import streamlit as st
import numpy as np
import time
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="NeuroFlight™ - Tactical Analytics", layout="wide", initial_sidebar_state="collapsed")

# --- REALISTINEN AGGRESSIIVINEN G-PROFIILI ---
def generate_dogfight_profile():
    t = np.arange(0, 250)
    g = np.ones(250)
    
    # Veto 1: Nopea nousu 7G, lyhyt pito, ja ROMAHTAVA pudotus
    g[30:35] = np.linspace(1.0, 7.0, 5) 
    g[35:50] = 7.0 + np.random.normal(0, 0.1, 15)
    g[50:53] = np.linspace(7.0, 1.0, 3) # <--- Pystysuora drop
    
    # Veto 2: Rajumpi veto 9G, pito, ja raju pudotus 3G:hen
    g[90:94] = np.linspace(1.0, 9.0, 4)
    g[94:110] = 9.0 + np.random.normal(0, 0.1, 16)
    g[110:113] = np.linspace(9.0, 3.0, 3) # <--- Nopea kevennys
    g[113:140] = 3.0 + np.random.normal(0, 0.05, 27) # 3G ylläpito
    g[140:143] = np.linspace(3.0, 1.0, 3) # Lopetus
    
    # Lisätään instrumentaalista kohinaa koko käyrään
    return np.clip(g + np.random.normal(0, 0.05, 250), 0.8, 9.5)

flight_data = generate_dogfight_profile()

# --- APUFUNKTIOT VISUALISOINTIIN ---
def get_heatmap_color(strain_percent):
    if strain_percent < 50:
        # Vihreä (0,255,0) -> Keltainen (255,255,0)
        r = int((strain_percent / 50) * 255)
        g = 255
    else:
        # Keltainen (255,255,0) -> Punainen (255,0,0)
        r = 255
        g = int(255 - ((strain_percent - 50) / 50) * 255)
    return f'rgb({r}, {g}, 0)'

st.title("🛡️ NeuroFlight™ Sensor Diagnostics")
st.write("Aggressive G-Dynamics & Anticipatory Bio-Response")

# --- VALINTA ---
c1, c2 = st.columns(2)
start_opt = c1.button("🚀 Start Optimal Mission (Expert)", use_container_width=True)
start_sub = c2.button("⚠️ Start Suboptimal Mission (Trainee)", use_container_width=True)

col1, col2 = st.columns([1.2, 2])

with col1:
    st.subheader("Anatomical Heatmap")
    # Tähän tulee iso dynaaminen vartalo-heatmap
    heatmap_placeholder = st.empty()

with col2:
    st.subheader("Tactical Data (G vs. % MVC)")
    # Käytetään Plotlyä, jotta saadaan kaksiakselinen kaavio
    chart_placeholder = st.empty()
    g_metric = st.empty()

# --- ANIMATION LOOP ---
if start_opt or start_sub:
    mode = "OPTIMAL" if start_opt else "SUBOPTIMAL"
    
    # Alustetaan historiadata
    time_hist, g_hist, core_hist, neck_hist = [], [], [], []
    
    for i in range(len(flight_data)):
        current_g = flight_data[i]
        
        # Katsotaan tulevaa G-voimaa (ennakointi, lyhyempi ikkuna dogfightissa)
        future_g = flight_data[min(i + 5, len(flight_data)-1)]
        
        # Biologinen kohina (Gaussian noise)
        noise = lambda: np.random.normal(0, 2.0)
        
        if mode == "OPTIMAL":
            # Optimaalisessa tilassa core/quads nousee agressiivisesti G:n mukana
            prep = max(current_g, future_g)
            strains = {
                "Neck": int(np.clip((current_g**1.5) * 1.5 + noise(), 5, 60)),
                "Back": int(np.clip((prep**1.7) * 1.4 + noise(), 10, 85)),
                "Core": int(np.clip((prep**1.9) * 1.2 + noise(), 10, 95)),
                "Glutes": int(np.clip((prep**2.0) * 1.1 + noise(), 15, 100)),
                "Quads": int(np.clip((prep**2.0) * 1.1 + noise(), 15, 100))
            }
        else:
            # Suboptimaalisessa niska joutuu repivässä liikkeessä koville
            strains = {
                "Neck": int(np.clip((current_g**2.2) * 1.8 + noise(), 0, 100)),
                "Back": int(np.clip((current_g**1.8) * 1.5 + noise(), 0, 90)),
                "Core": int(np.clip((current_g**1.5) * 1.1 + noise(), 0, 60)),
                "Glutes": int(np.clip((current_g**1.4) * 1.0 + noise(), 0, 50)),
                "Quads": int(np.clip((current_g**1.4) * 1.0 + noise(), 0, 50))
            }

        # 1. PÄIVITETÄÄN DYNAAMINEN VARTALO-HEATMAP
        heatmap_fig = go.Figure()
        
        # Anatomiset koordinaatit [x, y] - Normalisoitu 0-100 koordinaatistoon
        muscle_coords = {
            "Neck": [50, 88], "Back": [50, 65], "Core": [50, 55],
            "Glutes": [50, 42], "Quads": [50, 25]
        }
        
        # Sijoitetaan sensoripisteet
        for m, pos in muscle_coords.items():
            val = strains[m]
            heatmap_fig.add_trace(go.Scatter(
                x=[pos[0]], y=[pos[1]],
                mode='markers+text',
                text=[f"{val}%"], textposition="top center",
                marker=dict(size=25 + (val/4), color=get_heatmap_color(val), 
                            line=dict(width=2, color='white'), opacity=0.8),
                showlegend=False, hoverinfo="none"
            ))

        # SVG-ihmissiluetti taustalle (tämä korvaa "HUMAN DYNAMICS" -tekstin)
        heatmap_fig.add_annotation(
            x=50, y=50,
            text="👤", font=dict(size=120, color="rgba(255,255,255,0.08)"), # <--- SVG-ikoni haamuna
            showarrow=False
        )
        
        heatmap_fig.update_layout(
            template="plotly_dark", height=600, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
        )
        heatmap_placeholder.plotly_chart(heatmap_fig, use_container_width=True, key=f"heatmap_{i}")

        # 2. PÄIVITETÄÄN DYNAAMINEN KAKSI-AKSELINEN G-KÄYRÄ (Optimoidusti)
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
        g_metric.metric("G-LOAD (G)", f"{current_g:.1f} G", delta=f"{strains['Core']}% Core")
        
        time.sleep(0.12)
