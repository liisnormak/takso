import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(
    page_title="Mudel",
    page_icon="🤖",
    layout="wide"
)

# -------------------------
# Kujundus
# -------------------------

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

[data-testid="stMarkdownContainer"] {
    color: black;
}

/* Pealkirjad */

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

/* KPI kaardid */

.model-kpi-card {
    background-color: #f5f5f5;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #dddddd;
    text-align: center;
    min-height: 125px;
}

.model-kpi-title {
    font-size: 18px;
    font-weight: 700;
    color: #333333;
}

.model-kpi-value {
    font-size: 30px;
    font-weight: 800;
    color: #111111;
    margin-top: 10px;
}

.model-kpi-description {
    font-size: 13px;
    color: #666666;
    margin-top: 6px;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #262730;
}

[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] a span,
[data-testid="stSidebarNav"] a p {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# Pealkiri
# -------------------------

st.title("Mudeli analüüs")

st.write(
    "Masinõppemudeli eesmärk on hinnata, kas sõiduga kaasneb "
    "hinnastamisega seotud kaebus."
)

st.write(
    "Mudel kasutab sõidu omadusi, et ennustada, kas sõit kuulub "
    "kaebusega või kaebuseta sõitude hulka."
)

st.divider()


# -------------------------
# Mudel 1
# -------------------------

st.subheader("Mudel 1 — üldmudel")

st.markdown(
    '<div style="text-align: center; color: #555555; font-size: 16px; margin-bottom: 20px;">'
    'Testandmestik: 830 sõitu (20%)'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="model-kpi-card">
        <div class="model-kpi-title">Mudeli tüüp</div>
        <div class="model-kpi-value">Random Forest</div>
        <div class="model-kpi-description">Klassifitseerimismudel</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="model-kpi-card">
        <div class="model-kpi-title">Täpsus</div>
        <div class="model-kpi-value">92%</div>
        <div class="model-kpi-description">Kõikidest prognoosidest õiged</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="model-kpi-card">
        <div class="model-kpi-title">Kaebuse recall</div>
        <div class="model-kpi-value">27%</div>
        <div class="model-kpi-description">Tegelikest kaebustest leitud</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="model-kpi-card">
        <div class="model-kpi-title">F1-skoor</div>
        <div class="model-kpi-value">33%</div>
        <div class="model-kpi-description">Täpsuse ja recall'i tasakaal</div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("Mudeli prognoosid võrreldes tegeliku tulemusega")

# Päised
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("**Mudel / tegelik tulemus**")

with col2:
    st.markdown("**Tegelikult: ei**")

with col3:
    st.markdown("**Tegelikult: jah**")


# Mudel: ei
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("**Mudel: ei**")

with col2:
    st.metric("Õige prognoos", "743")

with col3:
    st.metric("Kaebus jäi leidmata", "45")


# Mudel: jah
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("**Mudel: jah**")

with col2:
    st.metric("Kaebust ei olnud", "25")

with col3:
    st.metric("Õige prognoos", "17")

st.subheader("Mudeli tunnuste olulisus")

feature_importance = pd.DataFrame({
    "Tunnus": [
        "EL-i näitaja",
        "Sõiduvahemaa erinevus",
        "Sõiduaja erinevus",
        "Pettuseriski näitaja",
        "Tegelik sõiduaeg",
        "Tegelik sõiduvahemaa",
        "GPS-i täpsus",
        "Prognoositud sõiduaeg",
        "Prognoositud sõidu tüüp",
        "Prognoositud sõiduvahemaa",
        "Ette lubatud hinnaga sõit",
        "Sõidu alguse tund",
        "TECNO",
        "Samsung",
        "Juhi rakenduse versioon DA.4.37",
        "Juhi rakenduse versioon DA.4.39",
        "Päeva periood: lõuna",
        "Päeva periood: hommik",
        "Nädalapäev: reede",
        "Nädalapäev: pühapäev"
    ],
    "Olulisus": [
        0.100428,
        0.066039,
        0.062904,
        0.061398,
        0.059780,
        0.055890,
        0.055743,
        0.052495,
        0.048305,
        0.046764,
        0.038046,
        0.036494,
        0.020642,
        0.011097,
        0.010069,
        0.008582,
        0.007974,
        0.007766,
        0.007608,
        0.007578
    ]
})

feature_importance["Olulisus (%)"] = feature_importance["Olulisus"] * 100

fig_importance = px.bar(
    feature_importance.sort_values("Olulisus (%)"),
    x="Olulisus (%)",
    y="Tunnus",
    orientation="h",
    text="Olulisus (%)",
    labels={
        "Olulisus (%)": "Olulisus (%)",
        "Tunnus": ""
    }
)

fig_importance.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    textfont=dict(
        family="Arial Black",
        size=14,
        color="black"
    )
)

fig_importance.update_xaxes(
    title_text="Olulisus (%)",
    title_font=dict(size=14, family="Arial Black", color="black"),
    tickfont=dict(size=13, family="Arial Black", color="black")
)

fig_importance.update_yaxes(
    tickfont=dict(size=13, family="Arial Black", color="black")
)

fig_importance.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=260, r=80, t=20, b=60)
)

st.plotly_chart(fig_importance, width="stretch")

st.write(
    "Tunnuse olulisus näitab, kui palju konkreetne tunnus mudeli prognoosidesse panustab. "
    "Suurem olulisus tähendab, et mudel kasutab seda tunnust oma otsustes rohkem. "
    "Olulisus ei näita, et tunnus põhjustab kaebuse tekkimist."
)
# -------------------------
# Mudel 2
# -------------------------
st.subheader("Mudel 2 — prognoositud sõitude mudel")
st.markdown(
    '<div style="text-align: center; color: #555555; font-size: 16px; margin-bottom: 20px;">'
    'Testandmestik: 200 sõitu (20%)'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="model-kpi-card">
        <div class="model-kpi-title">Mudeli tüüp</div>
        <div class="model-kpi-value">Random Forest</div>
        <div class="model-kpi-description">Klassifitseerimismudel</div>
    </div>
    """, unsafe_allow_html=True)

with col2: st.markdown(""" <div class="model-kpi-card"> <div class="model-kpi-title">Täpsus</div> <div class="model-kpi-value">78%</div> <div class="model-kpi-description">Kõikidest prognoosidest õiged</div> </div> """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="model-kpi-card">
        <div class="model-kpi-title">Kaebuse recall</div>
        <div class="model-kpi-value">37%</div>
        <div class="model-kpi-description">Tegelikest kaebustest leitud</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="model-kpi-card">
        <div class="model-kpi-title">F1-skoor</div>
        <div class="model-kpi-value">41%</div>
        <div class="model-kpi-description">Täpsuse ja recall'i tasakaal</div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("Mudeli prognoosid võrreldes tegeliku tulemusega")

# Päised
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("**Mudel / tegelik tulemus**")

with col2:
    st.markdown("**Tegelikult: ei**")

with col3:
    st.markdown("**Tegelikult: jah**")


# Mudel: ei
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("**Mudel: ei**")

with col2:
    st.metric("Õige prognoos", "141")

with col3:
    st.metric("Kaebus jäi leidmata", "26")


# Mudel: jah
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("**Mudel: jah**")

with col2:
    st.metric("Kaebust ei olnud", "18")

with col3:
    st.metric("Õige prognoos", "15")

st.subheader("Mudeli tunnuste olulisus")

feature_importance_prediction = pd.DataFrame({
    "Tunnus": [
        "Sõiduvahemaa erinevus",
        "Tegelik sõiduvahemaa",
        "Prognoositud sõiduvahemaa",
        "Prognoositud sõiduaeg",
        "Sõiduaja erinevus",
        "Tegelik sõiduaeg",
        "GPS-i täpsus",
        "Sõidu alguse tund",
        "TECNO",
        "Nädalapäev: pühapäev",
        "Rider app group CA.5",
        "Päeva periood: lõuna",
        "Rider app group CI.4",
        "Samsung",
        "Nädalapäev: reede",
        "HMD",
        "Päeva periood: hommik",
        "Nädalapäev: teisipäev",
        "Nädalapäev: neljapäev",
        "INFINIX"
    ],
    "Olulisus": [
        0.127507,
        0.121149,
        0.091041,
        0.090251,
        0.089669,
        0.088698,
        0.066937,
        0.063692,
        0.016364,
        0.016085,
        0.012961,
        0.012788,
        0.012089,
        0.012078,
        0.012035,
        0.011793,
        0.011399,
        0.010933,
        0.010814,
        0.010401
    ]
})

feature_importance_prediction["Olulisus (%)"] = (
    feature_importance_prediction["Olulisus"] * 100
)
fig_importance_prediction = px.bar(
    feature_importance_prediction.sort_values("Olulisus (%)"),
    x="Olulisus (%)",
    y="Tunnus",
    orientation="h",
    text="Olulisus (%)",
    labels={
        "Olulisus (%)": "Olulisus (%)",
        "Tunnus": ""
    }
)

fig_importance_prediction.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside",
    textfont=dict(
        family="Arial Black",
        size=14,
        color="black"
    )
)

fig_importance_prediction.update_xaxes(
    title_text="Olulisus (%)",
    title_font=dict(size=14, family="Arial Black", color="black"),
    tickfont=dict(size=13, family="Arial Black", color="black")
)

fig_importance_prediction.update_yaxes(
    tickfont=dict(size=13, family="Arial Black", color="black")
)

fig_importance_prediction.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=260, r=80, t=20, b=60)
)

st.plotly_chart(fig_importance_prediction, width="stretch")
st.write(
    "Tunnuse olulisus näitab, kui palju konkreetne tunnus mudeli prognoosidesse panustab. "
    "Suurem olulisus tähendab, et mudel kasutab seda tunnust oma otsustes rohkem. "
    "Olulisus ei näita, et tunnus põhjustab kaebuse tekkimist."
)