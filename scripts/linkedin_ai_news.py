#!/usr/bin/env python3
"""Daily LinkedIn AI News Poster — standalone version.

Fetches AI news using Google News RSS (no SearXNG or API keys needed).
Usage:
    python3 scripts/linkedin_ai_news.py                  # Fetch + show
    python3 scripts/linkedin_ai_news.py --dry-run        # Fetch + save to file
    python3 scripts/linkedin_ai_news.py --post           # Fetch + post via Interceptor
"""

import json
import sys
import os
import re
import logging
from datetime import datetime
from pathlib import Path

try:
    import httpx
except ImportError:
    os.system(f"{sys.executable} -m pip install --user --break-system-packages httpx")
    import httpx

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system(f"{sys.executable} -m pip install --user --break-system-packages beautifulsoup4")
    from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Config ──
MAX_NEWS_ITEMS = 5
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=AI+artificial+intelligence+when:1d&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=LLM+large+language+model+when:1d&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=machine+learning+breakthroughs+when:1d&hl=en-US&gl=US&ceid=US:en",
]


def fetch_ai_news() -> list[dict]:
    """Fetch AI news from Google News RSS feeds."""
    all_results = []
    seen_titles = set()

    for feed_url in RSS_FEEDS:
        try:
            response = httpx.get(feed_url, follow_redirects=True, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "xml")

            for item in soup.find_all("item")[:8]:
                title = item.find("title")
                if not title:
                    continue
                title_text = title.get_text(strip=True)

                # Deduplicate by title similarity
                title_key = re.sub(r'[^a-z0-9]', '', title_text.lower())
                if title_key in seen_titles or len(title_key) < 20:
                    continue
                seen_titles.add(title_key)

                link = item.find("link")
                source = item.find("source")

                all_results.append({
                    "title": title_text,
                    "url": link.get_text(strip=True) if link else "",
                    "source": source.get_text(strip=True) if source else "Unknown",
                })
        except Exception as e:
            logger.warning(f"RSS fetch failed for feed: {e}")

    return all_results[:MAX_NEWS_ITEMS * 2]


def format_linkedin_post(news_items: list[dict]) -> str:
    """Format news items into a LinkedIn post."""
    today = datetime.now().strftime("%B %d, %Y")
    selected = news_items[:MAX_NEWS_ITEMS]

    lines = [
        f"AI Daily Digest — {today}",
        "",
    ]

    for i, item in enumerate(selected, 1):
        title = item["title"].strip()
        source = item.get("source", "")
        source_str = f" ({source})" if source else ""
        lines.append(f"{i}. {title}{source_str}")
        lines.append("")

    lines.extend([
        "What's catching your attention in AI today?",
        "",
        "#AI #ArtificialIntelligence #MachineLearning #TechNews #LLM",
    ])

    return "\n".join(lines)


def post_to_linkedin(text: str) -> bool:
    """Post to LinkedIn via Interceptor browser automation."""
    script_path = Path(__file__).parent / "linkedin-post.sh"
    post_file = Path(__file__).parent.parent / "data" / "linkedin_post.txt"

    # Save post text
    post_file.parent.mkdir(exist_ok=True)
    post_file.write_text(text, encoding="utf-8")

    # Run the post script
    import subprocess
    result = subprocess.run(
        ["bash", str(script_path), "--post"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main():
    dry_run = "--dry-run" in sys.argv
    do_post = "--post" in sys.argv

    logger.info("Fetching AI news...")
    news = fetch_ai_news()
    if not news:
        logger.error("No news items found")
        sys.exit(1)

    logger.info(f"Found {len(news)} news items")
    post_text = format_linkedin_post(news)

    print("\n" + "=" * 60)
    print("LINKEDIN POST PREVIEW")
    print("=" * 60)
    print(post_text)
    print("=" * 60 + "\n")

    if do_post:
        success = post_to_linkedin(post_text)
        sys.exit(0 if success else 1)
    elif dry_run:
        output_path = Path(__file__).parent.parent / "data" / "linkedin_post.txt"
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(post_text, encoding="utf-8")
        logger.info(f"Post saved to {output_path}")
    else:
        logger.info("Post ready. Use --dry-run to save, or --post to publish.")


if __name__ == "__main__":
    main()
