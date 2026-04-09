# task1_data_collection.py
# TrendPulse — Task 1: Fetch trending stories from HackerNews API
# Fetches top 500 stories, categorises them by keyword, saves to JSON

import requests
import json
import os
import time
from datetime import datetime

# --- Configuration ---

HEADERS = {"User-Agent": "TrendPulse/1.0"}
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
STORY_URL       = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
MAX_IDS         = 500   # how many story IDs to pull from the top list
MAX_PER_CATEGORY = 25   # cap per category

# Keywords used to assign each story to a category (case-insensitive match)
CATEGORIES = {
    "technology":    ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment": ["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"],
}

# --- Step 1: Fetch the top 500 story IDs ---

def fetch_top_ids():
    """Fetch the list of top story IDs from HackerNews and return the first MAX_IDS."""
    print("Fetching top story IDs...")
    try:
        response = requests.get(TOP_STORIES_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        all_ids = response.json()
        print(f"  Retrieved {len(all_ids)} total IDs. Using first {MAX_IDS}.")
        return all_ids[:MAX_IDS]
    except requests.RequestException as e:
        print(f"  Failed to fetch story IDs: {e}")
        return []

# --- Step 2: Fetch a single story's details by ID ---

def fetch_story(story_id):
    """Fetch a single story object from HackerNews. Returns None if the request fails."""
    url = STORY_URL.format(id=story_id)
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"  Could not fetch story {story_id}: {e}")
        return None

# --- Step 3: Assign a category based on keywords in the title ---

def assign_category(title):
    """
    Check the story title against each category's keyword list.
    Returns the first matching category, or None if no keywords match.
    """
    title_lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return None  # story doesn't fit any category

# --- Step 4: Main collection loop ---

def collect_stories(story_ids):
    """
    Loop through story IDs, fetch each one, assign a category,
    and collect up to MAX_PER_CATEGORY stories per category.
    Sleeps 2 seconds each time a category reaches its limit.
    """
    # Track how many stories we have per category
    counts     = {cat: 0 for cat in CATEGORIES}
    collected  = []
    now        = datetime.now().isoformat()  # timestamp added to every record

    print("\nCollecting stories...")

    for story_id in story_ids:

        # Stop early if every category is full
        if all(count >= MAX_PER_CATEGORY for count in counts.values()):
            print("  All categories full. Stopping early.")
            break

        story = fetch_story(story_id)

        # Skip if the request failed, the story has no title, or it's not a regular story
        if not story:
            continue
        if story.get("type") != "story":
            continue
        title = story.get("title", "").strip()
        if not title:
            continue

        category = assign_category(title)

        # Skip if we can't categorise it, or that category is already full
        if category is None:
            continue
        if counts[category] >= MAX_PER_CATEGORY:
            continue

        # Build the record with exactly the 7 required fields
        record = {
            "post_id":      story.get("id"),
            "title":        title,
            "category":     category,
            "score":        story.get("score", 0),
            "num_comments": story.get("descendants", 0),
            "author":       story.get("by", "unknown"),
            "collected_at": now,
        }

        collected.append(record)
        counts[category] += 1

        # Sleep 2 seconds each time a category hits its limit
        if counts[category] == MAX_PER_CATEGORY:
            print(f"  Category '{category}' full ({MAX_PER_CATEGORY} stories). Sleeping 2s...")
            time.sleep(2)

    return collected

# --- Step 5: Save to a dated JSON file in data/ ---

def save_to_json(stories):
    """Create the data/ folder if needed and save all collected stories as JSON."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    date_str  = datetime.now().strftime("%Y%m%d")
    filename = os.path.join(data_dir, f"trends_{date_str}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2, ensure_ascii=False)

    return filename

# --- Entry point ---

if __name__ == "__main__":
    ids      = fetch_top_ids()
    stories  = collect_stories(ids)
    filepath = save_to_json(stories)

    print(f"\nCollected {len(stories)} stories. Saved to {filepath}")

