# availability_checker.py

import requests
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_url(url):
    """
    Check the status of a URL.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return url, response.status_code
    except requests.RequestException as e:
        logging.error(f"Error checking URL {url}: {e}")
        return url, None

def check_availability(urls, max_workers=10, broken_links_only=True):
    """
    Check the availability of a list of URLs.
    """
    urls_with_status = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        for future in futures:
            url, status = future.result()
            if status is not None:
                if broken_links_only:
                    if status == 404:
                        urls_with_status.append((url, status))
                else:
                    urls_with_status.append((url, status))

    return urls_with_status
