import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import os
from datetime import datetime

st.set_page_config(
    page_title="GitUp · GitHub Intelligence",
    page_icon="⬆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.metric-card { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 1.25rem 1.5rem; text-align: center; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: #58a6ff; line-height: 1; }
.metric-label { font-size: 0.7rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.4rem; }
.section-title { font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.1em; border-bottom: 1px solid #21262d; padding-bottom: 0.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    try:
        if url and key:
            sb = create_client(url, key)
            repos = pd.DataFrame(sb.table("repositories").select("*").execute().data)
            contributors = pd.DataFrame(sb.table("contributors").select("*").execute().data)
            users = pd.DataFrame(sb.table("users").select("*").execute().data)
            commits = pd.DataFrame(sb.table("contributor_commits").select("*").execute().data)
            history = pd.DataFrame(sb.table("repo_history").select("*").execute().data)
        else:
            raise ValueError("No Supabase creds")
    except Exception:
        base = "data"
        repos        = pd.read_csv(f"{base}/repositories.csv")
        contributors = pd.read_csv(f"{base}/contributors.csv")
        users        = pd.read_csv(f"{base}/users.csv")
        commits      = pd.read_csv(f"{base}/contributor_commits_lookup.csv")
        history      = pd.read_csv(f"{base}/repo_history.csv")
    for df in [repos, contributors, users, commits, history]:
        df.columns = df.columns.str.strip()
    if "created_at" in repos.columns:
        repos["created_at"] = pd.to_datetime(repos["created_at"], errors="coerce")
    if "date" in history.columns:
        history["date"] = pd.to_datetime(history["date"], errors="coerce")
    if "stars" in history.columns:
        history["stars"] = pd.to_numeric(history["stars"], errors="coerce")
    return repos, contributors, users, commits, history

repos, contributors, users, commits, history = load_data()

with st.sidebar:
    st.markdown("### Filters")
    languages = ["All"] + sorted(repos["language"].dropna().unique().tolist())
    lang_filter = st.selectbox("Language", languages)
    star_min = st.slider("Min stars (k)", 10, 100, 10) * 1000
    top_n = st.slider("Top N repos", 10, 100, 25)

filtered = repos.copy()
if lang_filter != "All":
    filtered = filtered[filtered["language"] == lang_filter]
filtered = filtered[filtered["stars"] >= star_min].nlargest(top_n, "stars")

st.markdown('<div style="background:#0d1117;padding:1.5rem 2rem 1rem;border-bottom:1px solid #21262d;margin:-4rem -4rem 2rem;display:flex;align-items:baseline;gap:1rem"><span style="font-family:Space Mono,monospace;font-size:1.5rem;font-weight:700;color:#58a6ff">⬆ GitUp</span><span style="font-size:0.75rem;color:#8b949e;text-transform:uppercase;letter-spacing:.05em">GitHub Intelligence · Rankings · Trends · Contributors</span></div>', unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
def metric_card(col, value, label):
    col.markdown(f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

metric_card(k1, f"{len(repos):,}", "Repos tracked")
metric_card(k2, f"{repos['stars'].sum()/1e6:.1f}M", "Total stars")
metric_card(k3, f"{len(users):,}", "Contributors")
metric_card(k4, f"{repos['language'].nunique()}", "Languages")
metric_card(k5, datetime.now().strftime("%b %d"), "Last update")

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2])
with col_left:
    st.markdown('<div class="section-title">🏆 Top Repositories</div>', unsafe_allow_html=True)
    display = filtered[["name","owner","stars","language"]].copy()
    display.insert(0, "rank", range(1, len(display)+1))
    display["stars"] = display["stars"].apply(lambda x: f"{x/1000:.1f}k")
    display["language"] = display["language"].fillna("—")
    st.dataframe(display.rename(columns={"rank":"#","name":"Repository","owner":"Owner","stars":"⭐ Stars","language":"Language"}), use_container_width=True, height=400, hide_index=True)

with col_right:
    st.markdown('<div class="section-title">🌐 Language Distribution</div>', unsafe_allow_html=True)
    lang_counts = repos["language"].fillna("Other").value_counts().head(12)
    fig_lang = px.pie(values=lang_counts.values, names=lang_counts.index, hole=0.55, color_discrete_sequence=px.colors.qualitative.G10)
    fig_lang.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#8b949e", margin=dict(l=0,r=0,t=0,b=0), height=380)
    st.plotly_chart(fig_lang, use_container_width=True)

st.markdown('<div class="section-title">📈 Star Growth Trends</div>', unsafe_allow_html=True)
if not history.empty and "date" in history.columns:
    top10_ids = repos.nlargest(10,"stars")["repo_id"].tolist()
    top10_names = repos[repos["repo_id"].isin(top10_ids)][["repo_id","name"]]
    hist_top = history[history["repo_id"].isin(top10_ids)].merge(top10_names, on="repo_id")
    fig_trend = px.line(hist_top, x="date", y="stars", color="name", color_discrete_sequence=px.colors.qualitative.Plotly)
    fig_trend.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#8b949e", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#21262d"), margin=dict(l=0,r=0,t=0,b=0), height=300, hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("Star history will appear after the second daily run.")

col3a, col3b = st.columns(2)
with col3a:
    st.markdown('<div class="section-title">👥 Top Contributors</div>', unsafe_allow_html=True)
    if not commits.empty and not users.empty:
        top_contributors = commits.groupby("user_id")["exact_contributions"].sum().reset_index().merge(users[["user_id","login","contributor_name"]], on="user_id", how="left").nlargest(15,"exact_contributions")
        top_contributors["display_name"] = top_contributors["contributor_name"].fillna(top_contributors["login"])
        fig_contrib = px.bar(top_contributors, x="exact_contributions", y="display_name", orientation="h", color="exact_contributions", color_continuous_scale=["#1f3a56","#58a6ff"])
        fig_contrib.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#8b949e", coloraxis_showscale=False, margin=dict(l=0,r=0,t=0,b=0), height=350, yaxis=dict(autorange="reversed"), xaxis=dict(showgrid=True,gridcolor="#21262d"))
        st.plotly_chart(fig_contrib, use_container_width=True)

with col3b:
    st.markdown('<div class="section-title">⚡ Stars vs Contributors</div>', unsafe_allow_html=True)
    if not contributors.empty:
        contrib_count = contributors.groupby("repo_id").size().reset_index(name="contributor_count")
        scatter_df = filtered.merge(contrib_count, on="repo_id", how="left").dropna(subset=["contributor_count"])
        fig_scatter = px.scatter(scatter_df, x="contributor_count", y="stars", size="stars", color="language", hover_name="name", size_max=30, color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#8b949e", xaxis=dict(showgrid=True,gridcolor="#21262d"), yaxis=dict(showgrid=True,gridcolor="#21262d"), margin=dict(l=0,r=0,t=0,b=0), height=350)
        st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown(f'<div style="text-align:center;color:#8b949e;font-size:0.7rem;margin-top:3rem;border-top:1px solid #21262d;padding-top:1rem;font-family:Space Mono,monospace">GitUp · Data refreshed daily · {len(repos):,} repos · {len(users):,} contributors</div>', unsafe_allow_html=True)
