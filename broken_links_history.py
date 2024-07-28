# broken_links_history.py

from get_history import get_wayback_urls, filter_urls
from availability_checker import check_availability
import time

def get_wayback_uls(domain, iterations=10):
    broken_links_set = set()

    for i in range(iterations):
        urls_df = get_wayback_urls(domain)
        filtered_urls_df = filter_urls(urls_df)

        if not filtered_urls_df.empty:
            urls = filtered_urls_df["original"].tolist()
            live_urls, broken_urls = check_availability(urls)
            print(f"broken_urls found:{broken_urls}")
            # Add broken URLs to the set
            broken_links_set.update(broken_urls)

            print(f"Iteration {i + 1}/{iterations} completed.")
            time.sleep(1)  # Adding a delay to avoid overwhelming the server
        else:
            print("No contentful URLs found.")
            break

    # Display broken URLs
    if broken_links_set:
        print("\nBroken URLs:")
        for url in broken_links_set:
            print(url)
    else:
        print("No broken URLs found.")

    return broken_links_set

# Example usage
if __name__ == "__main__":
    domain = "example.com"
    get_wayback_uls(domain)
