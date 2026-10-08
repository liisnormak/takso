import streamlit as st
import pandas as pd
import numpy as np

st.title("Andmepuhastus")

# Andmete laadimine
bolt_andmed = pd.read_csv("rf_andmed.csv")

st.markdown("""
<style>
.stApp {
    background-color: white;
    color: black;
}

.stApp * {
    color: black;
}

[data-testid="stMarkdownContainer"] h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.subheader("1. Põhiandmestiku viimine sõidu tasemele")

order_andmed = (
    bolt_andmed
    .groupby("order_id_new", as_index=False)
    .agg({
        "calc_created": "first",
        "order_try_id_new": "first",
        "metered_price": "first",
        "upfront_price": "first",
        "distance": "first",
        "duration": "first",
        "gps_confidence": "first",
        "entered_by": "first",
        "b_state": "first",
        "dest_change_number": "first",
        "prediction_price_type": "first",
        "predicted_distance": "first",
        "predicted_duration": "first",
        "change_reason_pricing": "first",
        "ticket_id_new": "first",
        "rider_app_version": "first",
        "order_state": "first",
        "order_try_state": "first",
        "driver_app_version": "first",
        "driver_device_uid_new": "first",
        "device_name": "first",
        "eu_indicator": "first",
        "overpaid_ride_ticket": "max",
        "fraud_score": "first",
        "date": "first",
        "time": "first",
        "day_of_week": "first",
        "day_of_week_nr": "first",
        "month": "first",
        "year": "first",
        "is_invalid_ride": "first",
        "fraud_score_status": "first",
        "overcharge_status": "first"
    })
)

st.write(f"Algselt: {len(bolt_andmed)} piletirida")
st.write(f"Pärast sõitude tasemele viimist: {len(order_andmed)} sõitu")


st.subheader("2. Puuduvate fraud_score väärtuste käsitlemine")

order_andmed["fraud_score"] = order_andmed["fraud_score"].fillna(0)


st.subheader("3. Aja määratlemine")

order_andmed["hour"] = pd.to_datetime(
    order_andmed["time"],
    format="%H:%M:%S"
).dt.hour

order_andmed["päeva_periood"] = pd.cut(
    order_andmed["calc_created"].pipe(pd.to_datetime).dt.hour,
    bins=[-1, 6, 12, 18, 24],
    labels=["öö", "hommik", "lõuna", "õhtu"]
)


st.subheader("4. Mõõtühikute teisendamine")

# Vahemaad meetritest kilomeetriteks
order_andmed["distance_km"] = order_andmed["distance"] / 1000
order_andmed["predicted_distance_km"] = (
    order_andmed["predicted_distance"] / 1000
)

# Kestused sekunditest minutiteks
order_andmed["duration_min"] = order_andmed["duration"] / 60
order_andmed["predicted_duration_min"] = (
    order_andmed["predicted_duration"] / 60
)

# Hinnad sentidest eurodeks
order_andmed["metered_price_eur"] = (
    order_andmed["metered_price"] / 100
)
order_andmed["upfront_price_eur"] = (
    order_andmed["upfront_price"] / 100
)


st.subheader("5. Hinna muutuse arvutamine")

order_andmed["hinna_muutus"] = (
    order_andmed["metered_price"] -
    order_andmed["upfront_price"]
)

order_andmed["hinna_muutus_eur"] = (
    order_andmed["metered_price_eur"] -
    order_andmed["upfront_price_eur"]
)


st.subheader("6. Arvutusliku kiiruse kontroll")

order_andmed["speed_kmh"] = np.where(
    order_andmed["duration"] > 0,
    order_andmed["distance"] /
    order_andmed["duration"] * 3.6,
    np.nan
)

order_andmed["kiiruse_anomaalia"] = (
    order_andmed["speed_kmh"] >= 150
)

kiiruse_anomaaliad = order_andmed[
    order_andmed["kiiruse_anomaalia"]
]

st.write(
    f"Kontrolli käigus tuvastati {len(kiiruse_anomaaliad)} "
    "ebatavaliselt kõrge arvutusliku kiirusega sõitu."
)


st.subheader("Puhastatud andmestik")

st.write(
    "Algandmeid ei kustutatud ega muudetud algses tähenduses. "
    "Analüüsi jaoks teisendati mõõtühikuid ning arvutati "
    "täiendavaid tunnuseid."
)

st.dataframe(order_andmed)

st.subheader("7. Analüütilise valimi määratlemine")

analüüs = order_andmed[
    (order_andmed["predicted_distance"] > 0) &
    (order_andmed["predicted_duration"] > 0) &
    (order_andmed["distance"] > 0) &
    (order_andmed["duration"] > 0)
].copy()

st.write(
    f"Analüüsi kaasati {len(analüüs)} sõitu, "
    "mille tegelik ja prognoositud vahemaa ning sõiduaeg olid suuremad kui 0."
)