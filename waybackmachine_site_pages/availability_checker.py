# availability_checker.py

import requests
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import random
import string

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define headers to emulate a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Generate a random hash
def generate_random_hash(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Check how the site handles non-existing pages
def get_non_existing_page_redirect(url, timeout=20):
    random_hash = generate_random_hash()
    non_existing_url = f"{url.rstrip('/')}/{random_hash}/"
    try:
        response = requests.get(non_existing_url, headers=HEADERS, allow_redirects=True, timeout=timeout, verify=False)
        if response.history:
            final_url = response.url
            return final_url
        return non_existing_url
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking non-existing URL: {non_existing_url}: {e}")
        return None

def check_url_with_requests(url, timeout=20):
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=timeout, verify=False)
        redirects = []
        if response.history:
            for resp in response.history:
                redirect_info = {
                    'from': resp.url,
                    'to': response.url,
                    'status_code': resp.status_code
                }
                redirects.append(redirect_info)
                logging.debug(f"Redirected from {resp.url} to {response.url} with status {resp.status_code}")
        logging.debug(f"Final URL: {response.url}, Status Code: {response.status_code}")
        return url, response.status_code, redirects
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking URL with requests: {url}: {e}")
        return url, None, []

def check_url_with_selenium(url):
    try:
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options, executable_path='/path/to/chromedriver')
        driver.get(url)
        time.sleep(5)
        page_source = driver.page_source.lower()
        final_url = driver.current_url
        driver.quit()
        
        status_code = 200
        if any(keyword in page_source for keyword in NOT_FOUND_KEYWORDS):
            status_code = 404
        
        return url, status_code, [{'from': url, 'to': final_url, 'status_code': status_code}]
    except Exception as e:
        logging.error(f"Error checking URL with Selenium: {url}: {e}")
        return url, None, []

def check_url(url, access_type='requests', non_existing_url_redirect=None, max_retries=3, backoff_factor=0.3, timeout=20):
    """
    Check the status of a URL with retry and backoff, using the specified access method (requests or selenium).

    Args:
        url (str): The URL to check.
        access_type (str): The type of access method to use ('requests' or 'selenium').
        non_existing_url_redirect (str): The URL to which non-existing pages redirect.
        max_retries (int): The maximum number of retries.
        backoff_factor (float): The backoff factor for exponential backoff.
        timeout (int): The timeout for the request.

    Returns:
        tuple: The URL, its status code, and any redirects that occurred.
    """
    if url.startswith("http://"):
        hostname = url.split('/')[2]
        if ":80" not in hostname:
            url = "https://" + url[7:]

    if access_type == 'requests':
        for retry in range(max_retries):
            url, status_code, history = check_url_with_requests(url, timeout)
            if status_code is not None:
                if non_existing_url_redirect and url in [r['to'] for r in history]:
                    status_code = 404
                return url, status_code, history
            logging.debug(f"Retry {retry + 1} for URL: {url}")
            time.sleep(backoff_factor * (2 ** retry))
    elif access_type == 'selenium':
        return check_url_with_selenium(url)

    return url, None, []

def check_availability(urls, access_type='requests', non_existing_url_redirect=None, max_workers=10, broken_links_only=True):
    """
    Check the availability of a list of URLs.

    Args:
        urls (list): List of URLs to check.
        access_type (str): The type of access method to use ('requests' or 'selenium').
        non_existing_url_redirect (str): The URL to which non-existing pages redirect.
        max_workers (int): Maximum number of concurrent workers.
        broken_links_only (bool): Whether to return only broken links.

    Returns:
        list: List of dictionaries containing URLs, their status codes, and any redirects.
    """
    urls_with_status = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url, url, access_type, non_existing_url_redirect): url for url in urls}
        for future in futures:
            url, status, redirects = future.result()
            if status is not None:
                logging.debug(f"Checked URL: {url}, Status: {status}, Redirects: {redirects}")
                url_info = {
                    'url': url,
                    'status': status,
                    'redirects': redirects
                }
                if broken_links_only:
                    if status == 404:
                        urls_with_status.append(url_info)
                        print(f"Broken Link Found: {url_info}")
                else:
                    urls_with_status.append(url_info)

    print(f"URLs with Status: {urls_with_status}")
    return urls_with_status
