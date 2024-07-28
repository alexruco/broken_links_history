# get_history.py

import requests
import pandas as pd
from datetime import datetime
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

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
    retry = Retry(connect=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        if len(data) > 1:
            # Convert to DataFrame and filter
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        else:
            return pd.DataFrame(columns=["original"])
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return pd.DataFrame(columns=["original"])

def filter_urls(df):
    """
    Filter URLs to include only contentful URLs (e.g., HTML, PHP, PDF) and remove duplicates.
    """
    contentful_extensions = (".php", ".html", "/", ".pdf")
    filtered_df = df[df["original"].str.endswith(contentful_extensions, na=False)]
    filtered_df = filtered_df.drop_duplicates()
    return filtered_df
