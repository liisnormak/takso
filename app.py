import streamlit as st
import pandas as pd
import plotly.express as px

rf_andmed = pd.read_csv("rf_andmed.csv")

filtreeritud = rf_andmed.copy()

prediction_price_type_nimed = {
    "Kõik": None,
    "Ette lubatud hinnaga sõit": "upfront",
    "Sihtkohta muudeti": "upfront_destination_changed",
    "Vahepunktiga sõit": "upfront_waypoint_changed",
    "Prognoositud sõit": "prediction"
}

prediction_price_type_valik = st.sidebar.selectbox(
    "Hinnastamise tüüp",
    options=list(prediction_price_type_nimed.keys())
)

valitud_prediction_type = prediction_price_type_nimed[
    prediction_price_type_valik
]

if valitud_prediction_type is not None:
    filtreeritud = filtreeritud[
        filtreeritud["prediction_price_type"] == valitud_prediction_type
    ]

filtreeritud["distance_difference"] = (
    filtreeritud["distance_km"]
    - filtreeritud["predicted_distance"] / 1000
)

filtreeritud["duration_difference"] = (
    filtreeritud["duration"] - filtreeritud["predicted_duration"]

)

filtreeritud["duration_difference_min"] = (
    filtreeritud["duration_difference"] / 60
)


st.set_page_config(
    page_title="VALI-IT",
    page_icon="🚕",
    layout="wide"
)

st.markdown("""
<style>

.stApp {
    background-color: #81C784;
}

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
        text-align: center;
    }

    .subtitle {
        font-size: 20px;
        color: white;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 30px;
    }

    .chart-title {
    text-align: center;
    font-size: 24px;
    font-weight: 700;
    color: #1B4332;
    margin: 25px 0 15px 0;
}

    .metric-card {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 35px;
    border-radius: 16px;
    text-align: center;
    margin: 10px 0 35px 0;
}

.metric-title {
    font-size: 26px;
    font-weight: 700;
    color: #2E5D3B;
}

.metric-value {
    font-size: 34px;
    font-weight: 800;
    color: #1B4332;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">VALI-IT 🚕</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Taksosõitude hinnastamise ja kaebuste analüüs</div>',
    unsafe_allow_html=True
)

st.divider()

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

st.markdown("""
<div class="metric-card">
    <div class="metric-title">Sõitude arv</div>
    <div class="metric-value">
        {:,}
    </div>
</div>
""".format(len(filtreeritud)).replace(",", " "), unsafe_allow_html=True)

st.markdown(
    '<div class="chart-title">Kaebuste osakaal päeva perioodi ja hinnastamise kategooria järgi</div>',
    unsafe_allow_html=True
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

graafik["päeva_periood"] = graafik["päeva_periood"].replace({
    "hommik": "Hommik",
    "lõuna": "Lõuna",
    "õhtu": "Õhtu",
    "öö": "Öö"
})

graafik["prediction_price_type"] = graafik["prediction_price_type"].replace({
    "upfront": "Ette lubatud sõidu hind",
    "prediction": "Prognoositud sõit",
    "upfront_destination_changed": "Sihtkohta muudeti",
    "upfront_waypoint_changed": "Eelnevalt määratud vahepunkt"
})

graafik["overcharge_pct"] = graafik["overpaid_ride_ticket"] * 100

fig = px.bar(
    graafik,
    x="päeva_periood",
    y="overcharge_pct",
    color="prediction_price_type",
    barmode="group",
    labels={
        "päeva_periood": "Sõidud päeva perioodi võrdluses",
        "overcharge_pct": "Kaebuste osakaal (%)",
        "prediction_price_type": "Hinnastamise kategooria"
    }
)

st.plotly_chart(
    fig,
    width="stretch"
)

st.markdown(
    '<div class="chart-title">Kaebuste osakaal tegeliku sõiduvahemaa järgi</div>',
    unsafe_allow_html=True
)

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
        "overcharge_pct": "Kaebuste osakaal (%)"
    }
)

st.plotly_chart(
    fig_distance,
    width="stretch"
)

distance_diff_graafik = (
    filtreeritud
    .assign(
        distance_difference_grupp=pd.cut(
            filtreeritud["distance_difference"],
            bins=[
                -float("inf"),
                -5,
                -2,
                0,
                2,
                5,
                10,
                float("inf")
            ],
            labels=[
                "Alla −5 km",
                "−5 kuni −2 km",
                "−2 kuni 0 km",
                "0 kuni 2 km",
                "2 kuni 5 km",
                "5 kuni 10 km",
                "Üle 10 km"
            ],
            include_lowest=True
        )
    )
    .groupby(
        "distance_difference_grupp",
        observed=True
    )["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

distance_diff_graafik["overcharge_pct"] = (
    distance_diff_graafik["overpaid_ride_ticket"] * 100
)

st.markdown(
    '<div class="chart-title">Kaebuste osakaal tegeliku ja prognoositud teepikkuse erinevuse järgi</div>',
    unsafe_allow_html=True
)

fig_distance_diff = px.bar(
    distance_diff_graafik,
    x="distance_difference_grupp",
    y="overcharge_pct",
    labels={
        "distance_difference_grupp": "Tegeliku ja prognoositud teepikkuse erinevus",
        "overcharge_pct": "Kaebuste osakaal (%)"
    }
)

st.plotly_chart(
    fig_distance_diff,
    width="stretch"
)

st.markdown(
    '<div class="chart-title">Kaebuste osakaal tegeliku sõiduaja järgi</div>',
    unsafe_allow_html=True
)

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
        "overcharge_pct": "Kaebuste osakaal (%)"
    }
)

st.plotly_chart(
    fig_duration,
    width="stretch"
)
st.markdown(
    '<div class="chart-title">Kaebuste osakaal tegeliku ja prognoositud sõiduaja erinevuse järgi</div>',
    unsafe_allow_html=True
)

duration_diff_graafik = (
    filtreeritud
    .assign(
        duration_difference_grupp=pd.cut(
            filtreeritud["duration_difference_min"],
            bins=[
                -float("inf"),
                -10,
                -5,
                0,
                5,
                10,
                20,
                float("inf")
            ],
            labels=[
                "Alla −10 min",
                "−10 kuni −5 min",
                "−5 kuni 0 min",
                "0 kuni 5 min",
                "5 kuni 10 min",
                "10 kuni 20 min",
                "Üle 20 min"
            ],
            include_lowest=True
        )
    )
    .groupby(
        "duration_difference_grupp",
        observed=True
    )["overpaid_ride_ticket"]
    .mean()
    .reset_index()
)

duration_diff_graafik["overcharge_pct"] = (
    duration_diff_graafik["overpaid_ride_ticket"] * 100
)

fig_duration_diff = px.bar(
    duration_diff_graafik,
    x="duration_difference_grupp",
    y="overcharge_pct",
    labels={
        "duration_difference_grupp": "Tegeliku ja prognoositud sõiduaja erinevus",
        "overcharge_pct": "Kaebuste osakaal (%)"
    }
)

st.plotly_chart(
    fig_duration_diff,
    width="stretch"
)

st.markdown(
    '<div class="chart-title">Sõitja tarkvara versiooni ja päeva perioodi seos kaebustega</div>',
    unsafe_allow_html=True
)

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
        "overcharge_pct": "Kaebuste osakaal (%)",
        "päeva_periood": "Päeva periood"
    }
)

st.plotly_chart(
    fig_rider_paevaperiood,
    width="stretch"
)
st.markdown(
    '<div class="chart-title">Juhi tarkvara versiooni ja päeva perioodi seos kaebustega</div>',
    unsafe_allow_html=True
)

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
        "overcharge_pct": "Kaebuste osakaal (%)",
        "päeva_periood": "Päeva periood"
    }
)

st.plotly_chart(
    fig_driver_paevaperiood,
    width="stretch"
)

st.markdown(
    '<div class="chart-title">Kaebuste osakaal seadme tootja järgi</div>',
    unsafe_allow_html=True
)

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
        "overcharge_pct": "Kaebuste osakaal (%)"
    }
)

st.plotly_chart(
    fig_seade,
    width="stretch"
)