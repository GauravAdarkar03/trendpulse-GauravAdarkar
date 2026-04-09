# task4_visualization.py
# TrendPulse: Visualizing analysed data using Matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import os

# -----------------------------
# Step 1: Setup
# -----------------------------

# Get correct file path
base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "data", "trends_analysed.csv")

# Load data
df = pd.read_csv(file_path)

# Create outputs folder if not exists
output_dir = os.path.join(base_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)


# ----------------------------------------
# Chart 1: Top 10 Stories by Score
# ----------------------------------------

# Sort by score and take top 10
top_stories = df.sort_values(by="score", ascending=False).head(10)

# Shorten long titles (max 50 chars)
def shorten_title(title):
    return title[:50] + "..." if len(title) > 50 else title

titles = top_stories["title"].apply(shorten_title)
scores = top_stories["score"]

# Create horizontal bar chart
plt.figure()
plt.barh(titles, scores)
plt.xlabel("Score")
plt.ylabel("Story Title")
plt.title("Top 10 Stories by Score")
plt.gca().invert_yaxis()  # Highest score on top

# Save chart BEFORE showing
plt.savefig(os.path.join(output_dir, "chart1_top_stories.png"))
plt.close()


# ----------------------------------------
# Chart 2: Stories per Category
# ----------------------------------------

category_counts = df["category"].value_counts()

plt.figure()
plt.bar(category_counts.index, category_counts.values)
plt.xlabel("Category")
plt.ylabel("Number of Stories")
plt.title("Stories per Category")

# Rotate labels for readability
plt.xticks(rotation=45)

plt.savefig(os.path.join(output_dir, "chart2_categories.png"))
plt.close()


# ----------------------------------------
# Chart 3: Score vs Comments
# ----------------------------------------

# Separate popular and non-popular
popular = df[df["is_popular"] == True]
not_popular = df[df["is_popular"] == False]

plt.figure()

# Plot both groups with different colors
plt.scatter(popular["score"], popular["num_comments"], label="Popular")
plt.scatter(not_popular["score"], not_popular["num_comments"], label="Not Popular")

plt.xlabel("Score")
plt.ylabel("Number of Comments")
plt.title("Score vs Comments")
plt.legend()

plt.savefig(os.path.join(output_dir, "chart3_scatter.png"))
plt.close()


# ----------------------------------------
# Bonus: Dashboard (All charts together)
# ----------------------------------------

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Chart 1 in dashboard
axes[0].barh(titles, scores)
axes[0].set_title("Top Stories")
axes[0].invert_yaxis()

# Chart 2 in dashboard
axes[1].bar(category_counts.index, category_counts.values)
axes[1].set_title("Categories")
axes[1].tick_params(axis='x', rotation=45)

# Chart 3 in dashboard
axes[2].scatter(popular["score"], popular["num_comments"], label="Popular")
axes[2].scatter(not_popular["score"], not_popular["num_comments"], label="Not Popular")
axes[2].set_title("Score vs Comments")
axes[2].legend()

# Overall title
fig.suptitle("TrendPulse Dashboard")

# Save dashboard
plt.savefig(os.path.join(output_dir, "dashboard.png"))
plt.close()


print("All charts saved in 'outputs/' folder")