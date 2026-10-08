import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

st.set_page_config(
    page_title="Andmed",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>

.stApp {
    background-color: white;
}

[data-testid="stAppViewContainer"] {
    background-color: white;
}

[data-testid="stHeader"] {
    background-color: white;
}

[data-testid="stMarkdownContainer"] h1 {
    color: black;
    font-size: 42px;
    font-weight: 800;
}

[data-testid="stMarkdownContainer"] h2 {
    color: black;
    font-size: 32px;
}

[data-testid="stMarkdownContainer"] h3 {
    color: black;
    font-size: 26px;
    font-weight: 800;
    text-align: center;
    margin-top: 35px;
    margin-bottom: 15px;
}

[data-testid="stMetric"] {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #dddddd;
}

[data-testid="stMetricLabel"] {
    font-size: 18px;
    font-weight: 700;
    color: black;
}

[data-testid="stMetricValue"] {
    font-size: 32px;
    font-weight: 800;
    color: black;
}

[data-testid="stSidebar"] {
    background-color: #262730;
}

[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p {
    color: white !important;
}

[data-testid="stSidebar"] label {
    color: white;
    font-weight: 700;
    font-size: 16px;
}

[data-testid="stExpander"] summary {
    color: black !important;
}

[data-testid="stExpander"] summary p {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

rf_andmed = pd.read_csv("rf_andmed.csv")

filtreeritud = rf_andmed.copy()

analüüs = filtreeritud[
    (filtreeritud["predicted_distance"] > 0) &
    (filtreeritud["predicted_duration"] > 0) &
    (filtreeritud["distance"] > 0) &
    (filtreeritud["duration"] > 0)
].copy()

def lähtesta_filtrid():
    st.session_state["hinnastamise_tüüp"] = "Kõik"
    st.session_state["gps"] = "Kõik"
    st.session_state["eu"] = "Kõik"
    st.session_state["nädalapäev"] = "Kõik"

with st.sidebar:

    st.markdown(
    '<div style="font-size: 26px; font-weight: 900; color: white; margin-bottom: 20px;">🛠️ Filtrid</div>',
    unsafe_allow_html=True
)

    hinnastamise_tüüp = st.selectbox(
        "Hinnastamise tüüp",
        [
            "Kõik",
            "Ette lubatud hinnaga sõit",
            "Sihtkohta muudeti",
            "Vahepunktiga sõit",
            "Prognoositud sõit"
        ],
    key="hinnastamise_tüüp"
)

    gps = st.selectbox(
        "GPS-i täpsus",
        ["Kõik", "Täpne", "Ebatäpne"],
     key="gps"
)

    eu = st.selectbox(
        "EL-i näitaja",
        ["Kõik", "Jah", "Ei"],
    key="eu"
)

    nädalapäev = st.selectbox(
        "Nädalapäev",
        ["Kõik"] + sorted(rf_andmed["weekday"].dropna().unique().tolist()),
        key="nädalapäev"
    )

    st.button(
        "Lähtesta filtrid",
        on_click=lähtesta_filtrid,
        type="primary"
    )


# Filtreerimine

hinnastamise_tüüp_väärtus = {
    "Ette lubatud hinnaga sõit": "upfront",
    "Sihtkohta muudeti": "upfront_destination_changed",
    "Vahepunktiga sõit": "upfront_waypoint_changed",
    "Prognoositud sõit": "prediction"
}

if hinnastamise_tüüp != "Kõik":
    filtreeritud = filtreeritud[
        filtreeritud["prediction_price_type"]
        == hinnastamise_tüüp_väärtus[hinnastamise_tüüp]
    ]

if gps != "Kõik":
    gps_väärtus = {
        "Täpne": 1,
        "Ebatäpne": 0
    }

    filtreeritud = filtreeritud[
        filtreeritud["gps_confidence"] == gps_väärtus[gps]
    ]

if eu != "Kõik":
    eu_väärtus = {
        "Jah": 1,
        "Ei": 0
    }

    filtreeritud = filtreeritud[
        filtreeritud["eu_indicator"] == eu_väärtus[eu]
    ]

if nädalapäev != "Kõik":
    filtreeritud = filtreeritud[
        filtreeritud["weekday"] == nädalapäev
    ]

analüüs = filtreeritud[
    (filtreeritud["predicted_distance"] > 0) &
    (filtreeritud["predicted_duration"] > 0) &
    (filtreeritud["distance"] > 0) &
    (filtreeritud["duration"] > 0)
].copy()

st.title("Andmed")

st.download_button(
    label="Lae filtreeritud andmed alla",
    data=filtreeritud.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtreeritud_andmed.csv",
    mime="text/csv"
)

with st.expander("Vaata filtreeritud andmeid"):
    st.dataframe(
        filtreeritud,
        width="stretch",
        hide_index=True
    )

st.write(
    f"Andmestikus on **{len(rf_andmed)} sõitu** ja "
    f"**{len(rf_andmed.columns)} tunnust**."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Sõitude arv",
        len(filtreeritud)
    )

with col2:
    st.metric(
        "Tunnuste arv",
        len(filtreeritud.columns)
    )

with col3:
    st.metric(
        "Puuduvad väärtused",
        int(filtreeritud.isna().sum().sum())
    )

veerud = st.multiselect(
    "Vali tabelis kuvatavad tunnused",
    rf_andmed.columns.tolist(),
     default=[
        "order_id_new",
        "metered_price",
        "upfront_price",
        "distance_km",
        "duration_min",
        "prediction_price_type",
        "overpaid_ride_ticket"
    ]
)

st.subheader("Overcharge rate (%) by actual ride distance")

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

    .groupby(
        "distance_grupp",
        observed=True
    )

    .agg(
        overcharge_pct=("overpaid_ride_ticket", "mean"),
        sõitude_arv=("order_id_new", "nunique")
    )

    .reset_index()

)

distance_graafik["overcharge_pct"] = (
    distance_graafik["overcharge_pct"] * 100
)

fig_distance = px.bar(
    distance_graafik,
    x="distance_grupp",
    y="overcharge_pct",
    labels={
        "distance_grupp": "Actual distance (km)",
        "overcharge_pct": "Overcharge rate (%)"
    }
)

fig_distance.update_xaxes(
    title_text="Actual distance (km)",
    title_font=dict(
        size=14,
        family="Arial Black",
        color="black"
    ),
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )
)

fig_distance.update_yaxes(
    title_text="Overcharge rate (%)",
    title_font=dict(
        size=14,
        family="Arial Black",
        color="black"
    ),
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )
)

fig_distance.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(
        l=70,
        r=30,
        t=20,
        b=60
    )
)

fig_distance.update_xaxes(
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )
)

fig_distance.update_yaxes(
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )
)

distance_graafik["tekst"] = (
    distance_graafik["overcharge_pct"].map(lambda x: f"{x:.1f}%".replace(".", ","))
    + "<br>"
    + distance_graafik["sõitude_arv"].map(lambda x: f"{x:,}".replace(",", " ") + " Rides")
)

fig_distance = px.bar(

    distance_graafik,

    x="distance_grupp",

    y="overcharge_pct",

    text="tekst",

    labels={

        "distance_grupp": "Actual distance (km)",

        "overcharge_pct": "Overcharge rate (%)"

    }

)

fig_distance.update_xaxes(
    title_text="Actual distance (km)",
    title_font=dict(
        size=14,
        family="Arial Black",
        color="black"
    ),
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )
)

fig_distance.update_yaxes(
    title_text="Overcharge rate (%)",
    title_font=dict(
        size=14,
        family="Arial Black",
        color="black"
    ),
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )
)

fig_distance.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(
        l=70,
        r=30,
        t=20,
        b=60
    )
)

fig_distance.update_xaxes(
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )
)

fig_distance.update_yaxes(
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    )

)

fig_distance.update_traces(

    textposition="outside",

    textfont=dict(

        size=13,

        family="Arial Black",

        color="black"

    )

)

st.plotly_chart(
    fig_distance,
    width="stretch"
)
st.subheader("Actual vs Predicted distance (y=x)")

distance_scatter =  analüüs[
    [
        "predicted_distance_km",
        "distance_km",
        "overpaid_ride_ticket"
    ]
].dropna()

alla_yx_distance = (
    distance_scatter["distance_km"]
    < distance_scatter["predicted_distance_km"]
).sum()

ule_yx_distance = (
    distance_scatter["distance_km"]
    > distance_scatter["predicted_distance_km"]
).sum()

peal_yx_distance = (
    distance_scatter["distance_km"]
    == distance_scatter["predicted_distance_km"]
).sum()


distance_scatter["Overcharged"] = distance_scatter["overpaid_ride_ticket"].map({
    0: "No",
    1: "Yes"
})

fig_distance_scatter = px.scatter(

    distance_scatter,

    x="predicted_distance_km",

    y="distance_km",

    color="Overcharged",

    labels={

        "predicted_distance_km": "Predicted distance (km)",

        "distance_km": "Actual distance (km)",

        "Overcharged": "Overcharged"

    },

    color_discrete_map={

        "No": "blue",

        "Yes": "red"

    },

    opacity=0.5

)

max_distance = max(
    distance_scatter["predicted_distance_km"].max(),
    distance_scatter["distance_km"].max()
)

regressioon_distance = LinearRegression()

regressioon_distance.fit(
    distance_scatter[["predicted_distance_km"]],
    distance_scatter["distance_km"]
)

regressiooni_kalle_distance = regressioon_distance.coef_[0]
regressiooni_vabaliige_distance = regressioon_distance.intercept_

r2_distance = regressioon_distance.score(
    distance_scatter[["predicted_distance_km"]],
    distance_scatter["distance_km"]
)

y_regressioon = (

    regressiooni_kalle_distance * distance_scatter["predicted_distance_km"]

    + regressiooni_vabaliige_distance   

)

fig_distance_scatter.add_trace(

    go.Scatter(

        x=distance_scatter["predicted_distance_km"],

        y=y_regressioon,

        mode="lines",

        name="Regression line",

        line=dict(

            color="red"

        )

    )

)

fig_distance_scatter.add_shape(
    type="line",
    x0=0,
    y0=0,
    x1=max_distance,
    y1=max_distance,
    line=dict(
        dash="dash",
        color="black"
    )
)

fig_distance_scatter.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(
        l=70,
        r=30,
        t=20,
        b=60
    ),
)

fig_distance_scatter.update_xaxes(
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    ),
    title_font=dict(
        size=14,
        family="Arial Black",
        color="black"
    )
)

fig_distance_scatter.update_yaxes(
    tickfont=dict(
        size=13,
        family="Arial Black",
        color="black"
    ),
    title_font=dict(
        size=14,
        family="Arial Black",
        color="black"
    )
)

fig_distance_scatter.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
     legend=dict(
        title_font=dict(
            color="black"
        ),
        font=dict(
            color="black"
        )
    )
)

fig_distance_scatter.add_annotation(
    x=0.05,
    y=0.95,
    xref="paper",
    yref="paper",
    text=(
        f"R² = {r2_distance:.2f}<br>"
        f"Alla y=x: {alla_yx_distance}<br>"
        f"y=x peal: {peal_yx_distance}<br>"
        f"Üle y=x: {ule_yx_distance}"
    ),
    showarrow=False,
    align="left",
    font=dict(
        color="black",
        size=14
    )
)

st.plotly_chart(
    fig_distance_scatter,
    width="stretch"
)

st.subheader("Overcharge rate (%) by actual ride duration")

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

    .groupby(

        "duration_grupp",

        observed=True

    )

    .agg(

        overcharge_pct=("overpaid_ride_ticket", "mean"),

        sõitude_arv=("order_id_new", "nunique")

    )

    .reset_index()

)

duration_graafik["overcharge_pct"] = (

    duration_graafik["overcharge_pct"] * 100

)

duration_graafik["tekst"] = (

    duration_graafik["overcharge_pct"]

    .map(lambda x: f"{x:.1f}%".replace(".", ","))

    + "<br>"

    + duration_graafik["sõitude_arv"]

    .map(lambda x: f"{x:,}".replace(",", " ") + " Rides")

)

fig_duration = px.bar(

    duration_graafik,

    x="duration_grupp",

    y="overcharge_pct",

    text="tekst",

    labels={

        "duration_grupp": "Actual ride duration (min)",

        "overcharge_pct": "Overcharge rate (%)"

    }

)

fig_duration.update_layout(

    plot_bgcolor="white",

    paper_bgcolor="white",

    margin=dict(

        l=70,

        r=30,

        t=20,

        b=60

    )

)

fig_duration.update_xaxes(

    title_text="Actual ride duration (min)",

    title_font=dict(

        size=14,

        family="Arial Black",

        color="black"

    ),

    tickfont=dict(

        size=13,

        family="Arial Black",

        color="black"

    )

)

fig_duration.update_yaxes(

    title_text="Overcharge rate (%)",

    title_font=dict(

        size=14,

        family="Arial Black",

        color="black"

    ),

    tickfont=dict(

        size=13,

        family="Arial Black",

        color="black"

    )

)

fig_duration.update_traces(

    textposition="outside",

    textfont=dict(

        size=13,

        family="Arial Black",

        color="black"

    )

)

st.plotly_chart(

    fig_duration,

    width="stretch"

)


st.subheader("Actual vs Predicted ride duration (y=x)")

duration_scatter = analüüs[
    [
        "predicted_duration_min",
        "duration_min",
        "overpaid_ride_ticket"
    ]
].dropna()

alla_yx_duration = (
    duration_scatter["duration_min"]
    < duration_scatter["predicted_duration_min"]
).sum()

ule_yx_duration = (
    duration_scatter["duration_min"]
    > duration_scatter["predicted_duration_min"]
).sum()

peal_yx_duration = (
    duration_scatter["duration_min"]
    == duration_scatter["predicted_duration_min"]
).sum()

duration_scatter["Overcharged"] = duration_scatter["overpaid_ride_ticket"].map({
    0: "No",
    1: "Yes"
})

fig_duration_scatter = px.scatter(

    duration_scatter,

    x="predicted_duration_min",

    y="duration_min",

    color="Overcharged",

    labels={

        "predicted_duration_min": "Predicted duration (min)",

        "duration_min": "Actual duration (min)",

        "Overcharged": "Overcharged"

    },

    color_discrete_map={

        "No": "blue",

        "Yes": "red"

    },

    opacity=0.5

)

max_duration = max(

    duration_scatter["predicted_duration_min"].max(),

    duration_scatter["duration_min"].max()

)

regressioon = LinearRegression()

regressioon.fit(

    duration_scatter[["predicted_duration_min"]],

    duration_scatter["duration_min"]

)

regressiooni_kalle_duration = regressioon.coef_[0]

regressiooni_vabaliige_duration = regressioon.intercept_

r2_duration = regressioon.score(
    duration_scatter[["predicted_duration_min"]],
    duration_scatter["duration_min"]
)

y_regressioon = (

    regressiooni_kalle_duration * duration_scatter["predicted_duration_min"]

    + regressiooni_vabaliige_duration

)

fig_duration_scatter.add_trace(

    go.Scatter(

        x=duration_scatter["predicted_duration_min"],

        y=y_regressioon,

        mode="lines",

        name="Regression line",

        line=dict(

            color="red"

        )

    )

)

fig_duration_scatter.add_shape(

    type="line",

    x0=0,

    y0=0,

    x1=max_duration,

    y1=max_duration,

    line=dict(

        dash="dash",

        color="black"

    )

)

fig_duration_scatter.update_xaxes(

    tickfont=dict(

        size=13,

        family="Arial Black",

        color="black"

    ),

    title_font=dict(

        size=14,

        family="Arial Black",

        color="black"

    )

)

fig_duration_scatter.update_yaxes(

    tickfont=dict(

        size=13,

        family="Arial Black",

        color="black"

    ),

    title_font=dict(

        size=14,

        family="Arial Black",

        color="black"

    )

)

fig_duration_scatter.update_layout(

    plot_bgcolor="white",

    paper_bgcolor="white",

    margin=dict(

        l=70,

        r=30,

        t=20,

        b=60

    ),

    legend=dict(

        title_font=dict(

            color="black"

        ),

        font=dict(

            color="black"

        )

    )

)

fig_duration_scatter.add_annotation(
    x=0.05,
    y=0.95,
    xref="paper",
    yref="paper",
    text=(
        f"R² = {r2_duration:.2f}<br>"
        f"Alla y=x: {alla_yx_duration}<br>"
        f"y=x peal: {peal_yx_duration}<br>"
        f"Üle y=x: {ule_yx_duration}"
    ),
    showarrow=False,
    align="left",
    font=dict(
        color="black",
        size=14
    )
)

st.plotly_chart(

    fig_duration_scatter,

    width="stretch"

)



st.markdown("---")

st.subheader("Visuaalide seletus")

st.markdown("""
<div style="color: black;">

- <b>y = x</b> – ideaalne võrdlusjoon, mis tähistab olukorda, kus prognoositud ja tegelik väärtus on võrdsed. Joont kasutatakse prognoositud ja tegeliku väärtuse võrdlemiseks.
- <b>Regressioonijoon</b> – joon, mis kirjeldab prognoositud ja tegeliku väärtuse vahelist lineaarset seost kogu analüüsivalimis.
- <b>R²</b> – lineaarse seose tugevuse mõõdik, mis näitab, kui suure osa tegeliku väärtuse varieeruvusest kirjeldab lineaarne seos prognoositud väärtusega. R² ei näita prognoosi täpsust protsendina.
- <b>Total rides</b> – analüüsis kasutatud sõitude koguarv.
- <b>Alla y=x</b> – tegelik väärtus oli prognoositust väiksem.
- <b>y=x peal</b> – tegelik ja prognoositud väärtus olid võrdsed.
- <b>Üle y=x</b> – tegelik väärtus oli prognoositust suurem.

</div>
""", unsafe_allow_html=True)


st.subheader("Distance vs Duration regressioonide võrdlus")

st.markdown("""
<div style="color: black;">

<b>Kuidas tulemusi lugeda?</b><br>

Regressioonijoone ideaalne kalle on <b>1.0</b>, mis vastab ideaaljoonele <b>y = x</b>.
Mida lähemal on regressioonijoone kalle väärtusele 1.0, seda lähemal on prognoositud
ja tegeliku väärtuse lineaarne muutumissuhe ideaalile. Samas tuleb regressioonijoont
tõlgendada koos R²-ga, sest kalle üksi ei näita seose tugevust.

</div>
""", unsafe_allow_html=True)


erinevus_distance = regressiooni_kalle_distance - 1
erinevus_duration = regressiooni_kalle_duration - 1


st.markdown(f"""
<div style="color: black;">

<b>Distance</b><br>
Regressioonijoone kalle = {regressiooni_kalle_distance:.3f}<br>
Vabaliige = {regressiooni_vabaliige_distance:.3f}<br>
R² = {r2_distance:.2f}<br>
Kalde erinevus y=x-st = {erinevus_distance:.3f}

<br><br>

<b>Duration</b><br>
Regressioonijoone kalle = {regressiooni_kalle_duration:.3f}<br>
Vabaliige = {regressiooni_vabaliige_duration:.3f}<br>
R² = {r2_duration:.2f}<br>
Kalde erinevus y=x-st = {erinevus_duration:.3f}

</div>
""", unsafe_allow_html=True)


st.markdown("---")

st.subheader("Järeldav kokkuvõte")

st.markdown("""
<div style="color: black;">

- <b>Distance / Kõik sõidud</b> – prognoositud ja tegeliku distantsi vahel esineb lineaarne seos (R² = 0,38). Regressioonijoone kalle 0,594 erineb märgatavalt ideaaljoone kaldest 1,0, mis näitab, et prognoositud ja tegeliku distantsi lineaarne suhe ei vasta kogu vahemikus 1:1 suhtele.

- <b>Duration / Kõik sõidud</b> – prognoositud sõidu kestuse ja tegeliku kestuse vaheline lineaarne seos on distantsi omast nõrgem (R² = 0,26). Samas on regressioonijoone kalle 0,999 ehk praktiliselt 1,0. See tähendab, et prognoositud ja tegeliku kestuse lineaarne muutumissuhe on ideaaljoonele väga lähedal, kuid üksikute sõitude väärtused on tugevalt hajunud.

- <b>Distance vs Duration</b> – distantsi puhul on prognoositud ja tegeliku väärtuse vaheline lineaarne seos tugevam, kuid regressioonijoone kalle erineb ideaalväärtusest rohkem. Kestuse puhul on regressioonikalle peaaegu ideaalne, kuid väiksem R² näitab, et üksikute sõitude vahel esineb rohkem hajuvust.

- <b>Prediction grupp / Duration</b> – 75,4% sõitudest oli tegelik kestus prognoositust pikem. See näitab, et tegelik kestus kaldus selles grupis sageli prognoosist ülespoole.

- <b>Prediction grupp / Distance</b> – 49,4% sõitudest oli tegelik distants prognoositust pikem, 37,3% lühem ja 15,0% täpselt prognoosiga võrdne.

- <b>Kaebuste osakaal</b> – ainuüksi prognoositust pikemaks kujunenud sõit ei näi seletavat kõrget kaebuste osakaalu. Upfront-grupis kujunes tegelik kestus 59,3% sõitudest prognoositust pikemaks, kuid kaebuste osakaal oli 3,5%. Prediction-grupis oli tegelik kestus prognoositust pikem 75,4% sõitudest ning kaebuste osakaal oli 20,4%. See näitab gruppide vahelist seost, kuid ei tõenda, et prognoosi ja tegeliku sõidu erinevus põhjustas kaebusi.

- <b>Analüüsi järgmine samm</b> – Prediction- ja Upfront-grupp erinevad märgatavalt nii prognoositud ja tegeliku sõidu kestuse suhte kui ka kaebuste osakaalu poolest. See suunab analüüsi järgmise sammuna hinnastamistüübi juurde: kas teatud hinnastamistüüp on seotud suurema kaebuste osakaaluga?

</div>
""", unsafe_allow_html=True)


st.markdown("---")

st.subheader("Piirangud")

st.markdown("""
<div style="color: black;">

Analüüs põhineb ainult pöördumisega seotud sõitudel. Algne andmestik sisaldas
<b>4166 unikaalset sõitu</b>, kuid prognoositud ja tegeliku distantsi ning kestuse
võrdlemiseks moodustati eraldi analüüsivalim. Sellest eemaldati sõidud, kus
vajalikud prognoositud või tegelikud väärtused olid nullväärtusega, ning
ebanormaalse kiirusega sõidud, mille tegeliku distantsi või kestuse väärtused
võisid olla ebarealistlikud. Selle tulemusena jäi hajuvusdiagrammide ja
regressioonanalüüsi aluseks <b>4091 sõitu</b>. Lisaks puudus <b>19 sõidul
prognoos</b>, mistõttu neid ei ole vastavatel hajuvusdiagrammidel. Analüüs näitab
prognoositud ja tegelike väärtuste vahelist seost, kuid ei tõenda, et
prognoosist pikem sõit või kestus põhjustab kaebuse ega võimalda kindlaks teha
nende erinevuste täpset põhjust.

</div>
""", unsafe_allow_html=True)