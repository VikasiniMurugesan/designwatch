import streamlit as st
import json
from repositories.scan_repository import SessionLocal, get_all_scans

st.title("Scan History")
st.markdown("All past scans stored in the local database.")
st.markdown("---")

db = SessionLocal()
scans = get_all_scans(db)
db.close()

if not scans:
    st.info("No scans yet. Run a Level 1, Level 2, or Level 3 scan to see results here.")
else:
    for scan in scans:
        level_labels = {"level1": "Level 1 — Design Audit", "level2": "Level 2 — Regression", "level3": "Level 3 — Browser Scan"}
        label = level_labels.get(scan.level.value, scan.level.value)
        status_icon = "✅" if scan.status.value == "completed" else "⏳" if scan.status.value == "pending" else "❌"
        created = scan.created_at.strftime("%Y-%m-%d %H:%M") if scan.created_at else "—"

        with st.expander(f"{status_icon} [{label}] Scan #{scan.id} — {created}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Status:** {scan.status.value}")
                st.markdown(f"**Level:** {label}")
                if scan.target_url:
                    st.markdown(f"**URL:** {scan.target_url}")
            with col2:
                if scan.completed_at:
                    st.markdown(f"**Completed:** {scan.completed_at.strftime('%Y-%m-%d %H:%M')}")

            if scan.summary:
                st.markdown(f"**Summary:** {scan.summary}")

            if scan.findings_json:
                findings = json.loads(scan.findings_json)
                st.markdown(f"**Findings:** {len(findings)}")
                if st.checkbox("Show findings JSON", key=f"json_{scan.id}"):
                    st.json(findings)

            if scan.report_path:
                try:
                    with open(scan.report_path, "r") as f:
                        html_content = f.read()
                    st.download_button(
                        "Download Report",
                        data=html_content,
                        file_name=f"designwatch_scan_{scan.id}.html",
                        mime="text/html",
                        key=f"dl_{scan.id}",
                    )
                except Exception:
                    pass
