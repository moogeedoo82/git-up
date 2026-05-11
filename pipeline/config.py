import os

TOKEN_KEYS = ["GITHUB_TOKEN","GITHUB_TOKEN_2","GITHUB_TOKEN_3","GITHUB_TOKEN_4","GITHUB_TOKEN_5"]
GITHUB_TOKENS = [os.getenv(k) for k in TOKEN_KEYS if os.getenv(k)]

if not GITHUB_TOKENS:
    raise RuntimeError("No GITHUB tokens found!")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BASE_REST = "https://api.github.com"
BASE_GQL  = "https://api.github.com/graphql"
