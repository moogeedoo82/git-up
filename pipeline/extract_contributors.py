import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import BASE_GQL
from .http import request_with_retry

CONTRIBUTORS_QUERY = """
query($owner: String!, $
ame: String!, $cursor: String) {
  repository(owner: $owner, name: $
ame) {
    mentionableUsers(first: 100, after: $cursor) {
      pageInfo { hasNextPage, endCursor }
      nodes {
        databaseId, login, name, createdAt, isSiteAdmin, __typename
      }
    }
  }
}
"""

def fetch_all_repo_contributors(owner, name):
    contributors = []
    cursor = None
    pages_fetched = 0
    MAX_PAGES = 50
    while pages_fetched < MAX_PAGES:
        variables = {"owner": owner, "name": name, "cursor": cursor}
        resp = request_with_retry("POST", BASE_GQL, is_graphql=True, json={"query": CONTRIBUTORS_QUERY, "variables": variables})
        if not resp or resp.status_code != 200:
            break
        data = resp.json().get("data", {}).get("repository", {})
        if not data or not data.get("mentionableUsers"): break
        users_data = data["mentionableUsers"]
        for node in users_data["nodes"]:
            if node and node["login"]:
                contributors.append({
                    "contributor_login": node["login"],
                    "contributor_name": node["name"],
                    "joining_date": node["createdAt"],
                    "user_id": node["databaseId"],
                    "type": "User" if node["__typename"] == "User" else "Organization",
                    "site_admin": node["isSiteAdmin"]
                })
        if not users_data.get("pageInfo", {}).get("hasNextPage"): break
        cursor = users_data["pageInfo"]["endCursor"]
        pages_fetched += 1
        time.sleep(0.1)
    return contributors

def process_repo(row, index, total):
    print(f"  [{index}/{total}] Fetching top contributors for: {row['owner']}/{row['name']}...")
    repo_contributors = fetch_all_repo_contributors(row["owner"], row["name"])
    for person in repo_contributors:
        person["repo_id"] = row["repo_id"]
    return repo_contributors

def get_contributors_and_users(repos_df):
    all_contributors_rows = []
    total_repos = len(repos_df)
    print(f"🚀 PACE RUN: Unleashing 5 Parallel Workers for {total_repos} repositories...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i, row in repos_df.iterrows():
            futures.append(executor.submit(process_repo, row, i+1, total_repos))
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    all_contributors_rows.extend(result)
            except Exception as e:
                print(f"❌ Worker error: {e}")
    contributors_df = pd.DataFrame(all_contributors_rows)
    cols = ["repo_id", "contributor_login", "user_id", "type", "site_admin"]
    contributors_df = contributors_df[cols] if not contributors_df.empty else pd.DataFrame(columns=cols)
    users_df = pd.DataFrame(all_contributors_rows)[["contributor_login", "user_id", "contributor_name", "joining_date"]].copy() if not contributors_df.empty else pd.DataFrame(columns=["login", "user_id", "contributor_name", "joining_date"])
    if not users_df.empty:
        users_df.columns = ["login", "user_id", "contributor_name", "joining_date"]
        users_df = users_df.drop_duplicates(subset=["login"])
    return contributors_df, users_df
