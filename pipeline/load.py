import os
import pandas as pd
from datetime import datetime
from supabase import create_client
from .config import SUPABASE_URL, SUPABASE_KEY

LOG_PATH = "public_repo/data/pipeline.log"

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def save_to_supabase(table_name, df):
    if not SUPABASE_URL or not SUPABASE_KEY:
        log_message(f"⚠️ SKIPPED CLOUD: Supabase credentials missing for {table_name}")
        return
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    clean_df = df.replace({pd.NA: None}).where(pd.notnull(df), None)
    data = clean_df.to_dict(orient='records')
    log_message(f"☁️ STARTING UPLOAD: {len(data)} rows to {table_name}")
    batch_size = 1000
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            if table_name == "repositories":
                supabase.table(table_name).upsert(batch, on_conflict="repo_id").execute()
            elif table_name == "users":
                supabase.table(table_name).upsert(batch, on_conflict="user_id").execute()
            elif table_name == "contributors":
                supabase.table(table_name).insert(batch).execute()
            elif table_name == "contributor_commits":
                supabase.table(table_name).upsert(batch, on_conflict="user_id,repo_id").execute()
            else:
                supabase.table(table_name).upsert(batch).execute()
        except Exception as e:
            error_msg = f"❌ CLOUD ERROR in {table_name}: {str(e)}"
            print(error_msg)
            log_message(error_msg)
    log_message(f"✅ CLOUD SUCCESS: {table_name} sync complete.")

def save_csv(df, path, table_name=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    log_message(f"💾 LOCAL SAVE: {path} ({len(df)} rows)")
    if table_name:
        save_to_supabase(table_name, df)
