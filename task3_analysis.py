import pandas as pd
import os
import numpy as np

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(base_dir, "data", "trends_clean.csv")

# Load CSV into DataFrame
df = pd.read_csv(file_path)

# Print shape of dataset
print("Loaded data:", df.shape)

# Print first 5 rows
print("\nFirst 5 rows:")
print(df.head())

average = df["score"].mean()
avg = df["num_comments"].mean()

print("\nAverage score   :", round(average))
print("Average comments:", round(avg))

#Basic Analysis with NumPy

print("\n--- NumPy Stats ---")

# Convert to numpy arrays
scores = df["score"].to_numpy()
comments = df["num_comments"].to_numpy()

# Mean, Median, Std
mean_score = np.mean(scores)
median_score = np.median(scores)
std_score = np.std(scores)

print("Mean score   :", round(mean_score))
print("Median score :", round(median_score))
print("Std deviation:", round(std_score))

# Max and Min
print("Max score    :", np.max(scores))
print("Min score    :", np.min(scores))

# Category with most stories
category_counts = df["category"].value_counts()
top_category = category_counts.idxmax()
top_count = category_counts.max()

print(f"\nMost stories in: {top_category} ({top_count} stories)")

# Story with most comments
max_comments_index = df["num_comments"].idxmax()
top_story = df.loc[max_comments_index]

print(f'\nMost commented story: "{top_story["title"]}" — {top_story["num_comments"]} comments')

#Add New Column

df["engagement"] = df["num_comments"] / (df["score"] + 1)
df["is_popular"] = df["score"] > average

#Save the result

output_path = os.path.join(base_dir, "data", "trends_analysed.csv")

# Create data folder if not exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Save CSV
df.to_csv(output_path, index=False)

print(f"\nSaved to {output_path}")