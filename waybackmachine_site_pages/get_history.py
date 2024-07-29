# get_history.py

import requests
import pandas as pd
from datetime import datetime
import logging
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_wayback_urls(domain, start_date="19960101", end_date=None):
    """
    Retrieve URLs from the Wayback Machine for a given domain and filter the results.
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    
    url = "http://web.archive.org/cdx/search/cdx"
    params = {
        "url": f"{domain}/*",
        "from": start_date,
        "to": end_date,
        "output": "json",
        "fl": "original",
        "collapse": "urlkey"
    }

    # Set up session with retries
    session = requests.Session()
    retry = Retry(total=10, connect=5, read=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        if len(data) > 1:
            # Convert to DataFrame and filter
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        else:
            return pd.DataFrame(columns=["original"])
    except requests.RequestException as e:
        logging.error(f"Error fetching data from Wayback Machine: {e}")
        return pd.DataFrame(columns=["original"])

def filter_urls(df):
    """
    Filter URLs to include only contentful URLs (e.g., HTML, PHP, PDF) and remove duplicates.
    """
    contentful_extensions = (".php", ".html", "/", ".pdf")
    filtered_df = df[df["original"].str.endswith(contentful_extensions, na=False)]
    filtered_df = filtered_df.drop_duplicates()
    return filtered_df
