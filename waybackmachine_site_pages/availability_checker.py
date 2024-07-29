# availability_checker.py

import requests
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import urllib3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_url(url, max_retries=3, backoff_factor=0.3, timeout=20):
    """
    Check the status of a URL with retry and backoff, avoiding SSL errors by not converting port-specific HTTP URLs to HTTPS.

    Args:
        url (str): The URL to check.
        max_retries (int): The maximum number of retries.
        backoff_factor (float): The backoff factor for exponential backoff.
        timeout (int): The timeout for the request.

    Returns:
        tuple: The URL and its status code or None if it failed.
    """
    # Convert HTTP URLs to HTTPS unless they specify port 80
    if url.startswith("http://") and not url.startswith("http://") + url.split('/')[2].split(':')[0] + ":80":
        url = "https://" + url[7:]

    for retry in range(max_retries):
        try:
            # Use GET instead of HEAD
            response = requests.get(url, allow_redirects=True, timeout=timeout, verify=False)
            return url, response.status_code
        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout error checking URL {url}: {e}")
        except requests.exceptions.SSLError as e:
            logging.error(f"SSL error checking URL {url}: {e}")
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error checking URL {url}: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error checking URL {url}: {e}")

        # Exponential backoff
        time.sleep(backoff_factor * (2 ** retry))

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
