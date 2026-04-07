import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config
import auth
import i18n
from sections import competitor

st.set_page_config(page_title="Competitor Analysis", page_icon="🔍", layout="wide")
st.markdown(config.CSS, unsafe_allow_html=True)

auth.check_auth()

lang_choice = "EN"
_ = lambda key, *args, **kwargs: i18n.get_text(lang_choice, key, *args, **kwargs)

competitor.render(_)
