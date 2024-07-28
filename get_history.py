# get_history.py

import requests
import pandas as pd
from datetime import datetime

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

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1:
            # Convert to DataFrame and filter
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        else:
            return pd.DataFrame(columns=["original"])
    else:
        print("Error fetching data:", response.status_code)
        return pd.DataFrame(columns=["original"])

def filter_urls(df):
    """
    Filter URLs to include only contentful URLs (e.g., HTML, PHP, PDF) and remove duplicates.
    """
    contentful_extensions = (".php", ".html", "/", ".pdf")
    filtered_df = df[df["original"].str.endswith(contentful_extensions, na=False)]
    filtered_df = filtered_df.drop_duplicates()
    return filtered_df
