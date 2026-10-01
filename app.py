import streamlit as st
import pandas as pd
import plotly.express as px

rf_andmed = pd.read_csv("rf_andmed.csv")

filtreeritud = rf_andmed.copy()

rf_andmed["prediction_price_type"] = pd.Categorical(
    rf_andmed["prediction_price_type"],
    categories=[
        "prediction",
        "upfront",
        "upfront_destination_changed",
        "upfront_waypoint_changed"
    ],
    ordered=True
)

rf_andmed.columns.tolist()

st.sidebar.header("Filtrid")

teepikkuse_valik = st.sidebar.selectbox(
    "Vahemaa",
    ["Kõik", "0–2 km", "2–5 km", "5–10 km", "10–20 km", "20+ km"]
)

sõidukestvuse_valik = st.sidebar.selectbox(
    "Kestus",
    ["Kõik", "0–5 min", "5–10 min", "10–20 min", "20–40 min", "40+ min"]
)

gps_valik = st.sidebar.selectbox(
    "GPS",
    ["Kõik", "GPS täpne", "GPS ebatäpne"]
)

eu_valik = st.sidebar.selectbox(
    "EU indicator",
    ["Kõik", "EU = jah", "EU = ei"]
)

hinna_vahemik = st.sidebar.slider(
    "Hinna muutus (€)",
    float(rf_andmed["hinna_muutus_eur"].min()),
    float(rf_andmed["hinna_muutus_eur"].max()),
    (
        float(rf_andmed["hinna_muutus_eur"].min()),
        float(rf_andmed["hinna_muutus_eur"].max())
    )
)

if hinna_vahemik != (
    float(rf_andmed["hinna_muutus_eur"].min()),
    float(rf_andmed["hinna_muutus_eur"].max())
):
    filtreeritud = filtreeritud[
        filtreeritud["hinna_muutus_eur"].between(
            hinna_vahemik[0],
            hinna_vahemik[1]
        )
    ]


if gps_valik == "GPS täpne":
    filtreeritud = filtreeritud[
        filtreeritud["gps_confidence"] == 1
    ]

elif gps_valik == "GPS ebatäpne":
    filtreeritud = filtreeritud[
        filtreeritud["gps_confidence"] == 0
    ]

if eu_valik == "EU = jah":
    filtreeritud = filtreeritud[
        filtreeritud["eu_indicator"] == 1
    ]

elif eu_valik == "EU = ei":
    filtreeritud = filtreeritud[
        filtreeritud["eu_indicator"] == 0
    ]

Nädalapäeva_valik = st.sidebar.selectbox(
    "Nädalapäev",
    [
        "Kõik",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]
)

if Nädalapäeva_valik != "Kõik":
    filtreeritud = filtreeritud[
        filtreeritud["weekday"] == Nädalapäeva_valik
    ]

if teepikkuse_valik == "0–2 km":
    filtreeritud = filtreeritud[
        filtreeritud["distance_km"].between(0, 2)
    ]

elif teepikkuse_valik == "2–5 km":
    filtreeritud = filtreeritud[
        filtreeritud["distance_km"].between(2, 5, inclusive="right")
    ]

elif teepikkuse_valik == "5–10 km":
    filtreeritud = filtreeritud[
        filtreeritud["distance_km"].between(5, 10, inclusive="right")
    ]

elif teepikkuse_valik == "10–20 km":
    filtreeritud = filtreeritud[
        filtreeritud["distance_km"].between(10, 20, inclusive="right")
    ]

elif teepikkuse_valik == "20+ km":
    filtreeritud = filtreeritud[
        filtreeritud["distance_km"] > 20
    ]


if sõidukestvuse_valik == "0–5 min":
    filtreeritud = filtreeritud[
        filtreeritud["duration_min"].between(0, 5)
    ]

elif sõidukestvuse_valik == "5–10 min":
    filtreeritud = filtreeritud[
        filtreeritud["duration_min"].between(5, 10, inclusive="right")
    ]

elif sõidukestvuse_valik == "10–20 min":
    filtreeritud = filtreeritud[
        filtreeritud["duration_min"].between(10, 20, inclusive="right")
    ]

elif sõidukestvuse_valik == "20–40 min":
    filtreeritud = filtreeritud[
        filtreeritud["duration_min"].between(20, 40, inclusive="right")
    ]

elif sõidukestvuse_valik == "40+ min":
    filtreeritud = filtreeritud[
        filtreeritud["duration_min"] > 40
    ]

st.metric(
    "Sõitude arv",
    f"{len(filtreeritud):,}".replace(",", " ")
)

graafik = (
    filtreeritud
    .groupby(
        ["päeva_periood", "prediction_price_type"],
        observed=True
    )["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

graafik["overcharge_pct"] = graafik["overpaid_ride_ticket"] * 100

fig = px.bar(
    graafik,
    x="päeva_periood",
    y="overcharge_pct",
    color="prediction_price_type",
    barmode="group",
    labels={
        "päeva_periood": "Sõidud päeva perioodi võrdluses",
        "overcharge_pct": "Overcharge-ticketite osakaal (%)",
        "prediction_price_type": "Hinnastamise kategooria"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Kaebuste osakaal sõidu vahemaa järgi")

distance_graafik = (
    filtreeritud
    .assign(
        distance_grupp=pd.cut(
            filtreeritud["distance_km"],
            bins=[0, 2, 5, 10, 20, 50, float("inf")],
            labels=[
                "0–2 km",
                "2–5 km",
                "5–10 km",
                "10–20 km",
                "20–50 km",
                "50+ km"
            ],
            include_lowest=True
        )
    )
    .groupby("distance_grupp", observed=True)["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

distance_graafik["overcharge_pct"] = (
    distance_graafik["overpaid_ride_ticket"] * 100
)

fig_distance = px.bar(
    distance_graafik,
    x="distance_grupp",
    y="overcharge_pct",
    labels={
        "distance_grupp": "Sõidu vahemaa",
        "overcharge_pct": "Kaebusega piletite osakaal (%)"
    }
)

st.plotly_chart(
    fig_distance,
    use_container_width=True
)


st.subheader("Kaebuste osakaal sõidu kestuse järgi")

duration_graafik = (
    filtreeritud
    .assign(
        duration_grupp=pd.cut(
            filtreeritud["duration_min"],
            bins=[0, 5, 10, 20, 40, 60, float("inf")],
            labels=[
                "0–5 min",
                "5–10 min",
                "10–20 min",
                "20–40 min",
                "40–60 min",
                "60+ min"
            ],
            include_lowest=True
        )
    )
    .groupby("duration_grupp", observed=True)["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

duration_graafik["overcharge_pct"] = (
    duration_graafik["overpaid_ride_ticket"] * 100
)

fig_duration = px.bar(
    duration_graafik,
    x="duration_grupp",
    y="overcharge_pct",
    labels={
        "duration_grupp": "Sõidu kestus",
        "overcharge_pct": "Kaebusega piletite osakaal (%)"
    }
)

st.plotly_chart(
    fig_duration,
    use_container_width=True
)

st.subheader("Sõitja tarkvara versiooni ja päeva perioodi seos kaebustega")

rider_paevaperiood = (
    filtreeritud
    .groupby(
        ["rider_app_group", "päeva_periood"]
    )["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

rider_paevaperiood["overcharge_pct"] = (
    rider_paevaperiood["overpaid_ride_ticket"] * 100
)

fig_rider_paevaperiood = px.bar(
    rider_paevaperiood,
    x="rider_app_group",
    y="overcharge_pct",
    color="päeva_periood",
    barmode="group",
    labels={
        "rider_app_group": "Sõitja tarkvara",
        "overcharge_pct": "Kaebusega piletite osakaal (%)",
        "päeva_periood": "Päeva periood"
    }
)

st.plotly_chart(
    fig_rider_paevaperiood,
    use_container_width=True
)
st.subheader("Juhi tarkvara versiooni ja päeva perioodi seos kaebustega")

driver_paevaperiood = (
    filtreeritud
    .groupby(
        ["driver_app_group", "päeva_periood"]
    )["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

driver_paevaperiood["overcharge_pct"] = (
    driver_paevaperiood["overpaid_ride_ticket"] * 100
)

fig_driver_paevaperiood = px.bar(
    driver_paevaperiood,
    x="driver_app_group",
    y="overcharge_pct",
    color="päeva_periood",
    barmode="group",
    labels={
        "driver_app_group": "Juhi tarkvara",
        "overcharge_pct": "Kaebusega piletite osakaal (%)",
        "päeva_periood": "Päeva periood"
    }
)

st.plotly_chart(
    fig_driver_paevaperiood,
    use_container_width=True
)

st.subheader("Kaebuste osakaal seadme tootja järgi")

seade_overcharge = (
    filtreeritud
    .groupby("Koond seadmed")["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

seade_overcharge["overcharge_pct"] = (
    seade_overcharge["overpaid_ride_ticket"] * 100
)

fig_seade = px.bar(
    seade_overcharge,
    x="Koond seadmed",
    y="overcharge_pct",
    labels={
        "Koond seadmed": "Seadme tootja",
        "overcharge_pct": "Kaebusega piletite osakaal (%)"
    }
)

st.plotly_chart(
    fig_seade,
    use_container_width=True
)