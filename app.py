# ======================================================================================================================
# LINE MODULE 001 - 130: DEPLOYMENT SETUPS, SYSTEM LIBS, ENFORCED FIREBASE CLOUD CONTROLS, AND SIDEBAR NAVIGATION
# ======================================================================================================================
import streamlit as st
import re
import os
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
    "RHB Bank Berhad", "RHB Islamic Berhad",
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

# 📦 PASTED TRIGGER: TWO-LEVEL TRANSACTION LEDGER WRITER
def process_dynamic_b2b_payout(buyer_email, total_bottles):
    """Executes dynamic 2-level commission distributions safely, logging steps to firestore."""
    if total_bottles < 50:
        return
        
    try:
        buyer_ref = db.collection("users").document(buyer_email.strip().lower()).get()
        if not buyer_ref.exists:
            return
            
        buyer_data = buyer_ref.to_dict()
        l1_email = buyer_data.get("upline", "").strip().lower()
        
        if l1_email and l1_email != buyer_email.strip().lower():
            l1_ref = db.collection("users").document(l1_email).get()
            if l1_ref.exists:
                # Level 1 Payout calculation (RM5 per bottle)
                l1_bonus = total_bottles * 5.0
                db.collection("users").document(l1_email).update({"wallet_balance": firestore.Increment(l1_bonus)})
                
                # Write Step 2 Ledger Record for Level 1
                db.collection("transactions").add({
                    "recipient_email": l1_email,
                    "buyer_email": buyer_email,
                    "level": 1,
                    "amount": l1_bonus,
                    "description": f"Level 1 B2B Recruit Bonus from {buyer_email} ({total_bottles} bottles)"
                })
                
                # Trace network architecture to Level 2
                l1_data = l1_ref.to_dict()
                l2_email = l1_data.get("upline", "").strip().lower()
                
                if l2_email and l2_email not in [buyer_email.strip().lower(), l1_email]:
                    l2_ref = db.collection("users").document(l2_email).get()
                    if l2_ref.exists:
                        # Level 2 Payout calculation (RM3 per bottle)
                        l2_bonus = total_bottles * 3.0
                        db.collection("users").document(l2_email).update({"wallet_balance": firestore.Increment(l2_bonus)})
                        
                        # Write Step 2 Ledger Record for Level 2
                        db.collection("transactions").add({
                            "recipient_email": l2_email,
                            "buyer_email": buyer_email,
                            "level": 2,
                            "amount": l2_bonus,
                            "description": f"Level 2 B2B Grandfather Bonus from {buyer_email} via {l1_email} ({total_bottles} bottles)"
                        })
    except Exception as e:
        st.error(f"Commission distribution failure: {e}")

def update_upline_post_registration(user_email, new_upline_email):
    """Updates the upline node in Firestore dynamically for post-registration modifications."""
    cleaned_upline = new_upline_email.strip().lower()
    cleaned_user = user_email.strip().lower()
    if not cleaned_upline or not is_valid_email(cleaned_upline):
        st.error("Validation error: Please input a structurally valid email reference string.")
        return False
    if cleaned_user == cleaned_upline:
        st.error("Hierarchy error: You cannot bind your own user node as an upline identifier.")
        return False
    try:
        upline_ref = db.collection("users").document(cleaned_upline).get()
        if not upline_ref.exists:
            st.error("Registry mismatch: The requested upline email target node does not exist in our cloud database.")
            return False
        db.collection("users").document(cleaned_user).update({"upline": cleaned_upline})
        st.success("🎉 Network position synchronized successfully! Upline structure updated.")
        return True
    except Exception as e:
        st.error(f"Cloud update pipeline error: {e}")
        return False

with st.sidebar:
    st.title("🌐 Hub Navigation")
    st.write("---")
    current_page = st.radio(
        "Select Portal Section Node:",
        [
            "🔑 1. Authorization Gateways",
            "📺 2. Product Video Presentation",
            "ℹ️ 3. Product Information Speclist",
            "🌳 4. Interactive MLM Genealogy Tree",
            "🛒 5. Commercial Purchase Room",
            "📦 6. Shipment Status & Logistics Details"
        ]
    )
    st.write("---")
    st.success("🟢 Verified Cloud Mode Active")
# ======================================================================================================================
# LINE MODULE 131 - 260: ACCESS PORTALS, SECURE PROFILE EXTRACTION, AND USER RECOGNITION INTERFACES
# ======================================================================================================================
if current_page == "🔑 1. Authorization Gateways":
    st.title("🔐 Secure Member Portal & Central Database Engine")
    app_view, admin_view = st.tabs(["👥 User Portal Gateways", "📊 Tabulated Admin Profile Engine"])
    
    with app_view:
        if st.session_state.logged_in:
            st.header(f"Welcome back to your node dashboard, {st.session_state.user_name}!")
            st.info(f"🔑 **Your Unique Firebase Account Identifier (UID):** `{st.session_state.user_uid}`")
            try:
                user_doc = db.collection("users").document(st.session_state.user_email).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    
                    # 📊 FINANCIAL OVERVIEW METRIC TILES
                    st.write("---")
                    st.subheader("💰 Financial Ledger & Earnings Matrix")
                    current_balance = user_data.get("wallet_balance", 0.0)
                    st.metric(label="Available Earning Wallet Balance", value=f"RM {current_balance:,.2f}")
                    
                    # 📋 DYNAMIC TRANSACTION HISTORY LEDGER
                    st.write("### 📜 Level 1 & Level 2 Commission Records")
                    tx_list = []
                    tx_ref = db.collection("transactions").where("recipient_email", "==", st.session_state.user_email).stream()
                    for doc in tx_ref:
                        tx_list.append(doc.to_dict())
                        
                    if tx_list:
                        tx_df = pd.DataFrame(tx_list)
                        # Clean up formatting for readability
                        if "amount" in tx_df.columns:
                            tx_df["amount"] = tx_df["amount"].apply(lambda x: f"RM {x:,.2f}")
                        st.dataframe(tx_df[["level", "amount", "buyer_email", "description"]], use_container_width=True, hide_index=True)
                    else:
                        st.info("ℹ️ No downline commission distributions have been credited to this node account yet.")
                    
                    # 🛠️ POST-REGISTRATION UPLINE MANAGEMENT UTILITY
                    st.write("---")
                    st.subheader("Network Hierarchy Settings")
                    current_upline = user_data.get("upline")
                    if current_upline and current_upline.strip():
                        st.success(f"🔒 **Network Position Locked:** Your account node is permanently assigned to Upline: `{current_upline}`")
                    else:
                        st.warning("⚠️ **Unassigned Node:** You currently have no parent upline recruiter assigned.")
                        with st.form("post_reg_upline_update_form"):
                            new_upline_input = st.text_input("Enter Parent Recruiter Email Address to Link Node:").strip()
                            if st.form_submit_button("Link Network Position Permanently"):
                                if update_upline_post_registration(st.session_state.user_email, new_upline_input):
                                    st.rerun()
            except Exception as e:
                st.error(f"Error executing profile extraction process logic: {e}")
            
            st.write("---")
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
                                auth_user = auth.get_user_by_email(login_email)
                                user_doc = db.collection("users").document(login_email).get()
                                if user_doc.exists:
                                    data = user_doc.to_dict()
                                    st.session_state.logged_in = True
                                    st.session_state.user_email = login_email
                                    st.session_state.user_name = data.get("name", "User")
                                    st.session_state.user_uid = auth_user.uid
                                    st.rerun()
                                else:
                                    st.error("Verification mismatch error: Profile data matrix entries missing.")
                            except Exception as e:
                                st.error(f"Authentication exception: Invalid credentials or missing account records: {e}")

# ======================================================================================================================
# LINE MODULE 261 - 390: PIPELINE ENROLLMENT SYSTEMS, INPUT DATA FIELD MAPPING, AND FIRESTORE CLOUD WRITERS
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
                            st.error("Banking mapping error: Please select a valid bank from the selection registry.")
                        elif not is_valid_email(email):
                            st.error("Formatting syntax exception: Target email fails structural validation requirements tests.")
                        elif len(password) < 6:
                            st.error("Security criteria exception: Password validation length parameters fail minimal 6-character thresholds.")
                        else:
                            try:
                                created_user = auth.create_user(email=email, password=password, display_name=name)
                                payload = {
                                    "uid": created_user.uid,
                                    "name": name, "email": email, "age": int(age), "gender": gender,
                                    "mobile": mobile, "address": address, "bank_name": chosen_bank,
                                    "bank_account": bank_account, "upline": upline.strip() if upline else None,
                                    "signup_reward_claimed": False,
                                    "is_admin": False  # 🔐 Adds default non-admin flag to new profiles
                                }
                                db.collection("users").document(email).set(payload)
                                st.success("🎉 Account Written Live to Cloud! Data streamed cleanly to your Firestore collections table.")
                            except Exception as e:
                                st.error(f"Cloud operational pipeline failed: {e}")
# ======================================================================================================================
# LINE MODULE 391 - 520: ADMINISTRATIVE SYSTEM SHEETS, PRESENTATION DOMAINS, AND MLM GENEALOGY WORKSPACES
# ======================================================================================================================
    with admin_view:
        # 🔒 ADMIN PRIVILEGE VALIDATION LAYER
        is_current_user_admin = False
        if st.session_state.logged_in:
            try:
                current_user_doc = db.collection("users").document(st.session_state.user_email).get()
                if current_user_doc.exists:
                    is_current_user_admin = current_user_doc.to_dict().get("is_admin", False)
            except Exception:
                pass

        if not is_current_user_admin:
            st.error("🔒 Security Clearance Denied: This administrative panel requires an authorized admin profile token signature.")
        else:
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

            # 🛠️ EXECUTIVE HIERARCHY OVERWRITE PANEL
            st.write("---")
            st.subheader("🔧 Executive Network Correction Panel")
            st.caption("Authorized administrators can use this tool to correct misconfigured or mistyped upline trees.")
            
            with st.form("admin_upline_correction_form"):
                target_user_email = st.text_input("Target User Email to Modify (Buyer):").strip().lower()
                corrected_upline_email = st.text_input("New Corrected Upline Recruiter Email (Leave blank to remove/reset):").strip().lower()
                
                if st.form_submit_button("Force Overwrite Network Node Structure", type="primary"):
                    if not target_user_email:
                        st.error("Missing fields error: Please specify a target user account node to modify.")
                    elif target_user_email == corrected_upline_email:
                        st.error("Hierarchy error: You cannot bind a user node as its own upline recruiter.")
                    else:
                        try:
                            # 1. Verify target user exists
                            user_check = db.collection("users").document(target_user_email).get()
                            if not user_check.exists:
                                st.error(f"Registry mismatch: Target user '{target_user_email}' does not exist in the database.")
                            else:
                                # 2. Verify new upline exists if it's not a complete deletion/reset
                                if corrected_upline_email:
                                    upline_check = db.collection("users").document(corrected_upline_email).get()
                                    if not upline_check.exists:
                                        st.error(f"Registry mismatch: The requested upline email '{corrected_upline_email}' does not exist.")
                                        st.stop()
                                
                                # 3. Commit administrative override bypassing normal user blocks
                                db.collection("users").document(target_user_email).update({
                                    "upline": corrected_upline_email if corrected_upline_email else None
                                })
                                st.success(f"🎉 Admin Overwrite Successful! Network position for '{target_user_email}' has been updated.")
                                st.rerun()
                        except Exception as ex:
                            st.error(f"Administrative database update failed: {ex}")

elif current_page == "📺 2. Product Video Presentation":
    st.title("📺 Media Presentation Room")
    st.write("---")
    st.video("https://w3schools.com")

elif current_page == "ℹ️ 3. Product Information Speclist":
    st.title("ℹ️ Mega H Global Product Inventory Center")
    st.write("---")
    st.image("https://unsplash.com", caption="Hardware Node Module")

elif current_page == "🌳 4. Interactive MLM Genealogy Tree":
    st.title("🌳 MLM Network Genealogy & Binary Matrix Visualizer")
    st.write("---")
    if not st.session_state.logged_in:
        st.warning("🔒 Access Restricted: Please authenticate your signature token on Link 1 to read your network branch positions.")
    else:
        st.success(f"Network context established for user node: **{st.session_state.user_email}**")
        st.info("🛠️ FUTURE PRODUCTION LOGIC STAGE: This module will read upline and downline keys from Firestore to generate dynamic network chart visualizers.")
        st.subheader("Your Network Core Connections Preview")
        col_t1, col_t2 = st.columns(2)
        col_t1.metric(label="Assigned Direct Sponsor Node (Upline ID)", value="Awaiting Data Match")
        col_t2.metric(label="Total Downline Connections Count", value="0 Active Members")
# ======================================================================================================================
# LINE MODULE 521 - 650: DYNAMIC FOLDER IMAGE SCANNING, MULTI-TIER MLM RATES ENGINE, AND STATEFUL MAYBANK2U BANKING FORM
# ======================================================================================================================
elif current_page == "🛒 5. Commercial Purchase Room":
    st.title("🛒 Commercial Checkout Gateway Engine")
    st.write("---")
    if not st.session_state.logged_in:
        st.warning("🔒 Access Blocked: You must authenticate your login status token in link 1 before accessing secure commerce purchases.")
    else:
        st.success(f"Verified Checkout Node Active for session token UID: **{st.session_state.user_uid}**")
        try:
            import mlm_logic
        except ImportError:
            st.error("🚨 Missing System File: Please verify that 'mlm_logic.py' exists in your root folder directory.")
            st.stop()

        if "checkout_stage" not in st.session_state: st.session_state.checkout_stage = "form"
        if "pending_order" not in st.session_state: st.session_state.pending_order = {}

        PRODUCT_DIR = "product"
        if not os.path.exists(PRODUCT_DIR): os.makedirs(PRODUCT_DIR)
        valid_extensions = (".png", ".jpg", ".jpeg", ".webp")
        product_images = [f for f in os.listdir(PRODUCT_DIR) if f.lower().endswith(valid_extensions)]
        
        product_options = []
        if len(product_images) > 0:
            st.subheader(f"📦 Active Product Catalog Matrix ({len(product_images)} Items Found)")
            grid_cols = st.columns(min(len(product_images), 4))
            for index, img_filename in enumerate(product_images):
                col_target = grid_cols[index % 4]
                clean_title = os.path.splitext(img_filename)[0].replace("_", " ").upper()
                product_options.append(clean_title)
                with col_target:
                    st.image(os.path.join(PRODUCT_DIR, img_filename), use_container_width=True)
                    st.write(f"**🏷️ {clean_title}**")
            st.write("---")
        else:
            product_options = ["DEFAULT BOTTLE PRODUCT"]

        if st.session_state.checkout_stage == "form":
            with st.form("checkout_order_submission_form"):
                st.subheader("Place Your Order Allocation Setup")
                selected_item = st.selectbox("Choose Product Catalog Choice:", product_options)
                st.caption("ℹ️ Tiered Rates: 1 bottle = RM248 | 2-49 bottles = RM198/ea | 50 bottles (B2B) = RM148/ea")
                order_quantity = st.number_input("Unit Allocation Quantity (Bottles per Purchase):", min_value=1, max_value=50, value=1)
                
                user_ctx = {}
                try:
                    doc = db.collection("users").document(st.session_state.user_email).get()
                    if doc.exists: user_ctx = doc.to_dict()
                except Exception: pass

                pricing = mlm_logic.calculate_bottle_order(int(order_quantity), user_ctx)
                
                st.markdown("### 📊 Order Billing Summary Preview")
                cb1, cb2, cb3 = st.columns(3)
                cb1.metric("Price per Bottle", f"RM {pricing['price_per_bottle']}")
                cb2.metric("Total Order Subtotal", f"RM {pricing['subtotal']}")
                cb3.metric("Free Bonus Bottles", f"{pricing['free_reward_bottles']} Bottle")
                
                st.write(f"**📋 Account Privilege Class:** `{pricing['tier_classification']}`")
                st.write(f"**🚚 Total Bottles Dispatched via Central Delivery:** `{pricing['total_delivery_bottles']}` bottles")

                if st.form_submit_button("💳 Proceed to Maybank2u Secure Payment"):
                    if len(product_images) == 0:
                        st.error("Transaction stopped: Cannot checkout without active product assets inside product/ folder.")
                    else:
                        st.session_state.pending_order = {
                            "product": selected_item, "quantity": int(order_quantity), "subtotal": pricing['subtotal'],
                            "delivery_total": pricing['total_delivery_bottles'], "applied_reward": pricing['is_signup_reward_applied']
                        }
                        st.session_state.checkout_stage = "maybank_gateway"
                        st.rerun()
# ======================================================================================================================
# LINE MODULE 651+: BANK TAC VALIDATION, ORDER WRITING ROUTINES, AND REAL-TIME LOGISTICS TRACKER LOOPS
# ======================================================================================================================
        elif st.session_state.checkout_stage == "maybank_gateway":
            p_order = st.session_state.pending_order
            st.markdown("""
                <div style="background-color:#FFCC00; padding:15px; border-radius:5px; text-align:center; margin-bottom:20px;">
                    <h2 style="color:#000000; margin:0; font-family:Arial, sans-serif;">💛 maybank2u.com Sandbox Gateway</h2>
                    <p style="color:#333333; margin:5px 0 0 0;">Secure Online Banking Demo Environment</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.container(border=True):
                st.write(f"**Merchant Name:** MEGA H GLOBAL SDN BHD")
                st.write(f"**Amount Due:** <span style='color:#d32f2f; font-weight:bold; font-size:18px;'>RM {p_order['subtotal']}.00</span>", unsafe_allow_html=True)
                st.write("---")
                st.text_input("Enter Maybank2u Username", value="malaysian_buyer88", disabled=True)
                st.text_input("Enter Secret Password String", value="********", type="password", disabled=True)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("📲 Request TAC Authorization Code", use_container_width=True):
                        st.session_state.sent_tac = "123456"
                        st.info("💡 Sandbox Simulation Notice: Your test TAC code is: **123456**")
                
                tac_input = st.text_input("Enter 6-Digit TAC Verification Code:", placeholder="######")
                
                col_nav1, col_nav2 = st.columns(2)
                with col_nav1:
                    if st.button("Confirm Payment Securely", type="primary", use_container_width=True):
                        if tac_input == "123456":
                            try:
                                order_payload = {
                                    "user_email": st.session_state.user_email, "product": p_order['product'],
                                    "quantity": p_order['quantity'], "amount_paid": p_order['subtotal'],
                                    "delivery_bottles": p_order['delivery_total'], "status": "Paid (Preparing Cargo)",
                                    "carrier": "PosLaju Malaysia", "tracking_id": f"PL-{st.session_state.user_uid[:5].upper()}-99X",
                                    "timestamp": firestore.SERVER_TIMESTAMP
                                }
                                db.collection("orders").add(order_payload)
                                if p_order['applied_reward']:
                                    db.collection("users").document(st.session_state.user_email).update({"signup_reward_claimed": True})
                                st.success("💰 Maybank Transaction Authorized Successfully!")
                                st.balloons()
                                st.session_state.checkout_stage = "form"
                                st.session_state.pending_order = {}
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Failed to record data inside database: {ex}")
                        else:
                            st.error("🚨 Invalid authentication entry: The input TAC code does not match the active sandbox verification criteria.")
                with col_nav2:
                    if st.button("Cancel & Abort Purchase", use_container_width=True):
                        st.session_state.checkout_stage = "form"
                        st.session_state.pending_order = {}
                        st.rerun()

elif current_page == "📦 6. Shipment Status & Logistics Details":
    st.title("📦 Logistics Pipeline & Real-Time Shipment Status Tracker")
    st.write("---")
    if not st.session_state.logged_in:
        st.warning("🔒 Access Blocked: Log in to link 1 to track shipping parameters bound to your account.")
    else:
        st.success(f"Active tracking connection established for profile: **{st.session_state.user_email}**")
        user_orders = []
        try:
            orders_ref = db.collection("orders").where("user_email", "==", st.session_state.user_email).stream()
            for doc in orders_ref: user_orders.append(doc.to_dict())
        except Exception as e:
            st.error(f"Error loading system order data matrices from cloud: {e}")

        if len(user_orders) == 0:
            st.info("ℹ️ No active checkout history logged under this profile yet. Go to Link 5 to run a Maybank test transaction purchase!")
        else:
            st.subheader(f"📊 Your Dispatch Queue Records ({len(user_orders)} Shipments In Progress)")
            for order in user_orders:
                with st.container(border=True):
                    col_s1, col_s2, col_s3 = st.columns(3)
                    col_s1.markdown(f"**📦 Consignment Product Item:** `{order.get('product')}`")
                    col_s1.write(f"**🔢 Quantity Ordered:** {order.get('quantity')} bottles")
                    col_s2.markdown(f"**🚚 Assigned Logistics Carrier:** `{order.get('carrier')}`")
                    col_s2.write(f"**🎫 Air Waybill Tracking Number:** `{order.get('tracking_id')}`")
                    col_s3.markdown(f"**💰 Ledger Transaction Cost:** `RM {order.get('amount_paid')}`")
                    col_s3.write(f"**📦 Total Delivery Vol:** `{order.get('delivery_bottles')}` bottles")
                    st.markdown(f"**🚨 Operational Status Tracker Label:** <span style='color:#1e88e5; font-weight:bold;'>{order.get('status')}</span>", unsafe_allow_html=True)
                    st.progress(45, text="Fulfillment State Indicator: Payment verified. Warehouse cargo packing sorting active.")
