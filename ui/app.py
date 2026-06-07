import streamlit as st

st.set_page_config(page_title="Designwatch", page_icon="🔍", layout="wide")

pages = {
    "Level 1 — Design Audit": "ui/pages/level1.py",
}

st.sidebar.title("Designwatch")
st.sidebar.caption("AI-powered UI/UX design audit agent")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", list(pages.keys()))

if page == "Level 1 — Design Audit":
    exec(open("ui/pages/level1.py").read())
