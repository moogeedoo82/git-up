import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import BASE_REST
from .http import request_with_retry

def fetch_all_repo_contributors(owner, name, repo_id):
    contributors = []
    page = 1
    while page <= 5:
        url = f"{BASE_REST}/repos/{owner}/{name}/contributors?per_page=100&page={page}&anon=false"
        resp = request_with_retry("GET", url, is_graphql=False)
        if not resp or resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        for user in data:
            if user.get("type") == "User":
                contributors.append({
                    "repo_id": repo_id,
                    "contributor_login": user["login"],
                    "user_id": user["id"],
                    "type": user["type"],
                    "site_admin": user.get("site_admin", False),
                    "contributor_name": user.get("name", user["login"]),
                    "joining_date": None
                })
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.2)
    return contributors

def process_repo(row, index, total):
    print(f"  [{index}/{total}] Fetching contributors for: {row['owner']}/{row['name']}...")
    return fetch_all_repo_contributors(row["owner"], row["name"], row["repo_id"])

def get_contributors_and_users(repos_df):
    all_contributors_rows = []
    total_repos = len(repos_df)
    print(f"🚀 Fetching contributors for {total_repos} repositories...")
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

    if not all_contributors_rows:
        cols = ["repo_id","contributor_login","user_id","type","site_admin"]
        return pd.DataFrame(columns=cols), pd.DataFrame(columns=["user_id","login","contributor_name","joining_date"])

    contributors_df = pd.DataFrame(all_contributors_rows)[["repo_id","contributor_login","user_id","type","site_admin"]]
    users_df = pd.DataFrame(all_contributors_rows)[["user_id","contributor_login","contributor_name","joining_date"]].drop_duplicates(subset=["user_id"])
    users_df.columns = ["user_id","login","contributor_name","joining_date"]
    return contributors_df, users_df
