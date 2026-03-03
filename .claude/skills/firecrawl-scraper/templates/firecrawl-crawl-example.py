#!/usr/bin/env python3
"""
Firecrawl Crawling Example (Python) - v4 API

This template demonstrates how to crawl multiple pages using Firecrawl v4 API.

Requirements:
    pip install firecrawl-py python-dotenv

Environment Variables:
    FIRECRAWL_API_KEY - Your Firecrawl API key (get from https://www.firecrawl.dev)

Usage:
    python firecrawl-crawl-example.py
"""

import os
from dotenv import load_dotenv
from firecrawl import Firecrawl

# Load environment variables from .env file
load_dotenv()


def crawl_site(url: str, limit: int = 10):
    """
    Crawl a website and return all pages.

    Args:
        url: Starting URL to crawl
        limit: Maximum number of pages to crawl

    Returns:
        CrawlResult object with data attribute containing list of Document objects
    """
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")

    app = Firecrawl(api_key=api_key)

    print(f"Starting crawl from: {url}")
    print(f"Limit: {limit} pages")

    try:
        # Start crawl - returns Pydantic CrawlResult object
        result = app.crawl(
            url=url,
            limit=limit,
            scrape_options={
                "formats": ["markdown"],
                "only_main_content": True,
            },
            # max_depth=2,  # Optional: limit crawl depth
            # allowed_domains=["docs.example.com"],  # Optional: restrict domains
            # exclude_paths=["/blog/*"],  # Optional: exclude patterns
        )

        return result

    except Exception as e:
        print(f"Error crawling {url}: {e}")
        raise


def main():
    """Main function demonstrating site crawling."""

    # Example: Crawl Firecrawl documentation
    url = "https://docs.firecrawl.dev"

    # Crawl the site (limit to 5 pages for demo)
    result = crawl_site(url, limit=5)

    print("\n" + "=" * 80)
    print("CRAWL RESULTS:")
    print("=" * 80)

    # result.data is a list of Document objects
    if result.data:
        print(f"\nTotal pages crawled: {len(result.data)}")

        for i, page in enumerate(result.data, 1):
            metadata = page.metadata
            source_url = getattr(metadata, "source_url", "Unknown URL") if metadata else "Unknown URL"
            title = getattr(metadata, "title", "No title") if metadata else "No title"
            content_length = len(page.markdown) if page.markdown else 0

            print(f"\n[{i}] {title}")
            print(f"    URL: {source_url}")
            print(f"    Content: {content_length:,} chars")

            # Save each page
            safe_filename = f"crawled_{i}.md"
            with open(safe_filename, "w", encoding="utf-8") as f:
                f.write(page.markdown or "")
            print(f"    Saved: {safe_filename}")
    else:
        print("No pages crawled")

    print("\n✅ Crawl complete!")


if __name__ == "__main__":
    main()
