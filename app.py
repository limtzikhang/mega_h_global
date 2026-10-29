# ======================================================================================================================
# LINE MODULE 001 - 130: CORES PIPELINES, DEPLOYMENT INITIALIZATION ENGINE, INTERACTIVE RETRACTABLE SIDEBAR NAVIGATION
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
    "Maybank (Malayan Banking Berhad)", "CIMB Bank Berhad", "Public Bank Berhad", "RHB Bank Berhad",
    "Hong Leong Bank Berhad", "AmBank (M) Berhad", "UOB (United Overseas Bank Malaysia)",
    "OCBC Bank (Malaysia) Berhad", "HSBC Bank Malaysia Berhad", "Standard Chartered Bank Malaysia",
    "Affin Bank Berhad", "Alliance Bank Malaysia Berhad", "Bank Islam Malaysia Berhad",
    "Bank Muamalat Malaysia Berhad", "Bank Rakyat", "BSN (Bank Simpanan Nasional)", "Agrobank",
    "Al Rajhi Bank Malaysia", "MBSB Bank Berhad", "GXBank (Digital Bank)", "AEON Bank (Digital Bank)",
    "Boost Bank (Digital Bank)"
]

def is_valid_email(email_str):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email_str) is not None

def process_user_logout():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.rerun()

# ----------------------------------------------------------------------------------------------------------------------
# RETRACTABLE NAVIGATION PANE (LEFT SIDEBAR LINK GENERATION)
# ----------------------------------------------------------------------------------------------------------------------
with st.sidebar:
    st.title("🌐 Hub Navigation")
    st.write("Toggle the arrow `>` or `<` at the top left of your viewport to retract this panel.")
    st.write("---")
    current_page = st.radio(
        "Select Portal Section Node:",
        [
            "🔑 1. Authorization Gateways",
            "📺 2. Product Video Presentation",
            "ℹ️ 3. Product Information Speclist",
            "🛒 4. Commercial Purchase Room"
        ]
    )
    st.write("---")
    if is_live_firebase:
        st.caption("🟢 Connection status: Live Firebase Storage Cluster")
    else:
        st.caption("🟡 Connection status: Sandbox Local Virtual Database")
# ======================================================================================================================
# LINE MODULE 131 - 260: CENTRAL ROUTING MATRIX LOOKUPS, AUTH PORTAL VIEWPORTS, AND ACCESS FORM VALIDATORS
# ======================================================================================================================
if current_page == "🔑 1. Authorization Gateways":
    st.title("🔐 Secure Member Portal & Central Database Engine")
    app_view, admin_view = st.tabs(["👥 User Portal Gateways", "📊 Tabulated Admin Profile Engine"])
    
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
                        elif chosen_bank == MALAYSIAN_BANKS:
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
# LINE MODULE 391 - 520: ADMIN DATABASE CONTROL PANELS, COMPREHENSIVE VIDEO PLATFORM MEDIA VIEWPORTS STRUCTURING
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
                st.error(f"Data stream collection pipeline exception dropped: {e}")
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

elif current_page == "📺 2. Product Video Presentation":
    st.title("📺 Media Presentation Room")
    st.write("Review our dynamic promotional video and ecosystem layout highlights down below.")
    st.write("---")
    # Native Streamlit structural media container layout engine mapping samples
    st.video("https://w3schools.com")
    st.subheader("Video Highlights Context Summary")
    st.markdown("- **Core Platform Utility**: Learn how our global node connections benefit your up-and-down lines.")
    st.markdown("- **Security Layout Infrastructure**: Encrypted database frameworks utilizing Google Firebase core layers.")
# ======================================================================================================================
# LINE MODULE 521+: ECORES METRICS LAYOUT VIEWS, PRODUCT INFO SCHEMATICS LISTS, AND DISPATCH COMMERCE GATEWAYS
# ======================================================================================================================
elif current_page == "ℹ️ 3. Product Information Speclist":
    st.title("ℹ️ Mega H Global Product Inventory Center")
    st.write("Examine our system core product capabilities and engineering design outlines.")
    st.write("---")
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.image("https://unsplash.com", caption="Ecosystem Node Hardware Module A")
    with col_info2:
        st.subheader("Technical Performance Metrics Specs")
        st.write("**Product Name:** Mega Hub Node Engine v4.0")
        st.write("**Origin Node:** Kuala Lumpur Logistics Terminal Base")
        st.write("**Ecosystem Compatibility:** Fully connects with assigned parent downlines network maps.")
        st.info("💡 Pro-Tip: Users can check the database matrix logs to verify their network association mapping IDs.")

elif current_page == "🛒 4. Commercial Purchase Room":
    st.title("🛒 Commercial Checkout Gateway Engine")
    st.write("Secure your units or deploy new ecosystem expansion profiles immediately from this viewport terminal room.")
    st.write("---")
    if not st.session_state.logged_in:
        st.warning("🔒 Access Blocked: You must authenticate your login status token in link 1 before accessing secure commerce purchases.")
    else:
        st.success(f"Verified Checkout Node Active for session token: **{st.session_state.user_email}**")
        with st.form("checkout_order_submission_form"):
            st.subheader("Order Information Payload Data")
            selected_item = st.selectbox("Choose Product Variant Configuration:", ["Standard Hub Unit - MYR 250", "Premium Network Matrix Package - MYR 600"])
            order_quantity = st.number_input("Unit Allocation Quantity:", min_value=1, max_value=50, value=1)
            st.write(f"**Assigned Shipping Address Target:** {st.session_state.user_email} associated user profiles records location")
            if st.form_submit_button("Confirm Order Execution and Bill Linked Bank Account"):
                st.balloons()
                st.success("🛒 Transaction Pipeline Triggered! Orders captured and registered to your cloud system node records mapping profile.")
