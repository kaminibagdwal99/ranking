import pandas as pd
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import streamlit as st

HISTORY_FILE = "rank_history.csv"

def save_to_history(keywords, website, ranks, region="Global"):
    """Save the history of ranks for multiple keywords and region."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = []
    for keyword, rank in ranks.items():
        data.append({
            "timestamp": timestamp,
            "keyword": keyword,
            "website": website,
            "region": region,
            "rank": rank
        })
    df = pd.DataFrame(data)
    if os.path.exists(HISTORY_FILE):
        df.to_csv(HISTORY_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(HISTORY_FILE, index=False)


def load_history():
    """Load the rank history from file, handling both 4 and 5 column formats."""
    if os.path.exists(HISTORY_FILE):
        try:
            # Try reading with headers first
            df = pd.read_csv(HISTORY_FILE)
        except pd.errors.ParserError:
            # Try reading without headers if there's a mismatch
            df = pd.read_csv(HISTORY_FILE, header=None)

        # Handle 4 or 5 column formats
        if df.shape[1] == 4:
            df.columns = ["timestamp", "keyword", "website", "rank"]
            df["region"] = "Global"  # Assign default
        elif df.shape[1] == 5:
            df.columns = ["timestamp", "keyword", "website", "region", "rank"]
        else:
            raise ValueError("Unexpected number of columns in rank_history.csv")

        df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
        df = df.dropna(subset=["rank"])
        df["rank"] = df["rank"].astype(int)
        return df
    return pd.DataFrame()


import matplotlib.pyplot as plt
from reportlab.platypus import Image
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors


def export_history_to_pdf(website_filter=None, limit_dates=5):
    """Export enhanced PDF report with chart limited to recent N dates."""
    
    df = load_history()
    if df.empty:
        st.warning("No history found.")
        return

    # Filter by website if provided
    if website_filter:
        df = df[df["website"] == website_filter]
        if df.empty:
            st.warning(f"No history found for website: {website_filter}")
            return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df = df.dropna(subset=["timestamp"])
    df["date"] = df["timestamp"].dt.date

    # Limit to recent N dates
    recent_dates = sorted(df["date"].unique(), reverse=True)[:limit_dates]
    df = df[df["date"].isin(recent_dates)]

    # Pivot to get keywords x dates
    pivot_df = df.pivot_table(index="keyword", columns="date", values="rank", aggfunc="first")
    pivot_df = pivot_df.sort_index(axis=1)  # sort columns (dates)


    # Create PDF document
    doc = SimpleDocTemplate("rank_history_report.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("📊 Website Rank Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # if not pivot_df.empty and "website" in df.columns:
    #     website = df["website"].iloc[0]
    #     elements.append(Paragraph(f"Website: <b>{website}</b>", styles['Heading2']))
    #     elements.append(Spacer(1, 12))
    if not pivot_df.empty and "website" in df.columns:
        website = df["website"].iloc[0]
        elements.append(Paragraph(f"Website: <b>{website}</b>", styles['Heading2']))

        # Show region(s)
        if "region" in df.columns:
            regions = ", ".join(sorted(df["region"].dropna().unique()))
            elements.append(Paragraph(f"Region(s): <b>{regions}</b>", styles['Heading2']))
        
        elements.append(Spacer(1, 12))


    elements.append(Paragraph("🔎 Keyword Rank Table", styles['Heading3']))
    keyword_data = [["Keyword"] + [str(date) for date in pivot_df.columns]]
    for keyword, row in pivot_df.iterrows():
        keyword_data.append([keyword] + [int(rank) if pd.notna(rank) else "-" for rank in row])

    keyword_table = Table(keyword_data, repeatRows=1)
    keyword_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(keyword_table)

    doc.build(elements)
    st.success(f"✅ PDF exported with the last 5 dates as `rank_history_report.pdf`")
