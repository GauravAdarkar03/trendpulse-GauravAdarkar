
#TASK 3 — Analyse Data (NumPy + Pandas)
#What to analyse:
#Average score
#Most commented post
#Top 5 posts

import pandas as pd
import numpy as np

df = pd.read_csv("data/clean_data.csv")

print("Average Score:", np.mean(df["score"]))

top_post = df.loc[df["score"].idxmax()]
print("Top Post:", top_post["title"])

top5 = df.sort_values(by="score", ascending=False).head(5)
print(top5)
