import os
import json
import sys
from datetime import datetime
from waybackmachine_site_pages import waybackmachine_pages, display_urls
import logging

# Configure logging to output to both console and a log file
log_file = f"log_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
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
        links_set (set): The set of tuples containing URLs and their status codes.
    """
    # Ensure the directory exists
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    directory = f"audits/{domain}"
    os.makedirs(directory, exist_ok=True)

    # Create the file path
    file_path = os.path.join(directory, f"{timestamp}_potential_brokenlinks.json")

    # Prepare data to be saved
    data = [{"url": url, "status": status} for url, status in links_set]
    
    # Log the data
    logging.debug(f"Final audit data: {data}")

    # Save to JSON file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"Results saved to {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    broken_links = waybackmachine_pages(domain, iterations=1, broken_links_only=True)
    
    # Optionally, display URLs
    # display_urls(broken_links)
    
    # Save results to JSON file
    save_to_json(domain, broken_links)
