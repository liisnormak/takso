import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

st.set_page_config(
    page_title="VALI-IT",
    page_icon="🚕",
    layout="wide"
)

rf_andmed = pd.read_csv("rf_andmed.csv")

filtreeritud = rf_andmed.copy()

def lähtesta_filtrid():
    st.session_state["teepikkuse_valik"] = "Kõik"
    st.session_state["sõidukestvuse_valik"] = "Kõik"
    st.session_state["gps_valik"] = "Kõik"
    st.session_state["eu_valik"] = "Kõik"
    st.session_state["Nädalapäeva_valik"] = "Kõik"
    st.session_state["hinna_vahemik"] = (
        float(rf_andmed["hinna_muutus_eur"].min()),
        float(rf_andmed["hinna_muutus_eur"].max())
    )

st.markdown("""
<style>

.stApp {
    background-color: #178939;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0;
    text-align: center;
    color: white;
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
    font-size: 26px;
    font-weight: 800;
    color: white;
    margin: 35px 0 15px 0;
}

.metric-card {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 28px;
    border-radius: 16px;
    text-align: center;
    margin: 10px 0 30px 0;
}

.metric-title {
    font-size: 24px;
    font-weight: 800;
    color: #2E5D3B;
}

.metric-value {
    font-size: 34px;
    font-weight: 800;
    color: #1B4332;
    margin-top: 8px;
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
    filtreeritud["duration"]
    - filtreeritud["predicted_duration"]
)

filtreeritud["duration_difference_min"] = (
    filtreeritud["duration_difference"] / 60
)


st.sidebar.header("Filtrid")

teepikkuse_valik = st.sidebar.selectbox(
    "Vahemaa",
    ["Kõik", "0–2 km", "2–5 km", "5–10 km", "10–20 km", "20+ km"],
    key="teepikkuse_valik"
)

sõidukestvuse_valik = st.sidebar.selectbox(
    "Kestus",
    ["Kõik", "0–5 min", "5–10 min", "10–20 min", "20–40 min", "40+ min"],
    key="sõidukestvuse_valik"
)

gps_valik = st.sidebar.selectbox(
    "GPS",
    ["Kõik", "GPS täpne", "GPS ebatäpne"],
    key="gps_valik"
)

eu_valik = st.sidebar.selectbox(
    "EU indicator",
    ["Kõik", "EU = jah", "EU = ei"],
    key="eu_valik"
)

hinna_vahemik = st.sidebar.slider(
    "Hinna muutus (€)",
    float(rf_andmed["hinna_muutus_eur"].min()),
    float(rf_andmed["hinna_muutus_eur"].max()),
    (
        float(rf_andmed["hinna_muutus_eur"].min()),
        float(rf_andmed["hinna_muutus_eur"].max())
    ),
      key="hinna_vahemik"
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
    ],
    key="Nädalapäeva_valik"
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

st.sidebar.button(
    "Lähtesta filtrid",
    on_click=lähtesta_filtrid,
    type="primary"
)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Sõitude arv</div>
        <div class="metric-value">
            {:,}
        </div>
    </div>
    """.format(
        len(filtreeritud)
    ).replace(",", " "), unsafe_allow_html=True)


with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Kaebusega sõite</div>
        <div class="metric-value">
            {:,}
        </div>
    </div>
    """.format(
        filtreeritud["overpaid_ride_ticket"].sum()
    ).replace(",", " "), unsafe_allow_html=True)


with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Kaebuste osakaal</div>
        <div class="metric-value">
            {:.1f}%
        </div>
    </div>
    """.format(
        filtreeritud["overpaid_ride_ticket"].mean() * 100
    ), unsafe_allow_html=True)


with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Keskmine sõiduvahemaa</div>
        <div class="metric-value">
            {:.1f} km
        </div>
    </div>
    """.format(
        filtreeritud["distance"].mean()
    ), unsafe_allow_html=True)

def kujunda_graafik(fig):
    fig.update_xaxes(
        title_text="",
        tickfont=dict(
            size=13,
            family="Arial Black",
            color="black"
        )
    )

    fig.update_yaxes(
        title_text="",
        tickfont=dict(
            size=13,
            family="Arial Black",
            color="black"
        )
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(
            l=60,
            r=30,
            t=20,
            b=50
 ),
        legend=dict(
            font=dict(
                color="black"
            ),
            title_font=dict(
                color="black"
            )
        )
    )
    return fig

st.markdown(
    '<div class="chart-title">Kaebuste osakaal (%) päeva perioodi ja hinnastamistüübi võrdluses</div>',
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

graafik["overcharge_pct"] = (
    graafik["overpaid_ride_ticket"] * 100
)

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

fig = kujunda_graafik(fig)

st.plotly_chart(
    fig,
    width="stretch"
)

st.markdown(
    '<div class="chart-title">Sõitja tarkvara ja päeva perioodi võrdlus kaebuste osakaaluga (%)</div>',
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

charts = []

for tarkvara in rider_paevaperiood["rider_app_group"].unique():

    andmed = rider_paevaperiood[
        rider_paevaperiood["rider_app_group"] == tarkvara
    ]

    chart = (
        alt.Chart(andmed)
        .mark_bar()
        .encode(
            x=alt.X(
                "päeva_periood:N",
                title=None,
                axis=alt.Axis(
                    labels=False,
                    ticks=False
                )
            ),
            y=alt.Y(
                "overcharge_pct:Q",
                title="Kaebuste osakaal (%)"
            ),
            color=alt.Color(
                "päeva_periood:N",
                title="Päeva periood"
            ),
            tooltip=[
                alt.Tooltip(
                    "rider_app_group:N",
                    title="Sõitja tarkvara"
                ),
                alt.Tooltip(
                    "päeva_periood:N",
                    title="Päeva periood"
                ),
                alt.Tooltip(
                    "overcharge_pct:Q",
                    title="Kaebuste osakaal (%)",
                    format=".2f"
                )
            ]
        )
        .properties(
            width=550,
            height=220,
            title=alt.TitleParams(
                text=tarkvara,
                font="Arial Black",
                fontSize=13,
                color="black",
                anchor="middle",
                offset=15
            )
        )
    )

    charts.append(chart)

chart = (
    alt.vconcat(
        alt.hconcat(charts[0], charts[1], spacing=35),
        alt.hconcat(charts[2], charts[3], spacing=35),
        spacing=30
    )
    .configure_view(
        stroke=None
    )
     .configure_axis(
    labelColor="black",
    titleColor="black",
    labelFontWeight="bold",
    titleFontWeight="bold",
    labelFontSize=13,
    titleFontSize=13
)
    .configure_legend(
    labelColor="black",
    titleColor="black",
    labelFontWeight="bold",
    titleFontWeight="bold",
    labelFontSize=13,
    titleFontSize=13
)

    .configure(
        background="white"
    )
)

st.markdown("""
<style>
.vega-embed text {
    font-weight: bold !important;
    fill: black !important;
}
</style>
""", unsafe_allow_html=True)

st.altair_chart(
    chart,
    width="stretch"
)

st.markdown(
    '<div class="chart-title">Juhi tarkvara ja päeva perioodi võrdlus kaebuste osakaaluga (%)</div>',
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

fig_driver_paevaperiood = kujunda_graafik(
    fig_driver_paevaperiood
)

st.plotly_chart(
    fig_driver_paevaperiood,
    width="stretch"
)
st.markdown(
    '<div class="chart-title">Kaebuste osakaal (%) seadme tootja järgi</div>',
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
    seade_overcharge.sort_values("overcharge_pct"),
    x="overcharge_pct",
    y="Koond seadmed",
    orientation="h",
    text="overcharge_pct",
    color="Koond seadmed",
    color_discrete_sequence=[
        "#2E86AB",
        "#F18F01",
        "#6A4C93",
        "#43AA8B",
        "#E76F51",
        "#577590",
        "#90BE6D",
        "#F9C74F",
        "#277DA1"
    ],
    labels={
        "Koond seadmed": "",
        "overcharge_pct": ""
    }
)

fig_seade.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    textfont=dict(
        size=15,
        family="Arial Black",
        color="black"
    )
)

fig_seade.update_layout(
    xaxis=dict(
        showticklabels=False,
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        tickfont=dict(
            size=14,
            family="Arial Black",
            color="black"
        ),
        showgrid=False
    ),
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.plotly_chart(
    fig_seade,
    width="stretch"
)