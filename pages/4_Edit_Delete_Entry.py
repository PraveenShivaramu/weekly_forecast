import streamlit as st
from datetime import date
from utils.supabase_db import (
    get_delivery_record,
    update_delivery_record,
    delete_delivery_record,
)

st.title("✏️ Edit / Delete Entry")

st.write("Use this page to correct or delete wrong station entries.")

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

st.subheader("Find Existing Entry")

col1, col2, col3 = st.columns(3)

selected_date = col1.date_input("Date", value=date.today())
station = col2.selectbox("Station", stations)
wave = col3.selectbox("Wave", waves)

if st.button("Find Entry"):
    record = get_delivery_record(selected_date, station, wave)

    if record is None:
        st.warning("No entry found for this Date + Station + Wave.")
    else:
        st.session_state["edit_record"] = record
        st.success("Entry found. You can edit or delete it below.")

if "edit_record" in st.session_state:
    record = st.session_state["edit_record"]

    st.subheader("Edit Entry")

    with st.form("edit_entry_form"):
        col4, col5, col6 = st.columns(3)

        orders_assigned = col4.number_input(
            "Orders Assigned",
            min_value=0,
            step=1,
            value=int(record["orders_assigned"]),
        )

        orders_delivered = col5.number_input(
            "Orders Delivered",
            min_value=0,
            step=1,
            value=int(record["orders_delivered"]),
        )

        first_attempt_delivered = col6.number_input(
            "First Attempt Delivered",
            min_value=0,
            step=1,
            value=int(record["first_attempt_delivered"]),
        )

        col7, col8, col9 = st.columns(3)

        rto_orders = col7.number_input(
            "RTO Orders",
            min_value=0,
            step=1,
            value=int(record["rto_orders"]),
        )

        backlog = col8.number_input(
            "Backlog",
            min_value=0,
            step=1,
            value=int(record["backlog"]),
        )

        drivers_used = col9.number_input(
            "Drivers Used",
            min_value=0,
            step=1,
            value=int(record["drivers_used"]),
        )

        update_btn = st.form_submit_button("Update Entry")

    if update_btn:
        if orders_delivered > orders_assigned:
            st.error("Orders Delivered cannot be greater than Orders Assigned.")
        elif first_attempt_delivered > orders_delivered:
            st.error("First Attempt Delivered cannot be greater than Orders Delivered.")
        elif rto_orders > orders_assigned:
            st.error("RTO Orders cannot be greater than Orders Assigned.")
        else:
            updated_record = {
                "orders_assigned": int(orders_assigned),
                "orders_delivered": int(orders_delivered),
                "first_attempt_delivered": int(first_attempt_delivered),
                "rto_orders": int(rto_orders),
                "backlog": int(backlog),
                "drivers_used": int(drivers_used),
            }

            update_delivery_record(record["id"], updated_record)
            st.success("Entry updated successfully.")
            del st.session_state["edit_record"]

    st.divider()
    st.subheader("Delete Entry")

    st.warning("Deleting is permanent. Use carefully.")

    confirm_delete = st.checkbox("I confirm I want to delete this entry")

    if confirm_delete:
        if st.button("Delete Entry"):
            delete_delivery_record(record["id"])
            st.success("Entry deleted successfully.")
            del st.session_state["edit_record"]