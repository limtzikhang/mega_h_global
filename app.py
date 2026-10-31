import streamlit as st
import re
import json
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore

st.set_page_config(page_title="Firebase Auth Portal", page_icon="🔐", layout="centered")

@st.cache_resource
def initialize_firebase():
    if firebase_admin._apps:
        return firestore.client()
    try:
        if "firebase" in st.secrets:
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
            firebase_admin.initialize_app(cred)
            return firestore.client()
        elif os.path.exists("firebase_creds.json"):
            cred = credentials.Certificate("firebase_creds.json")
            firebase_admin.initialize_app(cred)
            return firestore.client()
        return None
    except Exception as e:
        st.error(f"Initialization error: {e}")
        return None

db = initialize_firebase()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None

st.title("🔐 Secure Member Portal")

if db is None:
    st.warning("⚠️ Firebase configuration file missing!")
    with st.expander("🛠️ How to make it 100% working:", expanded=True):
        st.markdown("""
        1. Go to **Firebase Console** -> **Project Settings** -> **Service accounts**.
        2. Click **Generate new private key** and download the JSON.
        3. Place it in this app's directory as `firebase_creds.json`.
        """)
    if st.checkbox("💡 Enable Mock Mode (Test UI without Firebase configurations)"):
        if "mock_db" not in st.session_state:
            st.session_state.mock_db = {}
        RUN_MOCK = True
    else:
        st.stop()
else:
    RUN_MOCK = False

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔒 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login"):
            lemail = st.text_input("Email").strip()
            lpass = st.text_input("Password", type="password")
            if st.form_submit_button("Log In"):
                if RUN_MOCK:
                    user = st.session_state.mock_db.get(lemail)
                    if user and user["password"] == lpass:
                        st.session_state.logged_in = True
                        st.session_state.user_email = lemail
                        st.success("Logged in!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    try:
                        user = auth.get_user_by_email(lemail)
                        user_doc = db.collection("users").document(user.uid).get()
                        if user_doc.exists:
                            st.session_state.logged_in = True
                            st.session_state.user_email = lemail
                            st.success("Logged in!")
                            st.rerun()
                        else:
                            st.error("Profile record missing in database.")
                    except Exception as e:
                        st.error(f"Login failed: {e}")

    with tab2:
        st.subheader("Sign Up")
        with st.form("signup"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name *")
                email = st.text_input("Email *").strip()
                password = st.text_input("Password *", type="password")
                mobile = st.text_input("Mobile *")
            with c2:
                bank = st.text_input("Bank Account *")
                age = st.number_input("Age *", min_value=1, max_value=100, value=25)
                gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
                address = st.text_area("Address *")
            upline = st.text_input("Upline ID (Optional)")
            
            if st.form_submit_button("Register"):
                if not (name and email and password and mobile and bank and address):
                    st.error("Fill all required fields.")
                elif len(password) < 6:
                    st.error("Password must be >= 6 chars.")
                else:
                    if RUN_MOCK:
                        st.session_state.mock_db[email] = {"password": password, "name": name}
                        st.success("Signed up in Mock mode! Go to Login tab.")
                    else:
                        try:
                            user = auth.create_user(email=email, password=password, display_name=name)
                            db.collection("users").document(user.uid).set({
                                "name": name, "email": email, "mobile": mobile,
                                "bank": bank, "age": age, "gender": gender,
                                "address": address, "upline": upline if upline else None
                            })
                            st.success("Account created successfully! Go to Login tab.")
                        except Exception as e:
                            st.error(f"Sign up failed: {e}")
else:
    st.subheader(f"Welcome back, {st.session_state.user_email}! 👋")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.rerun()
