from datetime import date
import pandas as pd
import os

def build_repo_history(repos_df, path):
    today = date.today().isoformat()
    new_data = pd.DataFrame({
        "repo_id": repos_df["repo_id"],
        "date": today,
        "stars": repos_df["stars"]
    })
    if os.path.exists(path):
        existing = pd.read_csv(path)
        combined = pd.concat([existing, new_data], ignore_index=True)
    else:
        combined = new_data
    combined = combined.drop_duplicates(subset=["repo_id", "date"], keep="last")
    return combined
