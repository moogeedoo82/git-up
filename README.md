# ⬆ GitUp Arena — GitHub Intelligence Dashboard

## 🚀 [LIVE DASHBOARD → moogeedoo82.github.io/git-up](https://moogeedoo82.github.io/git-up)

> Real-time rankings, races, and contributor intelligence for the top 300 GitHub repositories — updated every day automatically.

---

### What's inside the Arena:
- 🏎️ Repo Race — animated bar race, sortable by stars, age, language
- 🌍 Star Network — interactive D3 force graph of languages and repos
- 👑 Hall of Fame — top contributors across all 300 repos
- 🗓 Age vs Stars — discover young repos punching above their weight
- ⚡ Daily Drama — the stories behind the numbers, updated daily

### Tech Stack
- Data: Python · httpx · GitHub REST + GraphQL API
- Storage: Supabase + CSV snapshots in this repo
- Automation: GitHub Actions (daily at 02:00 UTC)
- Visualization: D3.js · Pure HTML/CSS/JS
- Backup: Google Drive via rclone

### Data updated daily in public_repo/data/
- repositories.csv · contributors.csv · users.csv · repo_history.csv

---
Built with love · Fully automated · No laptop needed
