import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data
from utils.forecasting import forecast_range

st.title("📅 Forecast Planner")

df = load_data()

if df is None:
    st.warning("No data file found")
    st.stop()

stations = sorted(df["Station"].unique())

col1, col2, col3 = st.columns(3)

station = col1.selectbox("Station", stations)
from_date = col2.date_input("From Date")
to_date = col3.date_input("To Date")

buffer_pct = st.slider("Driver Buffer %", 0, 20, 10)


def confidence_label(history_used):
    if history_used >= 4:
        return "High"
    elif history_used >= 2:
        return "Medium"
    else:
        return "Low"


if st.button("Generate Forecast"):

    result = forecast_range(
        df,
        station,
        pd.to_datetime(from_date),
        pd.to_datetime(to_date),
        history_weeks=4,
        buffer_pct=buffer_pct
    )

    result["Confidence"] = result["History Used"].apply(confidence_label)

    st.subheader("Driver Requirement Summary")

    summary = (
        result
        .groupby("Wave", as_index=False)
        .agg({
            "Expected Orders": "sum",
            "Drivers Needed": "sum"
        })
    )

    total_drivers = result["Drivers Needed"].sum()
    total_orders = result["Expected Orders"].sum()

    s1, s2, s3 = st.columns(3)

    s1.metric("Total Expected Orders", f"{total_orders:,.0f}")
    s2.metric("Total Drivers Needed", f"{total_drivers:,.0f}")

    if not summary.empty:
        morning_drivers = summary.loc[summary["Wave"] == "Morning", "Drivers Needed"].sum()
        afternoon_drivers = summary.loc[summary["Wave"] == "Afternoon", "Drivers Needed"].sum()
        s3.metric("Morning / Afternoon Drivers", f"{morning_drivers:.0f} / {afternoon_drivers:.0f}")

    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.subheader("Forecast Details")

    st.dataframe(result, use_container_width=True, hide_index=True)

    csv = result.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Forecast CSV",
        data=csv,
        file_name="forecast_output.csv",
        mime="text/csv",
    )

    st.divider()
    st.subheader("Forecast Charts")

    c1, c2 = st.columns(2)

    fig_orders = px.bar(
        result,
        x="Date",
        y="Expected Orders",
        color="Wave",
        barmode="group",
        title="Expected Orders by Date and Wave",
        text="Expected Orders",
    )

    c1.plotly_chart(fig_orders, use_container_width=True)

    fig_drivers = px.bar(
        result,
        x="Date",
        y="Drivers Needed",
        color="Wave",
        barmode="group",
        title="Drivers Needed by Date and Wave",
        text="Drivers Needed",
    )

    c2.plotly_chart(fig_drivers, use_container_width=True)