import streamlit as st
from supabase import create_client, Client
import io
import pandas as pd

@st.cache_resource
def init_db() -> Client:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        st.error("⚠️ Configuration error: Supabase keys not found.")
        st.info("Create a `.streamlit/secrets.toml` file with SUPABASE_URL and SUPABASE_KEY.")
        st.stop()
    return create_client(url, key)

def get_db():
    return init_db()

# ── Auth ──────────────────────────────────────────────────────────────────────
def login(email, password):
    db = get_db()
    try:
        # Для простоты пока используем Supabase Auth
        response = db.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            st.session_state["user_id"] = response.user.id
            st.session_state["email"] = email
            return True
        return False
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            st.error("Invalid email or password.")
        else:
            st.error(f"Server error: {error_msg}")
        return False

def logout():
    db = get_db()
    try:
        db.auth.sign_out()
    except Exception:
        pass
    st.session_state.clear()

# ── Storage ───────────────────────────────────────────────────────────────────
def upload_file(path: str, file_bytes: bytes, mime_type: str = "text/csv", bucket_name: str = "reports"):
    db = get_db()
    try:
        db.storage.from_(bucket_name).upload(file=file_bytes, path=path, file_options={"content-type": mime_type})
    except Exception as e:
        # If already exists, update instead
        db.storage.from_(bucket_name).update(file=file_bytes, path=path, file_options={"content-type": mime_type})

def download_file(path: str, bucket_name: str = "reports") -> bytes:
    db = get_db()
    try:
        return db.storage.from_(bucket_name).download(path)
    except Exception:
        return None

def upload_csv(path: str, df: pd.DataFrame, bucket_name: str = "reports"):
    upload_file(path, df.to_csv(index=False).encode('utf-8'), "text/csv", bucket_name)

def download_csv(path: str, bucket_name: str = "reports") -> pd.DataFrame:
    res = download_file(path, bucket_name)
    if res:
        return pd.read_csv(io.BytesIO(res))
    return None

def list_projects(user_id: str, bucket_name: str = "reports") -> list:
    db = get_db()
    try:
        res = db.storage.from_(bucket_name).list(user_id)
        # Returns folders as well
        return [f["name"] for f in res if not f["name"].startswith(".")]
    except Exception:
        return []
