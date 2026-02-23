import io
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# Dark theme CSS
st.markdown("""
<style>
html, body, #root, .block-container {
    background: linear-gradient(135deg, #030812 0%, #0b1020 50%, #0a1525 100%) !important;
    color: #e6eef8 !important;
}
.page-section-title {
    font-size: 1.2rem; font-weight: 700; color: #e6eef8;
    margin-top: 24px; margin-bottom: 16px;
    padding-bottom: 12px; border-bottom: 2px solid rgba(255,255,255,0.05);
}
</style>
""", unsafe_allow_html=True)

try:
    import plotly.express as px
except Exception:
    px = None


def _get_session_data():
    return globals().get("session_data")


def _sample_timeline(n=8):
    now = datetime.now()
    rows = []
    for i in range(n):
        start = now - timedelta(days=(n - i) * 2)
        end = start + timedelta(hours=2 + i)
        rows.append({
            "patient_id": f"P{i+1:03}",
            "event": f"Stage {i+1}",
            "start": start,
            "end": end,
            "provider": f"Dr. {(i%4)+1}",
            "value": (i + 1) * 10,
        })
    return pd.DataFrame(rows)


def _ensure_datetime_cols(df: pd.DataFrame):
    if "start" in df.columns and "end" in df.columns:
        df["start"] = pd.to_datetime(df["start"], errors="coerce")
        df["end"] = pd.to_datetime(df["end"], errors="coerce")
    else:
        # create simple start/end from index when missing
        df = df.copy()
        df["start"] = pd.date_range(datetime.now(), periods=len(df), freq="H")
        df["end"] = df["start"] + pd.to_timedelta(1, unit="h")
    return df


def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def _to_excel_bytes(df: pd.DataFrame) -> bytes:
    bio = io.BytesIO()
    try:
        with pd.ExcelWriter(bio, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="report")
        return bio.getvalue()
    except Exception:
        # fallback: write CSV bytes into .xls container
        return _to_csv_bytes(df)


def _to_json_bytes(df: pd.DataFrame) -> bytes:
    return df.to_json(orient="records", date_format="iso").encode("utf-8")


def _to_pdf_bytes(fig, summary_text: str = "") -> bytes:
    # Try to render the Plotly figure to PNG (kaleido) and embed into a simple PDF (reportlab)
    try:
        img_bytes = fig.to_image(format="png")
    except Exception as e:
        raise RuntimeError("Figure export not available (kaleido missing or failed): " + str(e))

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader

        bio = io.BytesIO()
        c = canvas.Canvas(bio, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, height - 40, "MedIntel X — Timeline Report")
        c.setFont("Helvetica", 9)
        c.drawString(40, height - 60, f"Generated: {datetime.now().isoformat()}")
        text_y = height - 80
        for line in summary_text.splitlines():
            c.drawString(40, text_y, line)
            text_y -= 12
        img = ImageReader(io.BytesIO(img_bytes))
        # place image below header
        c.drawImage(img, 40, 120, width=520, preserveAspectRatio=True, mask="auto")
        c.showPage()
        c.save()
        return bio.getvalue()
    except Exception as e:
        raise RuntimeError("PDF generation failed (reportlab missing or failed): " + str(e))


def run():
    st.set_page_config(page_title="Reports — MedIntel X", layout="wide")
    st.markdown("**Reports & Exports — Timeline**")
    st.write("Generate timeline-based reports and export them in multiple formats.")

    df = _get_session_data()
    if df is None:
        st.warning("No session data found — using a small sample timeline for preview.")
        df = _sample_timeline(8)

    if not isinstance(df, pd.DataFrame):
        try:
            df = pd.DataFrame(df)
        except Exception:
            st.error("Uploaded data could not be converted to a table. Please upload a CSV.")
            return

    df = _ensure_datetime_cols(df)

    # Detect available columns for grouping
    available_id_cols = [c for c in df.columns if c in ['patient_id', 'id', 'provider', 'department', 'doctor']]
    if not available_id_cols:
        available_id_cols = [df.columns[0]]  # fallback to first column
    
    available_event_cols = [c for c in df.columns if c in ['event', 'department', 'provider', 'outcome']]
    if not available_event_cols:
        available_event_cols = available_id_cols[:1]

    # Controls
    with st.sidebar.form("report_opts"):
        st.header("Report options")
        min_date = df["start"].min()
        max_date = df["end"].max()
        start = st.date_input("Start date", value=min_date.date() if pd.notna(min_date) else datetime.now().date())
        end = st.date_input("End date", value=max_date.date() if pd.notna(max_date) else (datetime.now().date()))
        
        # Dynamic group_by based on available columns
        group_by = st.selectbox("Group by", options=available_id_cols, index=0)
        metric = st.selectbox("Metric", options=["count", "value_sum"], index=0)
        formats = st.multiselect("Export formats", options=["CSV", "Excel", "JSON", "PDF"], default=["CSV", "PDF"])
        make_report = st.form_submit_button("Generate report")

    # filter by date range
    s = pd.to_datetime(start)
    e = pd.to_datetime(end) + pd.Timedelta(days=1)
    mask = (df["start"] >= s) & (df["start"] < e)
    filtered = df.loc[mask].copy()
    if filtered.empty:
        st.info("No events found in the selected date range — try widening the dates.")

    st.markdown("### Timeline")
    if px is None:
        st.error("Plotly not available; timeline visualization requires Plotly.")
    else:
        try:
            # Use available column or fallback to first numeric column
            group_col = group_by if group_by in filtered.columns else available_id_cols[0]
            fig = px.timeline(
                filtered.sort_values("start"),
                x_start="start",
                x_end="end",
                y=group_col,
                color=group_col,
                height=400,
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e6eef8"),
                hovermode='closest'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ Timeline visualization error: {str(e)}")
            st.info("💡 Available columns: " + ", ".join(filtered.columns.tolist()))

    # build small summary
    summary = []
    try:
        if not filtered.empty:
            group_col = group_by if group_by in filtered.columns else available_id_cols[0]
            grp = filtered.groupby(group_col)
            count = grp.size().rename("count")
            vals = None
            if "value" in filtered.columns:
                vals = grp["value"].sum().rename("value_sum")
            elif "treatment_cost" in filtered.columns:
                vals = grp["treatment_cost"].sum().rename("cost_sum")
            summary_df = pd.concat([count, vals], axis=1)
            summary_df = summary_df.fillna(0).reset_index()
            st.markdown("#### Summary")
            st.dataframe(summary_df, use_container_width=True)
            summary_text = summary_df.head(20).to_string(index=False)
        else:
            summary_text = "No events in range."
    except Exception as e:
        summary_text = f"Unable to create summary: {e}"

    # Exports
    st.markdown("### Export report")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    if "CSV" in formats:
        csv_bytes = _to_csv_bytes(filtered)
        col1.download_button("Download CSV", data=csv_bytes, file_name="report.csv", mime="text/csv")

    if "Excel" in formats:
        try:
            excel_bytes = _to_excel_bytes(filtered)
            col2.download_button("Download Excel", data=excel_bytes, file_name="report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception:
            col2.error("Excel export failed (openpyxl may be missing).")

    if "JSON" in formats:
        json_bytes = _to_json_bytes(filtered)
        col3.download_button("Download JSON", data=json_bytes, file_name="report.json", mime="application/json")

    if "PDF" in formats:
        try:
            if px is None:
                col4.error("PDF export requires Plotly to render a chart preview.")
            else:
                pdf_bytes = _to_pdf_bytes(fig, summary_text)
                col4.download_button("Download PDF", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")
        except Exception as e:
            col4.error(f"PDF error: {str(e)[:50]}")


if __name__ == "__main__":
    run()
