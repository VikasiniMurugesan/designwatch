import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

st.title("Level 1 — Single Page Design Audit")
st.markdown("Upload a screenshot and get AI-powered design feedback across 5 principles.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Screenshot", type=["png", "jpg", "jpeg", "webp"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Screenshot", use_container_width=True)

    if st.button("Analyze Design", type="primary"):
        with st.spinner("Analyzing design... this may take 20–30 seconds"):
            try:
                response = requests.post(
                    f"{API_URL}/level1/analyze",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    timeout=120,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis complete!")

                    st.subheader("Summary")
                    st.info(data["summary"])

                    findings = data.get("findings", [])
                    st.subheader(f"Findings ({len(findings)})")

                    severity_colors = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                        "info": "🔵",
                    }

                    for i, f in enumerate(findings, 1):
                        severity = f.get("severity", "info").lower()
                        icon = severity_colors.get(severity, "⚪")
                        with st.expander(f"{icon} [{severity.upper()}] {f.get('principle', '')} — {f.get('location', '')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Issue:** {f.get('issue', '')}")
                                st.markdown(f"**User Impact:** {f.get('user_impact', '')}")
                            with col2:
                                st.markdown(f"**Recommendation:** {f.get('recommendation', '')}")
                                st.progress(f.get("confidence_score", 0) / 100)
                                st.caption(f"Confidence: {f.get('confidence_score', 0)}%")

                    st.subheader("Raw JSON")
                    st.json(data)

                    report_path = data.get("report_path")
                    if report_path:
                        try:
                            with open(report_path, "r") as f:
                                html_content = f.read()
                            st.download_button(
                                "Download HTML Report",
                                data=html_content,
                                file_name=f"designwatch_level1_scan_{data['scan_id']}.html",
                                mime="text/html",
                            )
                        except Exception:
                            pass
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API. Make sure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
