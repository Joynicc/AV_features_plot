import streamlit as st
import pandas as pd
import plotly.express as px
import datetime as dt
import os

st.set_page_config(layout="wide", page_title="AV Sensor Dashboard")

# -------------------------------
# Load data
# -------------------------------
@st.cache_data
def load_data(path="./input_data_0925.csv"):
    if not os.path.exists(path):
        st.error(f"❌ File not found: {path}")
        st.stop()

    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        st.error("❌ Missing 'timestamp' column in dataset.")
        st.stop()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    return df

df = load_data()

# -------------------------------
# Define features
# -------------------------------
features = [
    "driveSystem_actualSpeed",
    "localization_Roll",
    "driveSystem_hydraulicBrakePressure",
    "localization_Pitch",
    "driving_mode"   # 👈 new feature
]

# -------------------------------
# Time range setup
# -------------------------------
min_time_val = df["timestamp"].min()
max_time_val = df["timestamp"].max()

min_time = min_time_val.to_pydatetime() if hasattr(min_time_val, "to_pydatetime") else min_time_val
max_time = max_time_val.to_pydatetime() if hasattr(max_time_val, "to_pydatetime") else max_time_val

# -------------------------------
# Overview line plot
# -------------------------------
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

# -------------------------------
# Time window selector
# -------------------------------
time_window = st.slider(
    "Select time window (applies to all plots)",
    min_value=min_time,
    max_value=max_time,
    value=(min_time, max_time),
    format="YYYY-MM-DD HH:mm:ss",
    step=dt.timedelta(seconds=1),
)

# Filter data by selected window
filtered_df = df[(df["timestamp"] >= time_window[0]) & (df["timestamp"] <= time_window[1])]
st.write(f"**Active range:** {time_window[0]} → {time_window[1]}")

# -------------------------------
# Plot section
# -------------------------------
cols = st.columns(2)

for i, feature in enumerate(features):
    if feature not in filtered_df.columns:
        st.warning(f"⚠️ Missing column in data: {feature}")
        continue

    # Special handling for driving_mode
    if feature == "driving_mode":
        # Get unique values actually present
        unique_modes = sorted(filtered_df["driving_mode"].dropna().unique())

        # Convert to string category (discrete y-axis)
        filtered_df["driving_mode_str"] = filtered_df["driving_mode"].astype(str)

        fig = px.line(
            filtered_df,
            x="timestamp",
            y="driving_mode_str",
            height=250,
            markers=True,  # show points for clarity
        )

        fig.update_layout(
            margin=dict(l=40, r=20, t=10, b=10),
            xaxis_title=None,
            yaxis_title="driving_mode",
            hovermode="x unified",
            yaxis=dict(
                categoryorder="array",
                categoryarray=[str(v) for v in unique_modes],  # only show existing values
                showgrid=True,
            ),
        )

    else:
        # Standard numeric feature plots
        fig = px.line(
            filtered_df,
            x="timestamp",
            y=feature,
            height=250,
        )
        fig.update_layout(
            margin=dict(l=40, r=20, t=10, b=10),
            xaxis_title=None,
            yaxis_title=feature,
            hovermode="x unified",
        )
        fig.update_xaxes(rangeslider_visible=False)

    with cols[i % 2]:
        st.plotly_chart(fig, use_container_width=True)
