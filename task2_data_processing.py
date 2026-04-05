#TASK 2 — Clean Data (Pandas → CSV)
# What to do:
#Load JSON
#Remove missing/null values
#Convert into DataFrame
#Save as CSV

import pandas as pd
import os

print("Current directory:", os.getcwd())
print("Files in data folder:", os.listdir("data") if os.path.exists("data") else "No data folder")

df = pd.read_json("data/raw_data.json")

# Cleaning
df = df.dropna()
df = df[df["score"] > 0]

df.to_csv("data/clean_data.csv", index=False)
