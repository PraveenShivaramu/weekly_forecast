import streamlit as st
from datetime import date
from utils.supabase_db import insert_delivery_record

st.title("📝 Station Daily Data Entry")

st.write("Station managers can enter daily station and wave data here.")

stations = [
    "Cologne",
    "Dortmund",
    "Dusseldorf",
    "Essen",
    "Bochum",
    "Duisburg",
    "Leverkusen",
    "Bielefeld",
    "Aachen",
    "Munster",
    "Frankfurt",
    "Hamburg",
    "Berlin",
    "Wuppertal",
    "Gelsenkirchen",
]

waves = ["Morning", "Afternoon"]

with st.form("delivery_entry_form"):

    col1, col2, col3 = st.columns(3)

    delivery_date = col1.date_input("Date", value=date.today())
    station = col2.selectbox("Station", stations)
    wave = col3.selectbox("Wave", waves)

    col4, col5, col6 = st.columns(3)

    orders_assigned = col4.number_input("Orders Assigned", min_value=0, step=1)
    orders_delivered = col5.number_input("Orders Delivered", min_value=0, step=1)
    first_attempt_delivered = col6.number_input("First Attempt Delivered", min_value=0, step=1)

    col7, col8, col9 = st.columns(3)

    rto_orders = col7.number_input("RTO Orders", min_value=0, step=1)
    backlog = col8.number_input("Backlog", min_value=0, step=1)
    drivers_used = col9.number_input("Drivers Used", min_value=0, step=1)

    submitted = st.form_submit_button("Submit Data")

if submitted:

    if orders_delivered > orders_assigned:
        st.error("Orders Delivered cannot be greater than Orders Assigned.")

    elif first_attempt_delivered > orders_delivered:
        st.error("First Attempt Delivered cannot be greater than Orders Delivered.")

    elif rto_orders > orders_assigned:
        st.error("RTO Orders cannot be greater than Orders Assigned.")

    else:
        record = {
            "delivery_date": str(delivery_date),
            "station": station,
            "wave": wave,
            "orders_assigned": int(orders_assigned),
            "orders_delivered": int(orders_delivered),
            "first_attempt_delivered": int(first_attempt_delivered),
            "rto_orders": int(rto_orders),
            "backlog": int(backlog),
            "drivers_used": int(drivers_used),
        }

        try:
            insert_delivery_record(record)
            st.success("Data saved successfully.")

            st.info(
                "If the same Date + Station + Wave already existed, it was updated."
            )

        except Exception as e:
            st.error("Data was not saved.")
            st.exception(e)