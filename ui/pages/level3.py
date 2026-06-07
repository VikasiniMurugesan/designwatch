import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("Level 3 — Autonomous Regression Scan")
st.markdown("Automatically navigates the target website, captures screenshots, and detects visual regressions against the stored baseline.")
st.markdown("---")

target_url = st.text_input("Target Website URL", value="http://localhost:3000", help="The URL of the frontend app to scan")

col1, col2 = st.columns(2)

with col1:
    scan_button = st.button("Run Scan", type="primary", use_container_width=True)

with col2:
    refresh_button = st.button("Refresh Baseline", use_container_width=True, help="Clear stored baselines — next scan will create fresh ones")

if refresh_button:
    try:
        resp = requests.post(f"{API_URL}/level3/refresh-baseline", timeout=10)
        if resp.status_code == 200:
            st.success(resp.json().get("message", "Baseline cleared."))
        else:
            st.error("Failed to refresh baseline.")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API. Make sure the FastAPI server is running on port 8000.")

if scan_button:
    if not target_url:
        st.warning("Please enter a target URL.")
    else:
        with st.spinner("Scanning pages... this may take 1–3 minutes"):
            try:
                response = requests.post(
                    f"{API_URL}/level3/scan",
                    json={"url": target_url},
                    timeout=300,
                )
                if response.status_code == 200:
                    data = response.json()

                    if data.get("baseline_created"):
                        st.success("Baseline created! Screenshots captured for all pages. Run the scan again to detect regressions.")
                        st.info(data.get("summary", ""))
                    else:
                        regressions = data.get("regressions", [])
                        total = data.get("total_regressions", 0)

                        if total == 0:
                            st.success("No regressions detected. The UI looks good!")
                        else:
                            st.error(f"{total} regression(s) detected!")

                        st.subheader("Summary")
                        st.info(data.get("summary", ""))

                        st.subheader("Pages Scanned")
                        for p in data.get("pages_scanned", []):
                            status_icon = "🔴" if p.get("has_regressions") else "🟢"
                            st.markdown(f"{status_icon} **{p['page']}** — {p.get('summary', 'No regressions found')}")

                        if regressions:
                            st.subheader(f"Regressions ({total})")
                            severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                            for r in regressions:
                                severity = r.get("severity", "medium").lower()
                                icon = severity_icons.get(severity, "⚪")
                                with st.expander(f"{icon} [{severity.upper()}] {r.get('page', '')} — {r.get('location', '')}"):
                                    st.markdown(f"**Issue:** {r.get('issue', '')}")
                                    st.markdown(f"**Evidence:** {r.get('evidence', '')}")
                                    st.progress(r.get("confidence_score", 0) / 100)
                                    st.caption(f"Confidence: {r.get('confidence_score', 0)}%")

                        report_path = data.get("report_path")
                        if report_path:
                            try:
                                with open(report_path, "r") as f:
                                    html_content = f.read()
                                st.download_button(
                                    "Download HTML Report",
                                    data=html_content,
                                    file_name=f"designwatch_level3_scan_{data['scan_id']}.html",
                                    mime="text/html",
                                )
                            except Exception:
                                pass

                        if total > 0:
                            st.info("A report has been emailed to the configured recipients.")
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the API. Make sure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
