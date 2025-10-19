import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
import os

st.set_page_config(layout="wide", page_title="AV Sensor Dashboard")

#st.title("")


@st.cache_data
def load_data(path="./filtered_2025-09-25.parquet"):
    if not os.path.exists(path):
        st.error(f"❌ File not found: {path}")
        st.stop()

    df = pd.read_parquet(path)  #df = pd.read_parquet(path)

    if "timestamp" not in df.columns:
        st.error("❌ Missing 'timestamp' column in dataset.")
        st.stop()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    return df

df = load_data()

features = [
    "driveSystem_actualSpeed",
    "localization_Roll",
    "driveSystem_hydraulicBrakePressure",
    "localization_Pitch"
]

min_time_val = df["timestamp"].min()
max_time_val = df["timestamp"].max()

min_time = min_time_val.to_pydatetime() if hasattr(min_time_val, "to_pydatetime") else min_time_val
max_time = max_time_val.to_pydatetime() if hasattr(max_time_val, "to_pydatetime") else max_time_val



fig_filter = px.line(
    df,
    x="timestamp",
    y="driveSystem_actualSpeed",
    height=150,
)
fig_filter.update_layout(
    margin=dict(l=20, r=20, t=10, b=10),
    xaxis_title=None,
    yaxis_title="Speed",
    hovermode="x unified",
)
fig_filter.update_xaxes(rangeslider_visible=True)

st.plotly_chart(fig_filter, use_container_width=True)


# time window slider
time_window = st.slider(
    "Select time window (applies to all plots)",
    min_value=min_time,
    max_value=max_time,
    value=(min_time, max_time),
    format="YYYY-MM-DD HH:mm:ss",
    step=dt.timedelta(seconds=1),  # 👈 precise 1-second step
)

# Filter dataset based on selected time
filtered_df = df[(df["timestamp"] >= time_window[0]) & (df["timestamp"] <= time_window[1])]

st.write(f"**Active range:** {time_window[0]} → {time_window[1]}")


# Display all feature plots (with y-axis labels)

cols = st.columns(2)

for i, feature in enumerate(features):
    fig = px.line(
        filtered_df,
        x="timestamp",
        y=feature,
        height=250,
    )
    fig.update_layout(
        margin=dict(l=40, r=20, t=10, b=10),
        xaxis_title=None,
        yaxis_title=feature,  # keep y-axis labels
        hovermode="x unified",
    )
    fig.update_xaxes(rangeslider_visible=False)

    with cols[i % 2]:
        st.plotly_chart(fig, use_container_width=True)
