import streamlit as st
import pandas as pd
from rank_checker import get_ranks_for_multiple_keywords
from history import save_to_history, load_history, export_history_to_pdf
from agent import get_rank_agent

st.set_page_config(page_title="Website Rank Checker", layout="centered")
st.title("🔍 Website Rank Checker with Google Custom Search API")

# --- Inject CSS for custom button styles ---
st.markdown("""
    <style>
    .stButton > button {
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-weight: bold;
    }
    .green-btn button {
        background-color: #28a745 !important;
        color: white !important;
    }
    .yellow-btn button {
        background-color: #ffc107 !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Input Fields ---
selected_region = st.selectbox(
    "Select Region",
    ["Global", "Singapore", "Thailand", "Malaysia", "Indonesia"],
    index=0
)
keywords_input = st.text_area("Enter keywords (comma-separated):")
website = st.text_input("Enter website (e.g. example.com):")

# --- Green Button: Check Rank ---
with st.container():
    st.markdown('<div class="green-btn">', unsafe_allow_html=True)
    check = st.button("✅ Check Rank for Keywords")
    st.markdown('</div>', unsafe_allow_html=True)

if check:
    if keywords_input and website:
        keywords = [kw.strip() for kw in keywords_input.split(',')]
        ranks = get_ranks_for_multiple_keywords(keywords, website)
        if ranks:
            for keyword, rank in ranks.items():
                st.write(f"📈 Rank for **{website}** on **'{keyword}'**: **{rank}**")
            save_to_history(keywords, website, ranks, region=selected_region)
    else:
        st.warning("Please enter both keywords and website.")

# --- Show Rank History ---
if st.checkbox("Show Rank History"):
    history_df = load_history()
    if not history_df.empty:
        st.dataframe(history_df)

        # Filters
        kw_filter = st.text_input("Filter: Keyword")
        site_filter = st.text_input("Filter: Website")

        if kw_filter and site_filter:
            filtered = history_df[
                (history_df['keyword'] == kw_filter) &
                (history_df['website'] == site_filter)
            ]
            if not filtered.empty:
                filtered["timestamp"] = pd.to_datetime(filtered["timestamp"])
                filtered = filtered.sort_values("timestamp")
                filtered["rank"] = pd.to_numeric(filtered["rank"], errors='coerce')
                st.line_chart(data=filtered, x="timestamp", y="rank")
            else:
                st.info("No data matching filters.")
    else:
        st.info("No history data found.")

# --- Yellow Button: Export PDF ---
with st.container():
    st.markdown('<div class="yellow-btn">', unsafe_allow_html=True)
    export = st.button("📄 Export History as PDF")
    st.markdown('</div>', unsafe_allow_html=True)

if export:
    if website:
        pdf_buffer = export_history_to_pdf(website_filter=website, limit_dates=5)
        if pdf_buffer:
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer,
                file_name="rank_history_report.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("No history found to export.")
    else:
        st.warning("Please enter a website to filter before exporting.")

# --- LangChain Agent Interface ---
st.header("🧠 Ask the AI Agent")

query = st.text_input("Ask a natural language question (e.g. 'Where does openai.com rank for AI tools?')")

if st.button("Ask Agent"):
    agent = get_rank_agent()
    st.write(agent.run(query))
