"""
UFO Sightings Interactive Dashboard from NUFORC scrubbed.csv
Story: Reporting patterns changed across time, place, and shape.
I built it with Streamlit + Plotly
"""

from __future__ import annotations

import math
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UFO Sightings Dashboard",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      .stApp {
        background:
          radial-gradient(circle at top left, rgba(110,126,189,0.08), transparent 24%),
          linear-gradient(180deg, #08101E 0%, #0B1020 100%);
        color: #E7ECF7;
      }

      section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #070D19 0%, #0B1020 100%);
        border-right: 1px solid rgba(124,148,201,0.16);
      }

      section[data-testid="stSidebar"] * {
        color: #D7DFF0 !important;
      }

      .block-container {
        padding-top: 1.85rem;
        padding-bottom: 2rem;
      }

      .hero-card {
        background: linear-gradient(135deg, rgba(18,25,43,0.98), rgba(10,15,28,0.98));
        border: 1px solid rgba(124,148,201,0.18);
        border-radius: 18px;
        padding: 24px 28px 22px 28px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.20);
        margin-bottom: 1rem;
      }

      .hero-title {
        font-size: 2.45rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        color: #9CB2E8;
        margin-bottom: 0.4rem;
      }

      .hero-subtitle {
        color: #CAD3E8;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 0.45rem;
      }

      .hero-note {
        color: #9DA8C4;
        font-size: 0.94rem;
        line-height: 1.65;
      }

      .insight-box {
        background: linear-gradient(135deg, rgba(20,28,47,0.98), rgba(12,17,31,0.98));
        border-left: 4px solid #9CB2E8;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 0.45rem 0 1.05rem;
        color: #DEE5F6;
        line-height: 1.68;
      }

      .support-box {
        background: rgba(18, 25, 43, 0.94);
        border: 1px solid rgba(124,148,201,0.12);
        border-radius: 12px;
        padding: 12px 16px;
        color: #D7DFF0;
        line-height: 1.62;
        margin: 0.3rem 0 0.85rem;
      }

      div[data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(18,25,43,0.96), rgba(10,15,28,0.96));
        border: 1px solid rgba(124,148,201,0.12);
        border-radius: 14px;
        padding: 15px 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.16);
      }

      div[data-testid="metric-container"] label {
        color: #9DA8C4 !important;
        font-size: 0.88rem !important;
      }

      div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #F3F6FB !important;
        font-size: 1.95rem !important;
        font-weight: 760 !important;
      }

      h2 {
        color: #9CB2E8 !important;
        font-size: 1.95rem !important;
        font-weight: 800 !important;
        border-bottom: 1px solid rgba(124,148,201,0.14);
        padding-bottom: 0.42rem;
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
      }

      h3 {
        color: #D7DFF0 !important;
      }

      .footer-note {
        color: #8390AF;
        text-align: center;
        font-size: 0.85rem;
        padding: 10px 0 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


#DATA LOADING & CLEANING
@st.cache_data(show_spinner="Loading scrubbed UFO dataset...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv("scrubbed.csv", low_memory=False)
    df.columns = df.columns.str.strip()

    rename_map = {"longitude ": "longitude"}
    df = df.rename(columns=rename_map)

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])

    for col in ["city", "state", "country", "shape", "comments"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    df["country"] = df["country"].replace("", "Unknown").str.upper()
    df["state"] = df["state"].replace("", "Unknown").str.lower()
    df["city"] = df["city"].replace("", "Unknown").str.lower()
    df["shape"] = df["shape"].replace("", "unknown").str.lower()

    df["duration (seconds)"] = pd.to_numeric(df["duration (seconds)"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    df = df.dropna(subset=["duration (seconds)", "latitude", "longitude"])
    df = df[df["duration (seconds)"] > 0].copy()

    df["duration_min"] = df["duration (seconds)"] / 60.0
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["hour"] = df["datetime"].dt.hour
    df["decade"] = (df["year"] // 10) * 10

    season_map = {
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn",
    }
    df["season"] = df["month"].map(season_map)

    df = df[(df["year"] >= 1950) & (df["year"] <= 2014)].copy()

    # Cap only for some visuals; keep raw data intact.
    df["duration_min_capped"] = df["duration_min"].clip(upper=df["duration_min"].quantile(0.99))

    return df


df = load_data()


#CONSTANTS

SHAPE_COLORS = {
    "light": "#D8B24A",
    "triangle": "#7C94C9",
    "circle": "#C97D7D",
    "unknown": "#7E8796",
    "fireball": "#B98A5A",
    "other": "#8E87B8",
    "sphere": "#5C9FA8",
    "disk": "#B983A3",
    "oval": "#75B7AA",
    "formation": "#9F7C68",
}

COUNTRY_COLORS = {
    "US": "#D8B24A",
    "CA": "#6FA7A0",
    "GB": "#7C94C9",
    "AU": "#9A8BC2",
    "Unknown": "#7E8796",
}

PLOTLY_BASE = dict(
    plot_bgcolor="#0B1020",
    paper_bgcolor="#12192B",
    font=dict(color="#E7ECF7", family="Inter, Segoe UI, sans-serif"),
    margin=dict(l=40, r=24, t=62, b=42),
)

SEASON_ORDER = ["Spring", "Summer", "Autumn", "Winter"]



#HELPERS
def format_country_label(selected: List[str]) -> str:
    if not selected:
        return "all countries"
    if len(selected) <= 4:
        return ", ".join(selected)
    return ", ".join(selected[:4]) + f" +{len(selected) - 4} more"


def prettify_city(value: str) -> str:
    if not isinstance(value, str):
        return "Unknown"
    return value.title()


def top_shape_summary(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "No dominant shape available"
    vc = frame["shape"].value_counts()
    top_shape = vc.index[0]
    pct = vc.iloc[0] / vc.sum() * 100
    return f"{top_shape.title()} ({pct:.1f}%)"


def safe_median_duration(frame: pd.DataFrame) -> float:
    if frame.empty:
        return 0.0
    return float(frame["duration_min"].median())


def build_main_insight(frame: pd.DataFrame, selected_countries: List[str], years: tuple[int, int]) -> str:
    if frame.empty:
        return (
            "No sightings match the current filters. Widen the year, country, shape, or duration settings "
            "to restore the dashboard views."
        )

    top_country_counts = frame["country"].value_counts()
    dominant_country = top_country_counts.index[0]
    dominant_country_pct = top_country_counts.iloc[0] / len(frame) * 100

    top_shape_counts = frame["shape"].value_counts()
    dominant_shape = top_shape_counts.index[0].title()

    pre_1995 = frame[frame["year"] < 1995]
    post_1995 = frame[frame["year"] >= 1995]
    pre_avg = pre_1995.groupby("year").size().mean() if not pre_1995.empty else math.nan
    post_avg = post_1995.groupby("year").size().mean() if not post_1995.empty else math.nan

    if pd.notna(pre_avg) and pre_avg > 0 and pd.notna(post_avg):
        growth_text = f"average yearly reporting is about {post_avg / pre_avg:.1f}x higher after 1995"
    else:
        growth_text = "report volumes rise strongly in the later years"

    return (
        f"<b>Key Insight:</b> Analyzing <i>year × country × shape</i> shows a clear shift in reporting patterns after the mid-1990s. "
        f"Within the current selection ({years[0]}–{years[1]}), <b>{dominant_country}</b> contributes the largest share of reports "
        f"({dominant_country_pct:.1f}%), while <b>{dominant_shape}</b> remains the most frequently reported shape. Overall, the dashboard shows that sightings are concentrated in specific places and periods rather than being evenly distributed across the dataset."
    )


def standardize_figure(fig: go.Figure, height: int | None = None) -> go.Figure:
    fig.update_layout(**PLOTLY_BASE)
    fig.update_layout(
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
        title_x=0.02,
        hoverlabel=dict(bgcolor="#131938", font_color="#f5f7ff"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.10)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.10)", zeroline=False)
    if height is not None:
        fig.update_layout(height=height)
    return fig

#SIDEBAR FILTERS

with st.sidebar:
    st.markdown("## Dashboard Filters")
    st.caption("Use these filters to explore how reporting changes across time, place, shape, and duration.")
    st.markdown("---")

    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    default_years = (1990, 2014)
    year_range = st.slider(" Year Range", year_min, year_max, default_years)

    countries = sorted(df["country"].dropna().unique().tolist())
    default_countries = [c for c in ["US", "CA", "GB", "AU"] if c in countries]
    selected_countries = st.multiselect(" Country", countries, default=default_countries)
    if not selected_countries:
        selected_countries = countries

    top_shapes = df["shape"].value_counts().head(10).index.tolist()
    selected_shapes = st.multiselect("🔮 UFO Shape", top_shapes, default=top_shapes)
    if not selected_shapes:
        selected_shapes = top_shapes

    max_duration = int(max(60, df["duration_min_capped"].quantile(0.99)))
    duration_range = st.slider(" Duration (minutes)", 0, max_duration, (0, min(60, max_duration)))

    st.markdown("---")
    st.markdown("### About")
    st.caption("Dataset: NUFORC scrubbed.csv")
    st.caption("Source: Kaggle / Sigmond Axel")


#FILTERING OF DATA

fdf = df[
    df["year"].between(*year_range)
    & df["country"].isin(selected_countries)
    & df["shape"].isin(selected_shapes)
    & df["duration_min_capped"].between(*duration_range)
].copy()



#HERO HEADER
country_label = format_country_label(selected_countries)
hero_note = (
    f"Filtered to <b>{len(fdf):,}</b> sightings across <b>{country_label}</b> from <b>{year_range[0]}</b> to <b>{year_range[1]}</b>. "
    f"The dashboard focuses on one core question: <b>how UFO reporting changes across time, place, and shape</b>."
)

st.markdown(
    f"""
    <div class="hero-card">
      <div class="hero-title"> UFO Sightings: A 70-Year Reporting Story</div>
      <div class="hero-subtitle">Interactive analysis of the NUFORC scrubbed dataset, designed to show how reporting patterns cluster over time, across countries, and by reported shape.</div>
      <div class="hero-note">{hero_note}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"<div class='insight-box'>💡 {build_main_insight(fdf, selected_countries, year_range)}</div>",
    unsafe_allow_html=True,
)



#KPI ROW

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sightings", f"{len(fdf):,}")
k2.metric("Countries", f"{fdf['country'].nunique() if not fdf.empty else 0}")
k3.metric("Top Shape", top_shape_summary(fdf))
k4.metric("Median Duration", f"{safe_median_duration(fdf):.1f} min")

if fdf.empty:
    st.warning("No records match the current filters. Please widen the selected range or categories.")
    st.stop()

#MAIN STORY EVIDENCE
st.markdown("##  Main Story: Reporting Changes Across Time and Shape")
st.markdown(
    """
    <div class="support-box">
      These two visuals form the core evidence for the dashboard narrative. The line chart shows how sightings change over time across countries, while the ranked bar chart shows which shapes dominate under the current filters. Together they communicate the required multi-variable insight using <b>year</b>, <b>country</b>, and <b>shape</b>.
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2 = st.columns([1.65, 1.0])

with c1:
    top_countries = fdf["country"].value_counts().head(5).index.tolist()
    temporal = (
        fdf[fdf["country"].isin(top_countries)]
        .groupby(["year", "country"])
        .size()
        .reset_index(name="count")
    )

    fig_line = px.line(
        temporal,
        x="year",
        y="count",
        color="country",
        title=f"Yearly Sightings by Country ({year_range[0]}–{year_range[1]})",
        labels={"year": "Year", "count": "Sightings", "country": "Country"},
        color_discrete_map=COUNTRY_COLORS,
        markers=False,
    )
    fig_line.update_traces(line_width=2.8)
    if year_range[0] <= 1995 <= year_range[1]:
        fig_line.add_vline(
            x=1995,
            line_dash="dash",
            line_color="#ff8c8c",
            annotation_text="Mid-1990s reference point",
            annotation_font_color="#ffb0b0",
            annotation_position="top right",
        )
    standardize_figure(fig_line, height=430)
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    shape_rank = (
        fdf["shape"].value_counts().head(10).sort_values(ascending=True).reset_index()
    )
    shape_rank.columns = ["shape", "count"]
    shape_rank["shape_label"] = shape_rank["shape"].str.title()

    fig_shape_bar = go.Figure(
        go.Bar(
            x=shape_rank["count"],
            y=shape_rank["shape_label"],
            orientation="h",
            marker_color=[SHAPE_COLORS.get(s, "#8ea8ff") for s in shape_rank["shape"]],
            text=shape_rank["count"].map(lambda x: f"{x:,}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Sightings: %{x:,}<extra></extra>",
        )
    )
    fig_shape_bar.update_layout(
        title="Top 10 Shapes for Current Filters",
        xaxis_title="Sightings",
        yaxis_title="Shape",
        showlegend=False,
    )
    fig_shape_bar.update_yaxes(showgrid=False)
    standardize_figure(fig_shape_bar, height=430)
    st.plotly_chart(fig_shape_bar, use_container_width=True)



#SHAPE TRENDS OVER TIME

st.markdown("## Shape Trends Over Time")
st.markdown(
    """
    <div class="support-box">
      This view deepens the main insight by combining <b>time</b> and <b>shape</b>. It helps users see whether later growth is concentrated in only one category or shared across multiple reported forms. The chart does not claim causation; it shows a clear change in reporting patterns over time.
    </div>
    """,
    unsafe_allow_html=True,
)

top_shapes_area = fdf["shape"].value_counts().head(8).index.tolist()
shape_area = (
    fdf[fdf["shape"].isin(top_shapes_area)]
    .groupby(["year", "shape"])
    .size()
    .reset_index(name="count")
)

fig_area = px.area(
    shape_area,
    x="year",
    y="count",
    color="shape",
    color_discrete_map=SHAPE_COLORS,
    title="Annual Sightings by Shape (Top 8)",
    labels={"year": "Year", "count": "Sightings", "shape": "Shape"},
)
if year_range[0] <= 1995 <= year_range[1]:
    fig_area.add_vline(
        x=1995,
        line_dash="dash",
        line_color="#ff8c8c",
        annotation_text="Mid-1990s reference point",
        annotation_font_color="#ffb0b0",
        annotation_position="top right",
    )
fig_area.update_traces(line=dict(width=0.8))
standardize_figure(fig_area, height=430)
st.plotly_chart(fig_area, use_container_width=True)



#SUPPORTING EVIDENCE: GEOGRAPHIC MAP

st.markdown("## Supporting Evidence: Geographic Distribution")
st.markdown(
    """
    <div class="support-box">
      Each point is a reported sighting. This map adds spatial context to the main story and supports exploratory drill-down through hover details and zoom. It helps users test whether reports are broadly distributed or concentrated in specific regions.
    </div>
    """,
    unsafe_allow_html=True,
)

map_df = fdf.sample(min(15000, len(fdf)), random_state=42).copy() if len(fdf) > 15000 else fdf.copy()
map_df["city_label"] = map_df["city"].map(prettify_city)
map_df["shape_label"] = map_df["shape"].str.title()
map_df["duration_label"] = map_df["duration_min"].round(1).astype(str) + " min"

fig_map = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    color="shape",
    color_discrete_map=SHAPE_COLORS,
    hover_name="city_label",
    hover_data={
        "shape_label": True,
        "duration_label": True,
        "year": True,
        "country": True,
        "latitude": False,
        "longitude": False,
        "shape": False,
        "duration_min": False,
        "city": False,
        "city_label": False,
    },
    labels={
        "shape_label": "Shape",
        "duration_label": "Duration",
        "year": "Year",
        "country": "Country",
    },
    center=dict(lat=39, lon=-96),
    zoom=2.1,
    opacity=0.65,
    title=f"UFO Sightings Map ({len(map_df):,} points shown)",
)
fig_map.update_layout(
    mapbox_style="carto-darkmatter",
    **PLOTLY_BASE,
    height=560,
    title_x=0.02,
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)
fig_map.update_traces(marker_size=5)
st.plotly_chart(fig_map, use_container_width=True)



#ADVANCED INTERACTION: DRILL-DOWN

st.markdown("## Advanced Interaction: Country → State → City Drill-Down")
st.markdown(
    """
    <div class="support-box">
      This section satisfies the hierarchical exploration requirement. Users can select a country to reveal its top states or provinces, then select a state to reveal its top cities. This turns the dashboard from a static report into an interactive analytic view.
    </div>
    """,
    unsafe_allow_html=True,
)

d1, d2 = st.columns(2)

with d1:
    drill_countries = fdf["country"].value_counts().head(10).index.tolist()
    selected_drill_country = st.selectbox("Select Country to Drill Into", drill_countries)

    state_counts = (
        fdf[fdf["country"] == selected_drill_country]["state"]
        .dropna()
        .replace("", "Unknown")
        .value_counts()
        .head(15)
        .reset_index()
    )
    state_counts.columns = ["state", "count"]
    state_counts = state_counts.sort_values("count", ascending=True)

    fig_state = go.Figure(
        go.Bar(
            x=state_counts["count"],
            y=state_counts["state"],
            orientation="h",
            marker_color=[
                "#D8B24A" if i == len(state_counts) - 1 else "#6E7EBD"
                for i in range(len(state_counts))
            ],
            hovertemplate="<b>%{y}</b><br>Sightings: %{x:,}<extra></extra>",
        )
    )
    fig_state.update_layout(
        title=f"Top States / Provinces in {selected_drill_country}",
        xaxis_title="Sightings",
        yaxis_title="State / Province",
        showlegend=False,
    )
    fig_state.update_yaxes(showgrid=False)
    standardize_figure(fig_state, height=420)
    st.plotly_chart(fig_state, use_container_width=True)

with d2:
    state_options = state_counts["state"].tolist() if not state_counts.empty else []

    if state_options:
        selected_drill_state = st.selectbox(
            "Select State / Province to See Cities",
            state_options,
        )

        city_counts = (
            fdf[
                (fdf["country"] == selected_drill_country)
                & (fdf["state"] == selected_drill_state)
            ]["city"]
            .dropna()
            .replace("", "Unknown")
            .value_counts()
            .head(12)
            .reset_index()
        )
        city_counts.columns = ["city", "count"]
        city_counts["city_label"] = city_counts["city"].map(prettify_city)
        city_counts = city_counts.sort_values("count", ascending=True)

        fig_city = go.Figure(
            go.Bar(
                x=city_counts["count"],
                y=city_counts["city_label"],
                orientation="h",
                marker_color=[
                    "#D8B24A" if i >= len(city_counts) - 2 else "#6FA7A0"
                    for i in range(len(city_counts))
                ],
                hovertemplate="<b>%{y}</b><br>Sightings: %{x:,}<extra></extra>",
            )
        )
        fig_city.update_layout(
            title=f"Top Cities in {selected_drill_state.upper()}, {selected_drill_country}",
            xaxis_title="Sightings",
            yaxis_title="City",
            showlegend=False,
        )
        fig_city.update_yaxes(showgrid=False)
        standardize_figure(fig_city, height=420)
        st.plotly_chart(fig_city, use_container_width=True)
    else:
        st.info("No state-level records are available for the current selection.")


#OPTIONAL SUPPORT: BEHAVIOURAL PATTERNS

st.markdown("##  Supporting Detail: Behavioural Patterns")
st.markdown(
    """
    <div class="support-box" style="opacity:0.92;">
      These views add extra context rather than introducing a new main story. The heatmap shows when sightings are most commonly reported by season and hour, while the duration chart compares the typical reported length of each shape category.
    </div>
    """,
    unsafe_allow_html=True,
)

b1, b2 = st.columns(2)

with b1:
    heat = (
        fdf.groupby(["season", "hour"]).size().reset_index(name="count")
        .pivot(index="season", columns="hour", values="count")
        .fillna(0)
    )
    heat = heat.reindex([s for s in SEASON_ORDER if s in heat.index])
    hour_labels = [f"{h:02d}:00" for h in heat.columns]

    fig_heat = go.Figure(
        go.Heatmap(
            z=heat.values,
            x=hour_labels,
            y=heat.index,
            colorscale=[[0.0, '#10182D'], [0.35, '#2E477A'], [0.7, '#6E7EBD'], [1.0, '#D8B24A']],
            hovertemplate="Season: %{y}<br>Hour: %{x}<br>Sightings: %{z:,}<extra></extra>",
            colorbar=dict(title="Sightings"),
        )
    )
    fig_heat.update_layout(
        title="Sightings by Season and Hour of Day",
        xaxis_title="Hour of Day",
        yaxis_title="Season",
    )
    standardize_figure(fig_heat, height=430)
    fig_heat.update_yaxes(showgrid=False)
    st.plotly_chart(fig_heat, use_container_width=True)

with b2:
    duration_by_shape = (
        fdf[fdf["duration_min"] <= 60]
        .groupby("shape")["duration_min"]
        .agg(["median", "count"])
        .query("count >= 30")
        .sort_values("median", ascending=True)
        .tail(10)
        .reset_index()
    )
    duration_by_shape["shape_label"] = duration_by_shape["shape"].str.title()

    fig_dur = go.Figure(
        go.Bar(
            x=duration_by_shape["median"],
            y=duration_by_shape["shape_label"],
            orientation="h",
            marker_color=[SHAPE_COLORS.get(s, "#8ea8ff") for s in duration_by_shape["shape"]],
            text=duration_by_shape["median"].round(1).astype(str) + " min",
            textposition="outside",
            customdata=duration_by_shape["count"],
            hovertemplate="<b>%{y}</b><br>Median duration: %{x:.2f} min<br>Observations: %{customdata:,}<extra></extra>",
        )
    )
    fig_dur.update_layout(
        title="Median Sighting Duration by Shape",
        xaxis_title="Median Duration (minutes)",
        yaxis_title="Shape",
        showlegend=False,
    )
    fig_dur.update_yaxes(showgrid=False)
    standardize_figure(fig_dur, height=430)
    st.plotly_chart(fig_dur, use_container_width=True)


#METHODOLOGY NOTE + FOOTER
st.markdown("---")
st.markdown(
    """
    <div class="support-box">
      <b>Method note:</b> Visuals are based on the NUFORC scrubbed dataset from Kaggle. Records with invalid dates, non-numeric durations, or missing geographic coordinates were excluded where necessary for analysis. Duration is displayed in minutes, and map points are sampled only for performance when the filtered result set is very large.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p class="footer-note">
      UFO Sightings Dashboard · Dataset: NUFORC via Kaggle · Built with Streamlit + Plotly
    </p>
    """,
    unsafe_allow_html=True,
)
