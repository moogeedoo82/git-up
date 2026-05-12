# ⬆ GitUp Arena — GitHub Intelligence Dashboard

[![Live Arena](https://img.shields.io/badge/🚀_Live_Arena-moogeedoo82.github.io/git--up-58a6ff?style=for-the-badge&labelColor=0d1117)](https://moogeedoo82.github.io/git-up)
[![Python](https://img.shields.io/badge/Python-3.11-58a6ff?style=for-the-badge&labelColor=0d1117&logo=python&logoColor=white)](https://python.org)
[![Updated Daily](https://img.shields.io/badge/Data-Updated_Daily-3fb950?style=for-the-badge&labelColor=0d1117)](https://moogeedoo82.github.io/git-up)

> The only dashboard that tracks, ranks, and visualizes the entire GitHub ecosystem — updated every single day, fully automatically.

## 🔴 [→ Open Live Dashboard](https://moogeedoo82.github.io/git-up)

---

## Features
- 🏎️ **Repo Race** — animated bar race, sortable by stars, age, language
- 🌍 **Star Network** — interactive D3 force graph of languages and repos
- 👑 **Hall of Fame** — top contributors across all 300 repos
- 🗓 **Age vs Stars** — discover young repos punching above their weight
- ⚡ **Daily Drama** — the stories behind the numbers, updated daily

## Tech Stack
- Data: Python · httpx · GitHub REST + GraphQL API
- Storage: Supabase + CSV snapshots
- Automation: GitHub Actions (daily at 02:00 UTC · no laptop needed)
- Visualization: D3.js · Pure HTML/CSS/JS

## Data (updated daily)
| File | Description |
|---|---|
| repositories | Top 300 repos with stars, language, topics |
| contributors | All contributors per repo |
| users | Unique contributor profiles |
| repo_history | Daily star snapshots for trend tracking |

---
Built with love · Fully automated · Star this repo if you find it useful! ⭐
