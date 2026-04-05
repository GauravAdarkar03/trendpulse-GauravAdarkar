
#TASK 4 — Visualization (Matplotlib)
#Charts to create:
#Bar chart → Top 10 posts
#Histogram → Score distribution


import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/clean_data.csv")

top10 = df.sort_values(by="score", ascending=False).head(10)

plt.figure()
plt.barh(top10["title"], top10["score"])
plt.xlabel("Score")
plt.title("Top 10 Reddit Posts")
plt.show()
