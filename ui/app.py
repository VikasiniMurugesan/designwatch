import streamlit as st

st.set_page_config(page_title="Designwatch", page_icon="🔍", layout="wide")

st.sidebar.title("Designwatch")
st.sidebar.caption("AI-powered UI/UX design audit agent")
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate", [
    "Level 1 — Design Audit",
    "Level 2 — Before/After Regression",
    "Level 3 — Autonomous Scan",
    "History",
])

if page == "Level 1 — Design Audit":
    exec(open("ui/pages/level1.py").read())
elif page == "Level 2 — Before/After Regression":
    exec(open("ui/pages/level2.py").read())
elif page == "Level 3 — Autonomous Scan":
    exec(open("ui/pages/level3.py").read())
elif page == "History":
    exec(open("ui/pages/history.py").read())
