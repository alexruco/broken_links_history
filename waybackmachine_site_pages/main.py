import os
import json
import sys
from datetime import datetime
from waybackmachine_site_pages import waybackmachine_pages, check_availability
import logging

# Configure logging to output to both console and a log file
log_file = f"audits/log_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def save_to_json(domain, links_set):
    """
    Save the links set to a JSON file in the audits/{domain}/{timestamp}_potential_brokenlinks.json format.

    Args:
        domain (str): The domain to save the results for.
        links_set (list): The list of dictionaries containing URLs, their status codes, and any redirects.
    """
    # Ensure the directory exists
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    directory = f"audits/{domain}"
    os.makedirs(directory, exist_ok=True)

    # Create the file path
    file_path = os.path.join(directory, f"{timestamp}_potential_brokenlinks.json")

    # Log the data
    logging.debug(f"Final audit data: {links_set}")

    # Save to JSON file
    with open(file_path, "w") as json_file:
        json.dump(links_set, json_file, indent=4)

    print(f"Results saved to {file_path}")

def main(domain):
    # Step 1: Discover URLs using waybackmachine_pages
    discovered_urls = waybackmachine_pages(domain, iterations=10, broken_links_only=False)
    logging.debug(f"Discovered URLs: {discovered_urls}")

    # Step 2: Check availability using requests
    urls_list = [url for url, status in discovered_urls]
    checked_urls_requests = check_availability(urls_list, access_type='requests', max_workers=10, broken_links_only=False)
    
    # Filter out URLs that failed with requests
    failed_urls = [url_info['url'] for url_info in checked_urls_requests if url_info['status'] is None]
    successful_urls = [url_info for url_info in checked_urls_requests if url_info['status'] is not None]
    
    logging.debug(f"Failed URLs with requests: {failed_urls}")
    logging.debug(f"Successful URLs with requests: {successful_urls}")

    # Step 3: Check availability using selenium for failed URLs
    if failed_urls:
        checked_urls_selenium = check_availability(failed_urls, access_type='selenium', max_workers=10, broken_links_only=False)
        successful_urls.extend(checked_urls_selenium)
        logging.debug(f"Successful URLs with selenium: {checked_urls_selenium}")

    # Step 4: Save results to JSON file
    save_to_json(domain, successful_urls)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    main(domain)
