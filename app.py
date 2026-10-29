# ======================================================================================================================
# LINE MODULE 001 - 130: CORES PIPELINES, ENFORCED FIREBASE CLOUD CONTROLS, COMPREHENSIVE MALAYSIAN PAYMENT BANK MAPPING
# ======================================================================================================================
import streamlit as st
import re
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, firestore

st.set_page_config(
    page_title="Firebase Security Auth & Commerce Dashboard",
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
if "user_uid" not in st.session_state:
    st.session_state.user_uid = ""

is_live_firebase = False
db = None

if not firebase_admin._apps:
    try:
        cred_dict = dict(st.secrets["firebase"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        is_live_firebase = True
    except Exception as e:
        st.error(f"🚨 CRITICAL FIREBASE CONFIGURATION ERROR: {e}")
        st.stop()
else:
    db = firestore.client()
    is_live_firebase = True

MALAYSIAN_BANKS = [
    "-- Select Your Payment Bank --",
    "Maybank (Malayan Banking Berhad)", "Maybank Islamic Berhad",
    "CIMB Bank Berhad", "CIMB Islamic Bank Berhad",
    "Public Bank Berhad", "Public Islamic Bank Berhad",
    "RHB Bank Berhad", "RHB Islamic Bank Berhad",
    "Hong Leong Bank Berhad", "Hong Leong Islamic Bank Berhad",
    "AmBank (M) Berhad", "AmBank Islamic Berhad",
    "Affin Bank Berhad", "Affin Islamic Bank Berhad",
    "Alliance Bank Malaysia Berhad", "Alliance Islamic Bank Berhad",
    "Bank Islam Malaysia Berhad", "Bank Muamalat Malaysia Berhad",
    "Bank Rakyat (Bank Kerjasama Rakyat Malaysia Berhad)",
    "BSN (Bank Simpanan Nasional)", "Agrobank (Bank Pertanian Malaysia Berhad)",
    "MBSB Bank Berhad", "SME Bank Malaysia", "EXIM Bank Malaysia",
    "UOB (United Overseas Bank Malaysia)", "OCBC Bank (Malaysia) Berhad", "OCBC Al-Amin Bank Berhad",
    "HSBC Bank Malaysia Berhad", "HSBC Amanah Malaysia Berhad",
    "Standard Chartered Bank Malaysia Berhad", "Standard Chartered Saadiq Berhad",
    "Citibank Berhad", "Bank of China (Malaysia) Berhad",
    "ICBC (Industrial and Commercial Bank of China)", "GXBank (Licensed Digital Bank)",
    "AEON Bank (Licensed Islamic Digital Bank)", "Boost Bank Berhad (Licensed Digital Bank)"
]

def is_valid_email(email_str):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_str) is not None

def process_user_logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.user_uid = ""
    st.rerun()

with st.sidebar:
    st.title("🌐 Hub Navigation")
    st.write("---")
    current_page = st.radio(
        "Select Portal Section Node:",
        ["🔑 1. Authorization Gateways", "📺 2. Product Video Presentation", "ℹ️ 3. Product Information Speclist", "🛒 4. Commercial Purchase Room"]
    )
    st.write("---")
    st.success("🟢 Verified Cloud Mode Active")
# ======================================================================================================================
# LINE MODULE 131 - 260: ACCESS MANAGEMENT PORTALS, IDENTITY UID EXTRACTION AND INTERACTIVE SECURITY WORKSPACES
# ======================================================================================================================
if current_page == "🔑 1. Authorization Gateways":
    st.title("🔐 Secure Member Portal & Central Database Engine")
    app_view, admin_view = st.tabs(["👥 User Portal Gateways", "📊 Tabulated Admin Profile Engine"])
    
    with app_view:
        if st.session_state.logged_in:
            st.header(f"Welcome back to your node dashboard, {st.session_state.user_name}!")
            
            # --- HIGHLIGHTED REFINEMENT: Displaying the unique User UID at the Gateway layer ---
            st.info(f"🔑 **Your Unique Firebase Account Identifier (UID):** `{st.session_state.user_uid}`")
            
            try:
                user_doc = db.collection("users").document(st.session_state.user_email).get()
                if user_doc.exists:
                    st.json(user_doc.to_dict())
            except Exception as e:
                st.error(f"Error executing profile extraction process logic: {e}")
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
                        else:
                            try:
                                # Fetch primary cloud user credentials object from Firebase Auth to harvest global UID
                                auth_user = auth.get_user_by_email(login_email)
                                user_doc = db.collection("users").document(login_email).get()
                                if user_doc.exists:
                                    data = user_doc.to_dict()
                                    st.session_state.logged_in = True
                                    st.session_state.user_email = login_email
                                    st.session_state.user_name = data.get("name", "User")
                                    st.session_state.user_uid = auth_user.uid  # Assign UID to global workspace tracking state
                                    st.rerun()
                                else:
                                    st.error("Verification mismatch error: Profile mapping data matrix index rows missing.")
                            except Exception as e:
                                st.error(f"Authentication exception: Invalid configuration keys or missing profile identifier logs. Info: {e}")
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
                        password = st.text_input("Access Authorization Password * (Min 6 chars)", type="password")
                    with col_p2:
                        confirm_password = st.text_input("Confirm Verification Password Input *", type="password")
                    col1, col2 = st.columns(2)
                    with col1:
                        age = st.number_input("Biological Age Matrix *", min_value=1, max_value=120, value=25)
                    with col2:
                        gender = st.selectbox("Demographic Identity Gender Flag *", ["Male", "Female", "Other"])
                    mobile = st.text_input("Mobile Cellular Communications String Line * (e.g., +601xxxxxxxx)")
                    address = st.text_area("Physical Home Billing Address Node Structure *")
                    chosen_bank = st.selectbox("Associated Malaysian Financial Payment Bank *", MALAYSIAN_BANKS)
                    bank_account = st.text_input("Financial Ledger Bank Account Number Identifier *")
                    upline = st.text_input("Parent Network Upline Referral Affiliate Node Index Key (Optional)")
                    if st.form_submit_button("Finalize and Launch System Profile Registration"):
                        if not (name and email and password and confirm_password and mobile and address and bank_account):
                            st.error("Missing fields error: All primary inputs marked with (*) must contain valid information.")
                        elif password != confirm_password:
                            st.error("🚨 PASSWORD MISMATCH ERROR: Confirmation input field entry values do not match.")
                        elif chosen_bank == MALAYSIAN_BANKS:
                            st.error("Banking mapping error: Please select a valid Malaysian corporate bank from the selection registry.")
                        elif not is_valid_email(email):
                            st.error("Formatting syntax exception: Target email fails structural validation requirements tests.")
                        elif len(password) < 6:
                            st.error("Security criteria exception: Password validation length parameters fail minimal 6-character thresholds.")
                        else:
                            try:
                                # Create cloud auth account row element to capture new UID matrix values
                                created_user = auth.create_user(email=email, password=password, display_name=name)
                                payload = {
                                    "uid": created_user.uid,  # Embed unique secure UID value configuration parameters inside dataset rows
                                    "name": name, "email": email, "age": int(age), "gender": gender,
                                    "mobile": mobile, "address": address, "bank_name": chosen_bank,
                                    "bank_account": bank_account, "upline": upline.strip() if upline else None
                                }
                                db.collection("users").document(email).set(payload)
                                st.success("🎉 Account Written Live to Cloud! Data streamed cleanly to your Firestore collections table.")
                            except Exception as e:
                                st.error(f"Cloud operational pipeline failed: {e}")
# ======================================================================================================================
# LINE MODULE 391+: CENTRAL ADMINISTRATIVE MATRICES, VIDEO CONTROLS AND MULTI-PAGE WORKSPACE VIEWPORTS
# ======================================================================================================================
    with admin_view:
        st.subheader("📋 Centralized System Database Matrix View")
        st.write("This panel tracks and structures cloud system user directories directly into tabulated dashboard spreadsheet grids.")
        records_list = []
        try:
            for doc in db.collection("users").stream():
                dict_data = doc.to_dict()
                records_list.append(dict_data)
        except Exception as e:
            st.error(f"Data stream collection pipeline execution exception dropped: {e}")
        if records_list:
            df = pd.DataFrame(records_list)
            desired_order = ["uid", "name", "email", "age", "gender", "mobile", "bank_name", "bank_account", "upline", "address"]
            existing_order = [col for col in desired_order if col in df.columns] + [col for col in df.columns if col not in desired_order]
            df = df[existing_order]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                label="📥 Export Dynamic System Data Table Matrix to Local CSV File Spreadsheet",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="system_registered_directory.csv",
                mime="text/csv"
            )
        else:
            st.info("System registry status empty: No profiles initialized or compiled inside active directory node maps yet.")

elif current_page == "📺 2. Product Video Presentation":
    st.title("📺 Media Presentation Room")
    st.write("---")
    st.video("https://w3schools.com")

elif current_page == "ℹ️ 3. Product Information Speclist":
    st.title("ℹ️ Mega H Global Product Inventory Center")
    st.write("---")
    st.image("https://unsplash.com", caption="Hardware Node Module")

elif current_page == "🛒 4. Commercial Purchase Room":
    st.title("🛒 Commercial Checkout Gateway Engine")
    st.write("---")
    if not st.session_state.logged_in:
        st.warning("🔒 Access Blocked: You must authenticate your login status token in link 1 before accessing secure commerce purchases.")
    else:
        st.success(f"Verified Checkout Node Active for session token UID: **{st.session_state.user_uid}**")
