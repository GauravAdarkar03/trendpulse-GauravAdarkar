#TASK 1 — Fetch Reddit Data (JSON)
#What to do:
#Use Reddit API (no auth needed for basic)
#Fetch trending posts from a subreddit like:
#r/india
#r/worldnews
#r/technology

import requests
import json

url = "https://www.reddit.com/r/india/top.json?limit=50"
headers = {"User-Agent": "trendpulse-app"}

response = requests.get(url, headers=headers)
data = response.json()

posts = []

for post in data["data"]["children"]:
    posts.append({
        "title": post["data"]["title"],
        "score": post["data"]["score"],
        "author": post["data"]["author"],
        "comments": post["data"]["num_comments"]
    })

with open("data/raw_data.json", "w") as f:
    json.dump(posts, f, indent=4)
