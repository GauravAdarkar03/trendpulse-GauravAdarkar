# task2_data_processing.py
# TrendPulse - Task 2: Clean the data and save as CSV

import pandas as pd
import os

# Step 1: Locate the JSON file
# Get current script directory so paths work everywhere
base_dir = os.path.dirname(os.path.abspath(__file__))

# Change filename according to your Task 1 output
file_name = "trends_20260408.json"
file_path = os.path.join(base_dir, "data", file_name)

# Step 2: Load JSON into DataFrame
df = pd.read_json(file_path)

print(f"Loaded {len(df)} stories from {file_path}")

# -------------------------------
# Step 3: Clean the Data
# -------------------------------

# 1. Remove duplicate posts based on post_id
df = df.drop_duplicates(subset="post_id")
print(f"After removing duplicates: {len(df)}")

# 2. Remove rows with missing important fields
df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")

# 3. Fix data types (convert to integers)
df["score"] = df["score"].astype(int)
df["num_comments"] = df["num_comments"].astype(int)

# 4. Remove low-quality posts (score < 5)
df = df[df["score"] >= 5]
print(f"After removing low scores: {len(df)}")

# 5. Remove extra whitespace from titles
df["title"] = df["title"].str.strip()

# -------------------------------
# Step 4: Save cleaned data
# -------------------------------

output_path = os.path.join(base_dir, "data", "trends_clean.csv")

# Create data folder if not exists
os.makedirs(os.path.join(base_dir, "data"), exist_ok=True)

df.to_csv(output_path, index=False)

print(f"\nSaved {len(df)} rows to {output_path}")

# -------------------------------
# Step 5: Summary (stories per category)
# -------------------------------

print("\nStories per category:")

if "category" in df.columns:
    print(df["category"].value_counts())
else:
    print("No category column found in dataset")