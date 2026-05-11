# GitUp - GitHub Intelligence Dashboard

Live Dashboard: https://git-up.streamlit.app

The only dashboard that tracks, ranks, and visualizes the entire GitHub ecosystem - updated every single day, automatically.

## What is GitUp?

GitUp is a fully automated data pipeline and live intelligence dashboard that tracks the top 300 GitHub repositories by stars every day.

## Features

- Rankings: Top repos ranked by stars, filterable by language and topic
- Trends: Star growth curves over time
- Contributors: Global leaderboard of top contributors
- Competition Map: Stars vs contributor count
- Timeline: Repository creation heatmap
- Auto-refresh: Data updates daily at 02:00 UTC

## Tech Stack

- Data Collection: Python, httpx, GitHub REST + GraphQL API
- Parallelism: asyncio, Semaphore(20), ThreadPoolExecutor
- Storage: Supabase (PostgreSQL) + CSV snapshots
- Dashboard: Streamlit + Plotly
- Automation: GitHub Actions (daily cron)
- Deployment: Streamlit Cloud

## Data Files

Updated daily in public_repo/data/:

- repositories.csv: Top 300 repos with stars, language, topics
- contributors.csv: All contributors per repo
- users.csv: Unique contributor profiles
- contributor_commits_lookup.csv: Commit counts per user per repo
- repo_history.csv: Daily star snapshots for trend tracking

## Roadmap

- Rising stars detector (fastest growing this week)
- Language trend analysis over time
- Repo age vs stars (find underrated repos)
- Topic clustering and semantic search
- Daily email digest of top movers
- Contributor country inference
- GitHub profile intelligence cards

---
Built with love - Data refreshed daily - Fully automated
Star this repo if you find it useful!
