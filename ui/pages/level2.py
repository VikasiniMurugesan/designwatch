import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Level 2 — Before / After Regression Analysis")
st.markdown("Upload a baseline and a current screenshot to detect visual regressions and improvements.")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Before (Baseline)")
    baseline_file = st.file_uploader("Upload baseline screenshot", type=["png", "jpg", "jpeg", "webp"], key="baseline")
    if baseline_file:
        st.image(baseline_file, use_container_width=True)

with col2:
    st.subheader("After (Current)")
    current_file = st.file_uploader("Upload current screenshot", type=["png", "jpg", "jpeg", "webp"], key="current")
    if current_file:
        st.image(current_file, use_container_width=True)

if baseline_file and current_file:
    if st.button("Compare Designs", type="primary"):
        with st.spinner("Comparing designs... this may take 30–40 seconds"):
            try:
                response = requests.post(
                    f"{API_URL}/level2/analyze",
                    files={
                        "baseline": (baseline_file.name, baseline_file.getvalue(), baseline_file.type),
                        "current": (current_file.name, current_file.getvalue(), current_file.type),
                    },
                    timeout=120,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis complete!")

                    verdict = data.get("overall_verdict", "").upper()
                    verdict_color = {"IMPROVED": "🟢", "DEGRADED": "🔴", "UNCHANGED": "🟡"}.get(verdict, "⚪")
                    st.subheader(f"Overall Verdict: {verdict_color} {verdict}")

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Improvements", data.get("improvements_count", 0))
                    m2.metric("Regressions", data.get("regressions_count", 0))
                    m3.metric("Neutral", data.get("neutral_count", 0))

                    st.subheader("Summary")
                    st.info(data["summary"])

                    findings = data.get("findings", [])
                    st.subheader(f"Findings ({len(findings)})")

                    direction_icons = {"improvement": "🟢", "regression": "🔴", "neutral": "🟡"}

                    for f in findings:
                        direction = f.get("direction", "neutral").lower()
                        icon = direction_icons.get(direction, "⚪")
                        a11y = " ♿ Accessibility Regression" if f.get("accessibility_regression") else ""
                        with st.expander(f"{icon} [{direction.upper()}] {f.get('change_type', '')} — {f.get('location', '')}{a11y}"):
                            st.markdown(f"**What changed:** {f.get('description', '')}")
                            st.markdown(f"**Reasoning:** {f.get('reasoning', '')}")
                            st.markdown(f"**User Impact:** {f.get('user_impact', '')}")
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
                                file_name=f"designwatch_level2_scan_{data['scan_id']}.html",
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
elif baseline_file or current_file:
    st.warning("Please upload both a baseline and a current screenshot to proceed.")
