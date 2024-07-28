#     broken_links_history.py

from get_history import get_wayback_urls, filter_urls
from availability_checker import check_availability

def get_wayback_uls(domain):
    urls_df = get_wayback_urls(domain)
    filtered_urls_df = filter_urls(urls_df)

    # Display filtered URLs
    if not filtered_urls_df.empty:
        urls = filtered_urls_df["original"].tolist()
        live_urls, broken_urls = check_availability(urls)

        print("Live URLs:")
        for url in live_urls:
            print(url)

        print("\nBroken URLs:")
        for url in broken_urls:
            print(url)
    else:
        print("No contentful URLs found.")

# Example usage
if __name__ == "__main__":
    domain = "marketividade.com"
    get_wayback_uls(domain)
