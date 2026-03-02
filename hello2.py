import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="AWS Sensor Dashboard", layout="wide")

st.title("📊 AWS Sensor Monitoring Dashboard")
st.markdown("September 2025 to Present")
st.divider()

uploaded_file = st.file_uploader("Upload NHPC AWS Excel File", type=["xlsx"])

if uploaded_file is not None:

    # -------- READ FILE --------
    df = pd.read_excel(uploaded_file, header=2)
    df.columns = df.columns.str.strip()

    # -------- AUTO DATE COLUMN DETECTION --------
    date_col = None
    for col in df.columns:
        if "date" in col.lower() or "period" in col.lower():
            date_col = col
            break

    if date_col is None:
        st.error("❌ Date column not found.")
        st.stop()

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    df = df.rename(columns={date_col: "Date"})
    df = df.dropna(subset=["Date"])

    df = df[df["Date"] >= pd.Timestamp("2025-09-01")]
    df = df.sort_values("Date")

    # -------- CREATE FULL DATE RANGE (For Line Break) --------
    full_range = pd.date_range(
        start=df["Date"].min(),
        end=df["Date"].max(),
        freq="D"
    )

    df = df.set_index("Date").reindex(full_range)
    df.index.name = "Date"
    df = df.reset_index()

    # -------- SENSOR AUTO DETECTION --------
    sensor_groups = {}

    for col in df.columns:
        if " - " in col:
            sensor_name = col.split(" - ")[0]
            sensor_groups.setdefault(sensor_name, []).append(col)

    if not sensor_groups:
        st.error("❌ No sensor columns detected.")
        st.stop()

    sensors = list(sensor_groups.keys())
    selected_sensor = st.selectbox("Select Sensor", sensors)

    sensor_cols = sensor_groups[selected_sensor]
    sensor_df = df[["Date"] + sensor_cols]

    # -------- CREATE GRAPH --------
    fig = go.Figure()

    for col in sensor_cols:
        if "Min" in col:
            color = "blue"
        elif "Avg" in col:
            color = "green"
        elif "Max" in col:
            color = "red"
        else:
            color = "black"

        fig.add_trace(go.Scatter(
            x=sensor_df["Date"],
            y=sensor_df[col],
            mode="lines",
            name=col.split(" - ")[-1],
            line=dict(color=color, width=2),
            connectgaps=False  # 🔥 Important for line break
        ))

    fig.update_layout(
        title=f"{selected_sensor} Trend (Min / Avg / Max)",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(title="Legend"),
        height=600,
        margin=dict(l=40, r=40, t=80, b=40)
    )

    # -------- SHOW GRAPH WITH FULL DOWNLOAD SUPPORT --------
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"{selected_sensor}_trend_full",
                "height": 800,
                "width": 1600,
                "scale": 3  # High quality HD export
            }
        }
    )

    st.success("📸 Use the camera icon (top-right of graph) to download full HD image.")

else:
    st.info("📂 Upload the AWS Excel file to continue.")