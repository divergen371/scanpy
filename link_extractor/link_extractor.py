"""
Link Extractor Tool
"""
import argparse
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup as bs

internal_urls = set()  # To other page link on the same site.
external_urls = set()  # To other websites link


def valid_check(url: str) -> bool:
    """
    Check if the link is a valid one.
    """
    parse = urlparse(url)
    return bool(parse.netloc) & bool(parse.scheme)


def website_link_getter(url: str) -> set[str]:
    """
    Return all URLs that is found it belongs to the same site.
    """

    urls = set()
    domain_name = urlparse(url).netloc
    parsing = bs(requests.get(url).content, "html.parse")

    for a_tag in parsing.find_all("a"):
        href = a_tag.attr.get("href")
        if href == "" or href is None:
            continue  # If the href is empty.

        href = urljoin(url, href)
        parsed_href = urlparse(url, href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not valid_check(href):
            continue
        if href in internal_urls:
            continue
        if domain_name not in href:
            if href not in external_urls:
                print(f"[!] External link: {href}")
                external_urls.add(href)
            continue
        print(f"[*] Internal link: {href}")
        urls.add(href)
        internal_urls.add(href)
    return urls


def printer():
    """
    Show the number of found link.
    """
    print(f"[+] Total internal links: {len(internal_urls)}")
    print(f"[+] Total external links: {len(external_urls)}")
    print(f"[*] Total URLs: {len(internal_urls) + len(external_urls)}")


def result_store(domain: str):
    """
    Save the found link to a file.
    """
    domain_name = urlparse(domain).netloc

    with open(f"{domain_name}_internal_links.txt", "w") as int_file:
        for internal_link in internal_urls:
            print(internal_link.strip(), file=int_file)

    with open(f"{domain_name}_external_links.txt", "w") as ext_file:
        for external_link in external_urls:
            print(external_link.strip(), file=ext_file)


def crawler(url: str, max_url: int = 50):
    """
    Crawl a web site and extract all links.

    max_urls: Limit maximum number of URLs to try to crawl.
    """
    urls_visited_counter = 0
    urls_visited_counter += 1
    links = website_link_getter(url)
    for link in links:
        if urls_visited_counter > max_url:
            break
        crawler(link, max_url=max_url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Link Extractor Tool.")
    parser.add_argument(
        "url", help="URL of the site from which you want to extract the link."
    )
    parser.add_argument(
        "-m",
        "--max-url",
        help="Limit maximum number of URLs to try to crawl.",
        default=30,
        type=int,
    )

    args = parser.parse_args()
    url = args.url
    max_urls = args.max_urls

    crawler(url, max_urls)
    printer()
    result_store(url)
