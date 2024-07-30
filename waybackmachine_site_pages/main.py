# main.py

import os
import json
import sys
from datetime import datetime
from waybackmachine_site_pages import waybackmachine_pages, check_availability, get_non_existing_page_redirect, display_urls

def save_to_json(domain, links_set):
    """
    Save the links set to a JSON file in the audits/{domain}/{timestamp}_potential_brokenlinks.json format.

    Args:
        domain (str): The domain to save the results for.
        links_set (list): The list of dictionaries containing URLs, their status codes, and any redirects.
    """
    try:
        # Ensure the directory exists
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        directory = f"audits/{domain}"
        os.makedirs(directory, exist_ok=True)

        # Create the file path
        file_path = os.path.join(directory, f"{timestamp}_potential_brokenlinks.json")

        # Print the data
        print(f"Final audit data: {links_set}")

        # Save to JSON file
        with open(file_path, "w") as json_file:
            json.dump(links_set, json_file, indent=4)

        print(f"Results saved to {file_path}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def main(domain, iterations, broken_links_only):
    try:
        # Determine the redirect URL for non-existing pages
        non_existing_url_redirect = get_non_existing_page_redirect(domain)
        print(f"Non-existing pages redirect to: {non_existing_url_redirect}")

        # Step 1: Discover URLs using waybackmachine_pages
        discovered_urls = waybackmachine_pages(domain, iterations=iterations, broken_links_only=broken_links_only)
        print(f"Discovered URLs: {discovered_urls}")

        # Ensure discovered_urls is a set of tuples
        if not isinstance(discovered_urls, set):
            raise ValueError("Expected discovered_urls to be a set of tuples")

        # Step 2: Check availability using requests
        urls_list = [url for url, status in discovered_urls]
        print(f"URLs List: {urls_list}")
        checked_urls_requests = check_availability(urls_list, access_type='requests', non_existing_url_redirect=non_existing_url_redirect, max_workers=10, broken_links_only=broken_links_only)
        print(f"Checked URLs with requests: {checked_urls_requests}")

        # Filter out URLs that failed with requests
        failed_urls = [url_info['url'] for url_info in checked_urls_requests if url_info['status'] is None]
        successful_urls = [url_info for url_info in checked_urls_requests if url_info['status'] is not None]

        print(f"Failed URLs with requests: {failed_urls}")
        print(f"Successful URLs with requests: {successful_urls}")

        # Step 3: Check availability using selenium for failed URLs
        if failed_urls:
            checked_urls_selenium = check_availability(failed_urls, access_type='selenium', non_existing_url_redirect=non_existing_url_redirect, max_workers=10, broken_links_only=broken_links_only)
            successful_urls.extend(checked_urls_selenium)
            print(f"Successful URLs with selenium: {checked_urls_selenium}")

        # Step 4: Save results to JSON file
        save_to_json(domain, successful_urls)

    except Exception as e:
        print(f"An error occurred during execution: {e}")
        save_to_json(domain, [])

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <domain> <iterations> <broken_links_only>")
        sys.exit(1)
    
    domain = sys.argv[1]
    iterations = int(sys.argv[2])
    broken_links_only = sys.argv[3].lower() == 'true'
    main(domain, iterations, broken_links_only)
