# waybackmachine_pages.py

import time
from get_history import get_wayback_urls, filter_urls
from availability_checker import check_availability

def waybackmachine_pages(domain, iterations=10, broken_links_only=True):
    """
    Fetches and checks the availability of URLs from the Wayback Machine for a given domain.

    Args:
        domain (str): The domain to search for in the Wayback Machine.
        iterations (int, optional): Number of iterations to run the search. Default is 10.
        broken_links_only (bool, optional): Flag to return only broken links. Default is True.

    Returns:
        set: A set of tuples containing URLs and their status codes.
    """
    links_set = set()

    for i in range(iterations):
        urls_df = get_wayback_urls(domain)

        filtered_urls_df = filter_urls(urls_df)

        if not filtered_urls_df.empty:
            urls = filtered_urls_df["original"].tolist()

            urls_with_status = check_availability(urls, max_workers=iterations, broken_links_only=broken_links_only)
            
            # Adjusted to handle possible multiple return values
            for url_status in urls_with_status:
                url = url_status[0]
                status = url_status[1]

                if broken_links_only and status == 404:
                    links_set.add((url, status))
                elif not broken_links_only:
                    links_set.add((url, status))

            print(f"Iteration {i + 1}/{iterations} completed.")
            time.sleep(1)  # Adding a delay to avoid overwhelming the server
        else:
            print("No contentful URLs found.")
            break

    return links_set

def display_urls(links_set):
    """
    Displays the URLs and their status.

    Args:
        links_set (set): A set of tuples containing URLs and their status codes.
    """
    if links_set:
        print("\nURLs:")
        for url, status in links_set:
            print(f"{url} - Status: {status}")
    else:
        print("No URLs found.")

# Example usage
if __name__ == "__main__":
    domain = "marketividade.com"
    broken_links = waybackmachine_pages(domain, iterations=1, broken_links_only=True)
    display_urls(broken_links)
