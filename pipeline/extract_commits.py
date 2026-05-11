import pandas as pd
import asyncio
import os
from datetime import datetime
from .config import BASE_GQL
from .http import request_async, rotator
from .load import save_to_supabase

COMMIT_GQL_QUERY = """
query($login: String!, $epo_id: ID!) {
  user(login: $login) {
    contributionsCollection(repositoryID: $epo_id) {
      commitContributionsByRepository {
        repository { id }
        contributions { totalCount }
      }
    }
  }
}
"""

async def fetch_commits_one(row, sem):
    async with sem:
        login = row["contributor_login"]
        repo_id = row["repo_id"]
        try:
            resp = await request_async(
                "POST", BASE_GQL,
                json={"query": COMMIT_GQL_QUERY, "variables": {"login": login, "repo_id": repo_id}},
                is_graphql=True
            )
            if resp and resp.status_code == 200:
                data = resp.json().get("data", {}) or {}
                user = data.get("user") or {}
                collections = (
                    user.get("contributionsCollection", {})
                        .get("commitContributionsByRepository", [])
                )
                count = collections[0]["contributions"]["totalCount"] if collections else 1
            else:
                count = 1
        except Exception:
            count = 1
        return {
            "user_id": int(row["user_id"]),
            "repo_id": str(row["repo_id"]),
            "exact_contributions": int(count)
        }

async def _run_all(df, output_path, total_rows_overall, processed_count):
    sem = asyncio.Semaphore(20)
    tasks = [fetch_commits_one(row, sem) for _, row in df.iterrows()]
    results = []
    current_completed = processed_count
    BATCH = 500
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        current_completed += 1
        if len(results) >= BATCH:
            batch_df = pd.DataFrame(results)
            save_to_supabase("contributor_commits", batch_df)
            batch_df.to_csv(output_path, mode="a", header=not os.path.exists(output_path), index=False)
            now = datetime.now().strftime("%H:%M:%S")
            token_num = rotator.current_index + 1
            print(f"⚡ FAST SYNC: Token {token_num} | {current_completed}/{total_rows_overall} rows @ {now}")
            results = []
    if results:
        batch_df = pd.DataFrame(results)
        save_to_supabase("contributor_commits", batch_df)
        batch_df.to_csv(output_path, mode="a", header=not os.path.exists(output_path), index=False)
        now = datetime.now().strftime("%H:%M:%S")
        print(f"⚡ FAST SYNC: {current_completed}/{total_rows_overall} rows @ {now}")

def update_commit_counts():
    input_path = "public_repo/data/contributors.csv"
    output_path = "public_repo/data/contributor_commits_lookup.csv"
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found!")
        return
    df = pd.read_csv(input_path)
    total_rows_overall = len(df)
    processed_count = 0
    if os.path.exists(output_path):
        done_df = pd.read_csv(output_path)
        processed_count = len(done_df)
        df["key"] = df["user_id"].astype(str) + "_" + df["repo_id"].astype(str)
        done_df["key"] = done_df["user_id"].astype(str) + "_" + done_df["repo_id"].astype(str)
        df = df[~df["key"].isin(done_df["key"])].drop(columns=["key"])
        print(f"🔄 RESUME: {processed_count} done. {len(df)} remaining.")
    if df.empty:
        print("✅ All commits already extracted!")
        return
    print(f"🚀 ASYNC RUN: {len(df)} rows with semaphore(20)")
    asyncio.run(_run_all(df, output_path, total_rows_overall, processed_count))
    print(f"✅ MISSION COMPLETE: {total_rows_overall} total rows.")

if __name__ == "__main__":
    update_commit_counts()
