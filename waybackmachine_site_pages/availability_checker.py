# availability_checker.py

import requests
from concurrent.futures import ThreadPoolExecutor
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_url(url, max_retries=3, backoff_factor=0.3):
    """
    Check the status of a URL with retry and backoff, always trying HTTPS.

    Args:
        url (str): The URL to check.
        max_retries (int): The maximum number of retries.
        backoff_factor (float): The backoff factor for exponential backoff.

    Returns:
        tuple: The URL and its status code or None if it failed.
    """
    # Convert HTTP URLs to HTTPS
    if url.startswith("http://"):
        url = "https://" + url[7:]

    for retry in range(max_retries):
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            return url, response.status_code
        except requests.RequestException as e:
            logging.error(f"Error checking URL {url}: {e}")
            time.sleep(backoff_factor * (2 ** retry))  # Exponential backoff

    return url, None

def check_availability(urls, max_workers=10, broken_links_only=True):
    """
    Check the availability of a list of URLs.

    Args:
        urls (list): List of URLs to check.
        max_workers (int): Maximum number of concurrent workers.
        broken_links_only (bool): Whether to return only broken links.

    Returns:
        list: List of tuples containing URLs and their status codes.
    """
    urls_with_status = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        for future in futures:
            url, status = future.result()
            if status is not None:
                if broken_links_only and status == 404:
                    urls_with_status.append((url, status))
                elif not broken_links_only:
                    urls_with_status.append((url, status))

    return urls_with_status
