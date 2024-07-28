# availability_checker.py

import requests
from concurrent.futures import ThreadPoolExecutor

def check_url(url):
    """
    Check the status of a URL.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            return url, True
        elif response.status_code == 404:
            return url, False
        else:
            return url, None
    except requests.RequestException:
        return url, None

def check_availability(urls, max_workers=10):
    """
    Check the availability of a list of URLs.
    """
    live_urls = []
    broken_urls = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_url, url): url for url in urls}
        for future in futures:
            url, status = future.result()
            if status is True:
                live_urls.append(url)
            elif status is False:
                broken_urls.append(url)

    return live_urls, broken_urls
