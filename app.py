# ======================================================================================================================
# LINE MODULE 001 - 130: SYSTEM CORE PIPELINES, DEPLOYMENT INITIALIZATION ENGINE, AND CREDENTIAL CONTEXT LOOPS
# ======================================================================================================================
import streamlit as st
import re
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, firestore

st.set_page_config(
    page_title="Firebase Security Auth Dashboard Portal",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "mock_db" not in st.session_state:
    st.session_state.mock_db = {}

is_live_firebase = False
db = None

if not firebase_admin._apps:
    try:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        is_live_firebase = True
    except Exception:
        is_live_firebase = False

MALAYSIAN_BANKS = [
    "-- Select Your Bank --",
    "Maybank (Malayan Banking Berhad)",
    "CIMB Bank Berhad",
    "Public Bank Berhad",
    "RHB Bank Berhad",
    "Hong Leong Bank Berhad",
    "AmBank (M) Berhad",
    "UOB (United Overseas Bank Malaysia)",
    "OCBC Bank (Malaysia) Berhad",
    "HSBC Bank Malaysia Berhad",
    "Standard Chartered Bank Malaysia",
    "Affin Bank Berhad",
    "Alliance Bank Malaysia Berhad",
    "Bank Islam Malaysia Berhad",
    "Bank Muamalat Malaysia Berhad",
    "Bank Rakyat",
    "BSN (Bank Simpanan Nasional)",
    "Agrobank",
    "Al Rajhi Bank Malaysia",
    "MBSB Bank Berhad",
    "GXBank (Digital Bank)",
    "AEON Bank (Digital Bank)",
    "Boost Bank (Digital Bank)"
]

def is_valid_email(email_str):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_str) is not None

def process_user_logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.rerun()

st.title("🔐 Secure Member Portal & Central Database Engine")
if is_live_firebase:
    st.success("🟢 Active Session Node: Connected to Live Firebase Cloud Infrastructure via secrets.toml")
else:
    st.warning("🟡 Standalone Safe Mode: Streamlit engine secrets.toml not found. Operating via local sandbox.")

app_view, admin_view = st.tabs(["👥 User Portal Gateways", "📊 Tabulated Admin Profile Engine"])
# ======================================================================================================================
# LINE MODULE 131 - 260: USER GATEWAYS VIEWPORTS, ACCOUNT AUTHORIZATION SYSTEM FORMS, AND ENROLLMENT PIPELINES
# ======================================================================================================================
with app_view:
    if st.session_state.logged_in:
        st.header(f"Welcome back to your node dashboard, {st.session_state.user_name}!")
        if is_live_firebase and db:
            try:
                user_doc = db.collection("users").document(st.session_state.user_email).get()
                if user_doc.exists:
                    st.json(user_doc.to_dict())
            except Exception as e:
                st.error(f"Error executing profile extraction process logic: {e}")
        else:
            st.json(st.session_state.mock_db.get(st.session_state.user_email, {}))
        st.button("Log Out of Session Room", on_click=process_user_logout, type="primary")
    else:
        tab1, tab2 = st.tabs(["🔑 Gateway User Login System", "📝 New Account Application Form"])
        with tab1:
            st.subheader("Account Authorization Panel")
            with st.form("portal_login_execution_form"):
                login_email = st.text_input("Registered Email Address").strip()
                login_password = st.text_input("Password", type="password")
                if st.form_submit_button("Authenticate Secure Node Signature"):
                    if not login_email or not login_password:
                        st.error("Identity error: Please input complete data combinations inside targets.")
                    elif is_live_firebase and db:
                        try:
                            user_doc = db.collection("users").document(login_email).get()
                            if user_doc.exists:
                                data = user_doc.to_dict()
                                st.session_state.logged_in = True
                                st.session_state.user_email = login_email
                                st.session_state.user_name = data.get("name", "User")
                                st.rerun()
                            else:
                                st.error("Verification mismatch error: Profile index not found.")
                        except Exception as e:
                            st.error(f"Internal cloud exception detected: {e}")
                    else:
                        mock_user = st.session_state.mock_db.get(login_email)
                        if mock_user and mock_user["password"] == login_password:
                            st.session_state.logged_in = True
                            st.session_state.user_email = login_email
                            st.session_state.user_name = mock_user["name"]
                            st.success("Sandbox Authorization Complete: Token deployed inside framework arrays.")
                            st.rerun()
                        else:
                            st.error("Verification mismatch error: Credentials did not clear structural hash maps.")
# ======================================================================================================================
# LINE MODULE 261 - 390: SIGN-UP SYSTEM INPUT ELEMENTS, CRITICAL LOGICAL FIELD CHECKS, AND DATA TRANSACTIONS
# ======================================================================================================================
        with tab2:
            st.subheader("Enrollment Pipeline Registry")
            with st.form("portal_signup_submission_form"):
                name = st.text_input("Legal Full Name *")
                email = st.text_input("Active Target Email Address *").strip()
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    password = st.text_input("Access Authorization Password * (Min 6 configurations)", type="password")
                with col_p2:
                    confirm_password = st.text_input("Confirm Verification Password Input *", type="password")
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input("Biological Age Matrix *", min_value=1, max_value=120, value=25)
                with col2:
                    gender = st.selectbox("Demographic Identity Gender Flag *", ["Male", "Female", "Other"])
                mobile = st.text_input("Mobile Cellular Communications String Line * (e.g., +601xxxxxxxx)")
                address = st.text_area("Physical Home Billing Address Node Structure *")
                chosen_bank = st.selectbox("Associated Malaysian Financial Corporate Bank Institution Entity *", MALAYSIAN_BANKS)
                bank_account = st.text_input("Financial Ledger Bank Account Distribution Identifier *")
                upline = st.text_input("Parent Network Upline Referral Affiliate Node Index Key (Optional)")
                if st.form_submit_button("Finalize and Launch System Profile Registration"):
                    if not (name and email and password and confirm_password and mobile and address and bank_account):
                        st.error("Missing configuration values: All fields marked with (*) must contain values.")
                    elif password != confirm_password:
                        st.error("String match exception: Secondary password validation inputs do not match.")
                    elif chosen_bank == MALAYSIAN_BANKS[0]:
                        st.error("Banking mapping error: Please anchor this data item to a registered corporate bank.")
                    elif not is_valid_email(email):
                        st.error("Formatting syntax exception: Target email fails structural validation tests.")
                    elif len(password) < 6:
                        st.error("Security criteria exception: Password validation length fails minimal thresholds.")
                    else:
                        payload = {
                            "name": name, "email": email, "age": int(age), "gender": gender,
                            "mobile": mobile, "address": address, "bank_name": chosen_bank,
                            "bank_account": bank_account, "upline": upline.strip() if upline else None
                        }
                        if is_live_firebase and db:
                            try:
                                auth.create_user(email=email, password=password, display_name=name)
                                db.collection("users").document(email).set(payload)
                                st.success("Cloud Transaction Dispatched: New user dataset successfully pushed into production.")
                            except Exception as e:
                                st.error(f"Cloud write operations failed: {e}")
                        else:
                            payload["password"] = password
                            st.session_state.mock_db[email] = payload
                            st.success("Local Workspace Complete: Storage array map appended safely. Go to tab 1 to launch.")
# ======================================================================================================================
# LINE MODULE 391+: CENTRAL ADMINISTRATIVE MATRICES, PANDAS MATRIX DATA ENGINE, AND DATA DUMP UTILITIES
# ======================================================================================================================
with admin_view:
    st.subheader("📋 Centralized System Database Matrix View")
    st.write("This panel tracks and structures cloud system user directories directly into tabulated dashboard spreadsheet grids.")
    records_list = []
    if is_live_firebase and db:
        try:
            for doc in db.collection("users").stream():
                dict_data = doc.to_dict()
                dict_data.pop("password", None)
                records_list.append(dict_data)
        except Exception as e:
            st.error(f"Data stream collection pipeline execution exception dropped: {e}")
    else:
        for email_key, data_val in st.session_state.mock_db.items():
            clean_item = data_val.copy()
            clean_item.pop("password", None)
            records_list.append(clean_item)
    if records_list:
        df = pd.DataFrame(records_list)
        desired_order = ["name", "email", "age", "gender", "mobile", "bank_name", "bank_account", "upline", "address"]
        existing_order = [col for col in desired_order if col in df.columns] + [col for col in df.columns if col not in desired_order]
        df = df[existing_order]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            label="📥 Export Dynamic System Data Table Matrix to Local CSV File Spreadsheet",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="system_registered_directory.csv",
            mime="text/csv",
            use_container_width=False
        )
    else:
        st.info("System registry status empty: No profiles initialized or compiled inside active directory node maps yet.")
