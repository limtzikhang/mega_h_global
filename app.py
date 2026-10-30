# ======================================================================================================================
# LINE MODULE 001 - 130: DEPLOYMENT SETUPS, SYSTEM LIBS, ENFORCED FIREBASE CLOUD CONTROLS, AND SIDEBAR NAVIGATION
# ======================================================================================================================
import streamlit as st
import re
import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, auth, firestore
import streamlit.components.v1 as components

# This pulls the updated strings from your animations.py file
from animations import BLOOD_FLOW_HTML, REDUCTION_HTML, HYDRATION_HTML

# --- PLACE IMMEDIATELY AFTER IMPORTS ---
st.set_page_config(page_title="Product Info Portal", layout="wide")

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
                                    "signup_reward_claimed": False
                                }
                                db.collection("users").document(email).set(payload)
                                st.success("🎉 Account Written Live to Cloud! Data streamed cleanly to your Firestore collections table.")
                            except Exception as e:
                                st.error(f"Cloud operational pipeline failed: {e}")
# ======================================================================================================================
# LINE MODULE 391 - 520: ADMINISTRATIVE SYSTEM SHEETS, PRESENTATION DOMAINS, AND MLM GENEALOGY WORKSPACES
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
    st.subheader("🎬 Live Simulation Frameworks")
    st.write("Click a panel to view the visual mechanical simulations.")

    # --- ROW 1 ANIMATION ---
    st.markdown("### 🔴 1. Zeta Potential Flow")
    # Enforce a tight, 450px centered window frame that matches our chat window exactly
    components.html(f'<div style="display:flex; justify-content:center;">{BLOOD_FLOW_HTML}</div>', height=205, scrolling=False)
    st.write("---")

    # --- ROW 2 ANIMATION ---
    st.markdown("### ⚡ 2. Radical Reduction Engine")
    components.html(f'<div style="display:flex; justify-content:center;">{REDUCTION_HTML}</div>', height=205, scrolling=False)
    st.write("---")

    # --- ROW 3 ANIMATION ---
    st.markdown("### 💧 3. Microcluster Entry")
    components.html(f'<div style="display:flex; justify-content:center;">{HYDRATION_HTML}</div>', height=205, scrolling=False)
    st.write("---")


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
