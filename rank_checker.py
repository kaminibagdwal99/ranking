import requests
import streamlit as st

# Google Custom Search API setup
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]  # Add your Google API key to secrets.toml

REGION_CSE_MAP = {
    "Global": st.secrets["CSE_ID_GLOBAL"],
    "Singapore": st.secrets["CSE_ID_SG"],
    "Thailand": st.secrets["CSE_ID_TH"]
}

def get_rank_using_google_cse(keyword, target_domain, region="Global", max_results=100):
    """Fetch website rank using Google Custom Search API for a single keyword and region."""
    cse_id = REGION_CSE_MAP.get(region, REGION_CSE_MAP["Global"])

    for start_index in range(1, max_results, 10):
        params = {
            "q": keyword,
            "key": GOOGLE_API_KEY,
            "cx": cse_id,
            "num": 10,
            "start": start_index
        }

        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            results = response.json()
            if "items" in results:
                for idx, item in enumerate(results["items"], start=start_index):
                    if target_domain in item["link"]:
                        return idx
        except Exception as e:
            st.error(f"Error fetching rank: {e}")
            return None

    return f"Not in Top {max_results}"

def get_ranks_for_multiple_keywords(keywords, target_domain, region="Global"):
    """Fetch website ranks for a list of keywords within a specific region."""
    ranks = {}
    for keyword in keywords:
        rank = get_rank_using_google_cse(keyword, target_domain, region=region)
        ranks[keyword] = rank
    return ranks



