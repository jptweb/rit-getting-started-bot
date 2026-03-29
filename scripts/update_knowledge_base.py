"""
Fetches the RIT Getting Started Google Doc, converts it to clean markdown,
and saves it as the knowledge base file.

Usage:
  python scripts/update_knowledge_base.py

Requires: markdownify, beautifulsoup4, requests
The Google Doc must be shared as "anyone with the link can view".
"""

import re
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Google Doc ID — update this if the source document changes
DOC_ID = "1oo9RQHJfQcp3FOVIqTVfg1lcJFRqvW8FxXxsekeRquo"
OUTPUT_FILE = "knowledge_rit-gettings-started-2251.md"

def fetch_doc_as_html(doc_id):
    """Export a public Google Doc as HTML."""
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def clean_google_links(soup):
    """Strip Google redirect wrappers from URLs."""
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'google.com/url' in href:
            parsed = parse_qs(urlparse(href).query)
            if 'q' in parsed:
                a['href'] = parsed['q'][0]

def html_to_markdown(html):
    """Convert Google Docs HTML to clean markdown."""
    soup = BeautifulSoup(html, 'html.parser')

    # Remove style and script tags
    for tag in soup.find_all(['style', 'script']):
        tag.decompose()

    # Clean Google redirect URLs
    clean_google_links(soup)

    # Convert to markdown
    markdown = md(str(soup), heading_style='ATX')

    # Clean up excessive blank lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return markdown

def main():
    print(f"Fetching Google Doc {DOC_ID}...")
    html = fetch_doc_as_html(DOC_ID)
    print(f"Fetched {len(html):,} bytes of HTML")

    print("Converting to markdown...")
    markdown = html_to_markdown(html)

    # Stats
    lines = markdown.split('\n')
    headings = [l for l in lines if l.startswith('# ')]
    links = re.findall(r'\[.*?\]\(.*?\)', markdown)
    print(f"Result: {len(lines)} lines, {len(headings)} sections, {len(links)} links")

    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
