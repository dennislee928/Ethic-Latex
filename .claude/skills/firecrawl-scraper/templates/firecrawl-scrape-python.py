#!/usr/bin/env python3
"""
Firecrawl Basic Scraping Example (Python) - v4 API

This template demonstrates how to scrape a single webpage using Firecrawl v4 API.

Requirements:
    pip install firecrawl-py python-dotenv

Environment Variables:
    FIRECRAWL_API_KEY - Your Firecrawl API key (get from https://www.firecrawl.dev)

Usage:
    python firecrawl-scrape-python.py
"""

import os
from dotenv import load_dotenv
from firecrawl import Firecrawl

# Load environment variables from .env file
load_dotenv()


def scrape_single_page(url: str):
    """
    Scrape a single webpage and return markdown content.

    Args:
        url: The URL to scrape

    Returns:
        Document object with markdown, html, metadata attributes
    """
    # Initialize Firecrawl client
    # NEVER hardcode API keys! Always use environment variables
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable not set")

    app = Firecrawl(api_key=api_key)

    try:
        # Scrape the URL - returns Pydantic Document object
        doc = app.scrape(
            url=url,
            # Output formats - can include multiple
            formats=["markdown", "html"],
            # Only extract main content (removes nav, footer, ads)
            # This saves credits and improves content quality
            only_main_content=True,
            # Remove base64 images to reduce response size
            remove_base64_images=True,
            # Wait time before scraping (ms) - useful for dynamic content
            # wait_for=3000,
            # Include screenshot
            # formats=["markdown", "screenshot"],
        )

        return doc

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        raise


def main():
    """Main function demonstrating basic scraping."""

    # Example URL to scrape
    url = "https://docs.firecrawl.dev"

    print(f"Scraping: {url}")

    # Scrape the page
    doc = scrape_single_page(url)

    # Access different parts of the result via attributes (not dict.get())
    markdown = doc.markdown or ""
    html = doc.html or ""
    metadata = doc.metadata

    # Print results
    print("\n" + "=" * 80)
    print("MARKDOWN CONTENT:")
    print("=" * 80)
    print(markdown[:500] if markdown else "No markdown content")  # First 500 characters
    print("...")

    print("\n" + "=" * 80)
    print("METADATA:")
    print("=" * 80)
    if metadata:
        print(f"Title: {getattr(metadata, 'title', 'N/A')}")
        print(f"Description: {getattr(metadata, 'description', 'N/A')}")
        print(f"Language: {getattr(metadata, 'language', 'N/A')}")
        print(f"Source URL: {getattr(metadata, 'source_url', 'N/A')}")

    # Save to file (optional)
    output_file = "scraped_content.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"\n✅ Full content saved to: {output_file}")


if __name__ == "__main__":
    main()
