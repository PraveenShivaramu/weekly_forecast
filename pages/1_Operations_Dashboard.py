import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data

st.title("📊 Operations Dashboard")

df = load_data()

if df is None:
    st.warning("No data file found. Please check data/delivery_data.xlsx")
    st.stop()

# Date filters
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

col1, col2, col3 = st.columns(3)

station_options = ["All Stations"] + sorted(df["Station"].dropna().unique().tolist())

selected_station = col1.selectbox("Station", station_options)
start_date = col2.date_input("Start Date", min_date)
end_date = col3.date_input("End Date", max_date)

# Filter data
filtered = df[
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date)
].copy()

if selected_station != "All Stations":
    filtered = filtered[filtered["Station"] == selected_station]

if filtered.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# Core calculations
orders_assigned = filtered["Orders Assigned"].sum()
orders_delivered = filtered["Orders Delivered"].sum()
first_attempt = filtered["First Attempt Delivered"].sum()
rto_orders = filtered["RTO Orders"].sum()
drivers_used = filtered["Drivers Used"].sum()
avg_backlog = filtered["Backlog"].mean()

otd = orders_delivered / orders_assigned if orders_assigned > 0 else 0
fad = first_attempt / orders_assigned if orders_assigned > 0 else 0
rto = rto_orders / orders_assigned if orders_assigned > 0 else 0
productivity = orders_delivered / drivers_used if drivers_used > 0 else 0

# KPI cards
st.subheader("Regional / Station KPIs")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Orders Assigned", f"{orders_assigned:,.0f}")
k2.metric("Orders Delivered", f"{orders_delivered:,.0f}")
k3.metric("OTD %", f"{otd:.1%}")
k4.metric("Productivity", f"{productivity:.1f}")

k5, k6, k7, k8 = st.columns(4)

k5.metric("FAD %", f"{fad:.1%}")
k6.metric("RTO %", f"{rto:.1%}")
k7.metric("Avg Backlog", f"{avg_backlog:.1f}")
k8.metric("Drivers Used", f"{drivers_used:,.0f}")

st.divider()

# Station summary table
st.subheader("Station Summary")

summary = (
    filtered
    .groupby("Station", as_index=False)
    .agg({
        "Orders Assigned": "sum",
        "Orders Delivered": "sum",
        "First Attempt Delivered": "sum",
        "RTO Orders": "sum",
        "Backlog": "mean",
        "Drivers Used": "sum"
    })
)

summary["OTD %"] = summary["Orders Delivered"] / summary["Orders Assigned"]
summary["FAD %"] = summary["First Attempt Delivered"] / summary["Orders Assigned"]
summary["RTO %"] = summary["RTO Orders"] / summary["Orders Assigned"]
summary["Productivity"] = summary["Orders Delivered"] / summary["Drivers Used"]

# Clean formatting
display_summary = summary[
    [
        "Station",
        "Orders Assigned",
        "Orders Delivered",
        "OTD %",
        "FAD %",
        "RTO %",
        "Backlog",
        "Drivers Used",
        "Productivity",
    ]
].copy()

display_summary["OTD %"] = display_summary["OTD %"].map(lambda x: f"{x:.1%}")
display_summary["FAD %"] = display_summary["FAD %"].map(lambda x: f"{x:.1%}")
display_summary["RTO %"] = display_summary["RTO %"].map(lambda x: f"{x:.1%}")
display_summary["Backlog"] = display_summary["Backlog"].map(lambda x: f"{x:.1f}")
display_summary["Productivity"] = display_summary["Productivity"].map(lambda x: f"{x:.1f}")

st.dataframe(display_summary, use_container_width=True, hide_index=True)

# Download station summary
csv = display_summary.to_csv(index=False).encode("utf-8")
st.divider()
st.subheader("Visual Analysis")

chart_data = summary.copy()

c1, c2 = st.columns(2)

fig_orders = px.bar(
    chart_data,
    x="Station",
    y="Orders Delivered",
    title="Orders Delivered by Station",
    text="Orders Delivered",
)

c1.plotly_chart(fig_orders, use_container_width=True)

fig_otd = px.bar(
    chart_data,
    x="Station",
    y="OTD %",
    title="OTD % by Station",
    text=chart_data["OTD %"].map(lambda x: f"{x:.1%}"),
)

fig_otd.update_yaxes(tickformat=".0%")

c2.plotly_chart(fig_otd, use_container_width=True)

fig_productivity = px.bar(
    chart_data,
    x="Station",
    y="Productivity",
    title="Productivity by Station",
    text=chart_data["Productivity"].map(lambda x: f"{x:.1f}"),
)

st.plotly_chart(fig_productivity, use_container_width=True)

st.download_button(
    label="Download Station Summary CSV",
    data=csv,
    file_name="station_summary.csv",
    mime="text/csv",
)