import streamlit as st

pages = {

    "": [
        st.Page("pages/1_ülevaade.py", title="Ülevaade", icon="🏠"),
        st.Page("pages/3_andmed.py", title="Andmed", icon="📊"),
        st.Page("pages/4_andmepuhastus.py", title="Andmepuhastus", icon="🧹"),
        st.Page("pages/2_mudel.py", title="Mudel", icon="🤖")
    ]

}

pg = st.navigation(pages)

pg.run()