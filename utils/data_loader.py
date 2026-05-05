import pandas as pd
from pathlib import Path

DATA_FILE = Path("data/delivery_data.xlsx")

def load_data():
    if not DATA_FILE.exists():
        return None

    df = pd.read_excel(DATA_FILE, sheet_name="Data_Entry", header=3)

    df.columns = [c.strip() for c in df.columns]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Station"] = df["Station"].astype(str).str.strip()
    df["Wave"] = df["Wave"].astype(str).str.strip()

    numeric_cols = [
        "Orders Assigned",
        "Orders Delivered",
        "First Attempt Delivered",
        "RTO Orders",
        "Backlog",
        "Drivers Used",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date", "Station", "Wave"])
    df["Day"] = df["Date"].dt.day_name()

    return df
