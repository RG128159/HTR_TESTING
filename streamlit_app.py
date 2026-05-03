import pickle
from pathlib import Path
import streamlit as st
import streamlit_authenticator as stauth

# ---- PAGE CONFIG (App name) ----
st.set_page_config(page_title="Login", layout="wide")

file_path = Path("hashed_passwords.pkl")

with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

credentials = {
    "usernames": {
        "Admin": {
            "name": "Admin",
            "password": hashed_passwords[0],
        },
        "User": {
            "name": "User",
            "password": hashed_passwords[1],
        },
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "HTR_Testing_Database",
    "HTR030526",
    cookie_expiry_days=30,
)

# ---- SIDEBAR LOGIN ----
with st.sidebar:
    st.title("🔐 Login")
    authenticator.login(location="sidebar")

authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")

# ---- AUTH FLOW ----
if authentication_status:
    with st.sidebar:
        st.success(f"Logged in as {name}")
        authenticator.logout("Logout", location="sidebar")

    # Summary FIRST
    pg = st.navigation([
        st.Page("pages/Upload_Checker_(Free_to_use).py", title="Upload Checker"),
        st.Page("pages/DataBase_(Login_Required).py", title="DataBase"),
    ])
    pg.run()

elif authentication_status is False:
    st.error("Username/password is incorrect")

else:
    st.title("Welcome to the HTR Testing Database - please login to access the content")
    st.subheader("You can still use the Summary page without logging in, but you won't be able to access the DataBase page.")
    st.warning("Please enter your username and password")