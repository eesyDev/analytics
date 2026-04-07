import streamlit as st
import db

def logout():
    db.logout()

def render_login():
    st.write("<br><br>", unsafe_allow_html=True)
    
    # Process OAuth callback from GitHub URL
    if "code" in st.query_params:
        try:
            code = st.query_params["code"]
            res = db.get_db().auth.exchange_code_for_session({"auth_code": code})
            if res.user:
                st.session_state["user_id"] = res.user.id
                st.session_state["email"] = res.user.email
                st.query_params.clear()
                st.rerun()
        except Exception as e:
            st.error(f"GitHub OAuth Error: {e}")
            st.query_params.clear()

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'>SEO Analytics Hub</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px;'>Sign in to access your projects and dashboards.</p>", unsafe_allow_html=True)
        
        # 1. GitHub SSO Button
        try:
            redirect_url = st.secrets.get("REDIRECT_URL", "http://localhost:8501")
            response = db.get_db().auth.sign_in_with_oauth({
                "provider": "github",
                "options": {
                    "redirect_to": redirect_url,
                    "skip_browser_redirect": True
                }
            })
            st.link_button("Continue with GitHub", response.url, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to load Github login: {e}")

        st.markdown("<div style='text-align: center; margin: 15px 0; color: #888; font-size: 0.9em;'>— or continue with email —</div>", unsafe_allow_html=True)
        
        # 2. Email & Password Form (Dual action)
        email = st.text_input("Email address")
        password = st.text_input("Password", type="password")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.warning("Please enter email and password.")
                else:
                    try:
                        resp = db.get_db().auth.sign_in_with_password({"email": email, "password": password})
                        if resp.user:
                            st.session_state["user_id"] = resp.user.id
                            st.session_state["email"] = email
                            st.rerun()
                    except Exception as e:
                        if "Invalid login credentials" in str(e):
                            st.error("Invalid email or password.")
                        else:
                            st.error(f"Authentication failed: {e}")
        
        with btn_col2:
            if st.button("Create Account", use_container_width=True):
                if len(password) < 6:
                    st.warning("Password must be at least 6 characters long.")
                else:
                    try:
                        resp = db.get_db().auth.sign_up({"email": email, "password": password})
                        st.success("Account created successfully! You can now Sign In.")
                    except Exception as e:
                        if "already registered" in str(e):
                            st.error("This email is already registered.")
                        else:
                            st.error(f"Registration failed: {e}")

def check_auth():
    if "user_id" not in st.session_state:
        render_login()
        st.stop()
