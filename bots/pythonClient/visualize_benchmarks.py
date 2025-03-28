import json
import glob
import os
import matplotlib.pyplot as plt
import pandas as pd

# Path to JSON files (adjust the pattern as needed)
json_files = glob.glob("data_benchmarks_medium_10games/*.json")  # or "path/to/json_files/*.json"

# Dictionaries to store data
boxplot_data = {}   # Filename -> list of scores
state_counts = {}   # Filename -> {"died": count, "finished": count}

for file in json_files:
    with open(file, "r") as f:
        data = json.load(f)
    # Use the filename without ".json" as the label
    label = os.path.basename(file).replace(".json", "")
    
    # Extract scores for the boxplot
    scores = [entry["score"] for entry in data["play_scores"] if "score" in entry]
    boxplot_data[label] = scores
    
    # Count the player states
    died_count = sum(1 for entry in data["play_scores"] if entry.get("player_state") == "died")
    finished_count = sum(1 for entry in data["play_scores"] if entry.get("player_state") == "finished")
    state_counts[label] = {"died": died_count, "finished": finished_count}

# Create a figure with 2 subplots (vertical layout)
fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 12))

# Boxplot for the scores
axes[0].boxplot(boxplot_data.values(), labels=boxplot_data.keys())
axes[0].set_xlabel("File (Filename)")
axes[0].set_ylabel("Score")
axes[0].tick_params(axis='x', rotation=45)
axes[0].set_ylim(bottom=0)  # Set y-axis to start from 0

# Prepare data for the barplot
df = pd.DataFrame(state_counts).T.reset_index().rename(columns={"index": "File"})
x = range(len(df))
width = 0.35

# Barplot for player states
axes[1].bar(x, df["died"], width, label="died")
axes[1].bar([i + width for i in x], df["finished"], width, label="finished")
axes[1].set_xticks([i + width/2 for i in x])
axes[1].set_xticklabels(df["File"], rotation=45)
axes[1].set_xlabel("File (Filename)")
axes[1].set_ylabel("Count")
axes[1].legend()

plt.tight_layout()
plt.show()