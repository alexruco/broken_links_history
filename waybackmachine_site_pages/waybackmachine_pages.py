import time
from get_history import get_wayback_urls, filter_urls
from availability_checker import check_availability
import logging

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
        try:
            urls_df = get_wayback_urls(domain)
            logging.debug(f"Iteration {i + 1}: Retrieved URLs DataFrame: {urls_df}")

            filtered_urls_df = filter_urls(urls_df)
            logging.debug(f"Iteration {i + 1}: Filtered URLs DataFrame: {filtered_urls_df}")

            if not filtered_urls_df.empty:
                urls = filtered_urls_df["original"].tolist()
                logging.debug(f"Iteration {i + 1}: URLs to Check: {urls}")

                urls_with_status = check_availability(urls, access_type='requests', max_workers=iterations, broken_links_only=broken_links_only)
                logging.debug(f"Iteration {i + 1}: URLs with Status: {urls_with_status}")

                # Adjusted to handle possible multiple return values
                for url_status in urls_with_status:
                    url = url_status[0]
                    status = url_status[1]

                    if broken_links_only and status == 404:
                        links_set.add((url, status))
                    elif not broken_links_only:
                        links_set.add((url, status))

                logging.info(f"Iteration {i + 1}/{iterations} completed.")
                time.sleep(1)  # Adding a delay to avoid overwhelming the server
            else:
                logging.info("No contentful URLs found.")
                break

        except Exception as e:
            logging.error(f"An error occurred during iteration {i + 1}: {e}")
            break

    return links_set
