from __future__ import annotations

from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from ..constants import PORTS


PALETTE = {"navy": "#0B1220", "panel": "#121C2D", "muted": "#8293A8", "cyan": "#51D5E8", "green": "#35C98A", "amber": "#F4B860", "red": "#F07178", "purple": "#9B8CFF"}


def inject_css() -> None:
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      h1,h2,h3,h4 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.035em; }
      .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
      [data-testid="stSidebar"] { border-right: 1px solid rgba(148,163,184,.13); }
      [data-testid="stMetric"] { background: linear-gradient(145deg,rgba(18,28,45,.95),rgba(14,24,39,.72)); border: 1px solid rgba(148,163,184,.14); padding: 15px 17px; border-radius: 15px; }
      [data-testid="stMetricLabel"] { color: #91A2B8 !important; font-size: .82rem !important; }
      [data-testid="stMetricValue"] { font-family: 'Space Grotesk',sans-serif; letter-spacing: -.04em; }
      div[data-testid="stForm"] { border: 1px solid rgba(148,163,184,.17); border-radius: 14px; padding: 16px; background: rgba(18,28,45,.48); }
      .nexus-kicker { text-transform: uppercase; letter-spacing: .16em; color: #51D5E8; font-size: .70rem; font-weight: 700; }
      .nexus-hero { padding: 22px 24px; border: 1px solid rgba(81,213,232,.20); border-radius: 18px; background: radial-gradient(circle at 88% 5%, rgba(81,213,232,.13), transparent 34%), linear-gradient(120deg,#111D30,#0B1422); margin-bottom: 18px; }
      .nexus-hero h1 { margin: 6px 0 5px 0; font-size: 2.25rem; }
      .nexus-hero p { color: #A4B3C6; margin: 0; }
      .nexus-card { padding: 16px 18px; background: linear-gradient(145deg,rgba(18,28,45,.95),rgba(14,24,39,.70)); border: 1px solid rgba(148,163,184,.14); border-radius: 15px; min-height: 100px; }
      .nexus-card-label { font-size: .76rem; color: #91A2B8; text-transform: uppercase; letter-spacing: .08em; }
      .nexus-card-value { font: 700 1.65rem 'Space Grotesk',sans-serif; margin-top: 7px; }
      .nexus-card-sub { font-size: .76rem; color: #8293A8; margin-top: 4px; }
      .nexus-note { font-size: .82rem; color: #91A2B8; }
      .status-pill { border-radius: 30px; padding: 4px 9px; font-size: .73rem; font-weight: 600; display: inline-block; }
      .small-muted { color: #8293A8; font-size: .78rem; }
      .stButton button { border-radius: 9px; }
      a { color: #51D5E8 !important; }
    </style>
    """, unsafe_allow_html=True)


def page_header(kicker: str, title: str, subtitle: str = "") -> None:
    st.markdown(f"<div class='nexus-kicker'>{kicker}</div>", unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def hero(title: str, subtitle: str, kicker: str = "GLOBAL LOGISTICS CONTROL PLANE") -> None:
    st.markdown(
        f"<div class='nexus-hero'><div class='nexus-kicker'>{kicker}</div><h1>{title}</h1><p>{subtitle}</p></div>",
        unsafe_allow_html=True,
    )


def usd(value: float, currency: str = "USD") -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    return f"{currency} {v:,.0f}" if abs(v) >= 1000 else f"{currency} {v:,.2f}"



def currency_breakdown(df: pd.DataFrame, amount_col: str, currency_col: str = "currency") -> str:
    """Format totals by currency without silently adding unlike currencies."""
    if df.empty or amount_col not in df.columns or currency_col not in df.columns:
        return "—"
    totals = df.groupby(currency_col)[amount_col].sum().sort_index()
    return " · ".join(f"{cur} {value:,.0f}" for cur, value in totals.items())


def status_color(status: str) -> str:
    return {
        "Delivered": "#35C98A", "In transit": "#51D5E8", "Booked": "#9B8CFF",
        "Customs hold": "#F4B860", "Exception": "#F07178", "Draft": "#8293A8",
        "Quoted": "#B39DDB", "Cancelled": "#7A8798",
    }.get(status, "#8293A8")


def plotly_dark(fig, height: int | None = None):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#C9D5E3", size=11),
        margin=dict(l=8, r=8, t=32, b=8), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    if height:
        fig.update_layout(height=height)
    return fig


def map_figure(shipments: pd.DataFrame, limit: int = 24):
    fig = go.Figure()
    if shipments.empty:
        return plotly_dark(fig, 360)
    subset = shipments.head(limit)
    for _, row in subset.iterrows():
        if not row.get("origin_lat") or not row.get("destination_lat"):
            continue
        fig.add_trace(go.Scattergeo(
            lon=[row["origin_lon"], row["destination_lon"]],
            lat=[row["origin_lat"], row["destination_lat"]],
            mode="lines", line=dict(width=1.2, color="rgba(81,213,232,.45)"),
            hovertemplate=f"{row['reference']}<br>{row['origin']} → {row['destination']}<extra></extra>",
            showlegend=False,
        ))
    ports = {}
    for _, row in subset.iterrows():
        for side in ["origin", "destination"]:
            name = row[side]
            if name not in ports:
                ports[name] = (row[f"{side}_lat"], row[f"{side}_lon"])
    if ports:
        fig.add_trace(go.Scattergeo(
            lon=[v[1] for v in ports.values()], lat=[v[0] for v in ports.values()],
            text=list(ports.keys()), mode="markers", marker=dict(size=5, color="#51D5E8", line=dict(width=.5, color="#EAFBFF")),
            hovertemplate="%{text}<extra></extra>", showlegend=False,
        ))
    fig.update_geos(
        projection_type="natural earth", showland=True, landcolor="#17253A", showocean=True,
        oceancolor="#0B1626", showcountries=True, countrycolor="#293B52",
        showcoastlines=True, coastlinecolor="#293B52", bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(title="Global shipment lanes · synthetic demo network", height=410, margin=dict(l=0, r=0, t=35, b=0))
    return plotly_dark(fig)


def empty_state(message: str):
    st.info(message)


def safe_dataframe(df: pd.DataFrame, columns: list[str] | None = None, height: int = 320):
    if df.empty:
        st.info("No records match the current filters.")
        return
    display = df[columns].copy() if columns else df.copy()
    st.dataframe(display, use_container_width=True, hide_index=True, height=height)
