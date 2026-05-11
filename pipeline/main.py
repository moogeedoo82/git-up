from dotenv import load_dotenv
load_dotenv()

def run():
    print("🚀 Starting Cloud-Integrated Pipeline...")
    from .extract_repos import get_top_repos
    from .extract_contributors import get_contributors_and_users
    from .history import build_repo_history
    from .load import save_csv
    from .extract_commits import update_commit_counts

    # 1. Repos
    repos = get_top_repos()
    save_csv(repos, "public_repo/data/repositories.csv", table_name="repositories")

    # 2. Contributors & Users
    contributors, users = get_contributors_and_users(repos)
    save_csv(contributors, "public_repo/data/contributors.csv", table_name="contributors")
    save_csv(users, "public_repo/data/users.csv", table_name="users")

    # 3. History
    history = build_repo_history(repos, "public_repo/data/repo_history.csv")
    save_csv(history, "public_repo/data/repo_history.csv")

    # 4. Commit Lookup
    update_commit_counts()

    print("🎉 PIPELINE COMPLETE: All data local and in Supabase.")

if __name__ == "__main__":
    run()
