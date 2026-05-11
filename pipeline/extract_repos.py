import pandas as pd
from .config import BASE_REST
from .http import request_with_retry

def get_top_repos(pages=3):
    repos = []
    for page in range(1, pages + 1):
        print(f"📦 Fetching repos page {page}...")
        url = f"{BASE_REST}/search/repositories?q=stars:>10000&sort=stars&order=desc&per_page=100&page={page}"
        resp = request_with_retry("GET", url, is_graphql=False)
        if not resp or resp.status_code != 200:
            print("❌ Failed to fetch repos. Skipping page.")
            continue
        data = resp.json()
        for r in data.get("items", []):
            repos.append({
                "repo_id": r["id"],
                "name": r["name"],
                "full_name": r["full_name"],
                "owner": r["owner"]["login"],
                "url": r["html_url"],
                "stars": r["stargazers_count"],
                "created_at": r["created_at"],
                "last_modified": r["pushed_at"],
                "language": r["language"],
                "topics": ", ".join(r.get("topics", []))
            })
    return pd.DataFrame(repos)
