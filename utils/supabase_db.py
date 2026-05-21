import streamlit as st
import pandas as pd
from supabase import create_client


@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def insert_delivery_record(record):
    supabase = get_supabase_client()

    response = (
        supabase
        .table("delivery_data")
        .upsert(
            record,
            on_conflict="delivery_date,station,wave"
        )
        .execute()
    )

    return response


def fetch_delivery_data():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("delivery_data")
        .select("*")
        .order("delivery_date")
        .execute()
    )

    data = response.data

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    df["delivery_date"] = pd.to_datetime(df["delivery_date"])
    df["Day"] = df["delivery_date"].dt.day_name()

    df = df.rename(columns={
        "delivery_date": "Date",
        "station": "Station",
        "wave": "Wave",
        "orders_assigned": "Orders Assigned",
        "orders_delivered": "Orders Delivered",
        "first_attempt_delivered": "First Attempt Delivered",
        "rto_orders": "RTO Orders",
        "backlog": "Backlog",
        "drivers_used": "Drivers Used",
    })

    return df