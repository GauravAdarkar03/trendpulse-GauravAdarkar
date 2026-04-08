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

# task2_clean_data.py
# TrendPulse: Clean raw JSON into tidy CSV

import pandas as pd, json, os

# --- Step 1: Load JSON file ---
base_dir = os.path.dirname(os.path.abspath(__file__))
fname = os.path.join(base_dir, "data", "trends_20260408.json") 
with open(fname) as f:
    raw = json.load(f)

print(os.listdir("data"))

df = pd.DataFrame(raw)
print(f"Loaded {len(df)} stories from {fname}")

# --- Step 2: Clean the Data ---

# Remove duplicates by post_id
df = df.drop_duplicates(subset="post_id")
print("After removing duplicates:", len(df))

# Drop rows with missing post_id, title, or score
df = df.dropna(subset=["post_id","title","score"])
print("After removing nulls:", len(df))

# Ensure score and num_comments are integers
df["score"] = df["score"].astype(int)
df["num_comments"] = df["num_comments"].astype(int)

# Remove low quality (score < 5)
df = df[df["score"] >= 5]
print("After removing low scores:", len(df))

# Strip whitespace from titles
df["title"] = df["title"].str.strip()

# --- Step 3: Save as CSV ---
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")

os.makedirs(data_dir, exist_ok=True)

out = os.path.join(data_dir, "trends_clean.csv")

df.to_csv(out, index=False)

print(f"Saved to: {out}")

# Quick summary: stories per category
print("Stories per category:")
print(df["category"].value_counts())


# task3_analysis.py
# TrendPulse:Analyse cleaned data with Pandas + NumPy

import pandas as pd, numpy as np, os

# Step 1: Load and Explore
base_dir = os.path.dirname(os.path.abspath(__file__))
fname = os.path.join(base_dir, "data", "trends_clean.csv") 
##fname = "data/trends_clean.csv"
df = pd.read_csv(fname)
print(f"Loaded data: {df.shape}\n")

print("First 5 rows:")
print(df.head(), "\n")

print("Average score   :", df["score"].mean())
print("Average comments:", df["num_comments"].mean())

# Step 2: Basic Analysis with NumPy
scores = df["score"].values

print("\n--- NumPy Stats ---")
print("Mean score   :", np.mean(scores))
print("Median score :", np.median(scores))
print("Std deviation:", np.std(scores))
print("Max score    :", np.max(scores))
print("Min score    :", np.min(scores))

# Category with most stories
cat_counts = df["category"].value_counts()
top_cat = cat_counts.idxmax()
print(f"\nMost stories in: {top_cat} ({cat_counts.max()} stories)")

# Story with most comments
top_story = df.loc[df["num_comments"].idxmax()]
print(f"\nMost commented story: \"{top_story['title']}\" — {top_story['num_comments']} comments")

# Step 3: Add New Columns
avg_score = df["score"].mean()
df["engagement"] = df["num_comments"] / (df["score"] + 1)
df["is_popular"] = df["score"] > avg_score

# Step 4: Save Result
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
os.makedirs(data_dir, exist_ok=True)

out = os.path.join(data_dir, "trends_analysed.csv")

df.to_csv(out, index=False)

print(f"Saved to: {out}")

# task4_visualise.py
# TrendPulse: Make charts from analysed data

import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.patches as mpatches

# Step 1: Setup
base_dir = os.path.dirname(os.path.abspath(__file__))
fname = os.path.join(base_dir, "data", "trends_analysed.csv")

df = pd.read_csv(fname)

# Create outputs folder safely
output_dir = os.path.join(base_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)

# Step 2: Chart 1 - Top 10 Stories by Score
top10 = df.nlargest(10, "score")

titles = [t[:50] + "..." if len(t) > 50 else t for t in top10["title"]]

plt.figure(figsize=(10,6))
plt.barh(titles[::-1], top10["score"][::-1])
plt.xlabel("Score")
plt.ylabel("Story Title")
plt.title("Top 10 Stories by Score")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "chart1_top_stories.png"))
plt.close()

# Step 3: Chart 2 - Stories per Category
cat_counts = df["category"].value_counts()

plt.figure(figsize=(8,6))
plt.bar(cat_counts.index, cat_counts.values)
plt.xlabel("Category")
plt.ylabel("Number of Stories")
plt.title("Stories per Category")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "chart2_categories.png"))
plt.close()

# Step 4: Chart 3 - Score vs Comments
colors = df["is_popular"].map({True:"green", False:"red"})

plt.figure(figsize=(8,6))
plt.scatter(df["score"], df["num_comments"], c=colors)
plt.xlabel("Score")
plt.ylabel("Number of Comments")
plt.title("Score vs Comments")

# Correct legend
green_patch = mpatches.Patch(color='green', label='Popular')
red_patch = mpatches.Patch(color='red', label='Not Popular')
plt.legend(handles=[green_patch, red_patch])

plt.tight_layout()
plt.savefig(os.path.join(output_dir, "chart3_scatter.png"))
plt.close()

# Bonus Dashboard
fig, axes = plt.subplots(1, 3, figsize=(18,6))

axes[0].barh(titles[::-1], top10["score"][::-1])
axes[0].set_title("Top 10 by Score")

axes[1].bar(cat_counts.index, cat_counts.values)
axes[1].set_title("Stories per Category")

axes[2].scatter(df["score"], df["num_comments"], c=colors)
axes[2].set_title("Score vs Comments")

fig.suptitle("TrendPulse Dashboard", fontsize=16)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "dashboard.png"))
plt.close()

print("Charts saved in outputs/ folder:")
print(" - chart1_top_stories.png")
print(" - chart2_categories.png")
print(" - chart3_scatter.png")
print(" - dashboard.png")