import pickle
from pathlib import Path
import streamlit_authenticator as stauth

usernames = ["admin", "user"]
passwords = ["xxx", "xxx"]

hashed_passwords = hashed_passwords = [stauth.Hasher().hash(pw) for pw in passwords]

file_path = "hashed_passwords.pkl"

with open(file_path, "wb") as file:
    pickle.dump(hashed_passwords, file)
