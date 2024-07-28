# availability_checker.py

import requests
from concurrent.futures import ThreadPoolExecutor

def check_url(url):
    """
    Check the status of a URL.
    """
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            return url, 200
        elif response.status_code == 404:
            return url, 404
        else:
            return url, response.status_code
    except requests.RequestException:
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
            if broken_links_only:
                if status == 404:
                    urls_with_status.append((url, status))
            else:
                urls_with_status.append((url, status))

    return urls_with_status
