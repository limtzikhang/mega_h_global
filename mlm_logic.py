import streamlit as st
import pandas as pd
from datetime import datetime

# -------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------------------
COMMISSION_RATES = {
    "b2b_50_bottles": {
        "level_1": 5.0,  # Immediate recruiter gets RM5/bottle
        "level_2": 3.0   # Recruiter's recruiter gets RM3/bottle
    }
}

# -------------------------------------------------------------------------
# HELPER FUNCTIONS FOR USER RELATIONSHIPS
# -------------------------------------------------------------------------
def get_user_data(username: str) -> dict:
    """Fetch user profile information from st.session_state or database."""
    if "users_db" not in st.session_state:
        st.session_state.users_db = {}
    return st.session_state.users_db.get(username, None)

def update_upline(username: str, upline_username: str) -> bool:
    """
    Updates the upline for an existing account.
    Handles the 'register first, edit upline later' scenario.
    """
    if "users_db" not in st.session_state or username not in st.session_state.users_db:
        return False
        
    # Prevent circular reference loops
    if username == upline_username:
        st.error("You cannot set yourself as your own upline.")
        return False
        
    st.session_state.users_db[username]["upline"] = upline_username
    return True

# -------------------------------------------------------------------------
# TWO-LEVEL COMMISSION LOGIC
# -------------------------------------------------------------------------
def calculate_b2b_commission(buyer_username: str, total_bottles: int = 50):
    """
    Calculates and distributes two-level income for B2B package buyers.
    Level 1 Recruiter: RM5 per bottle
    Level 2 Recruiter: RM3 per bottle
    """
    if total_bottles < 50:
        return  # Only applies to 50 bottles or more tier

    buyer = get_user_data(buyer_username)
    if not buyer:
        return

    # 1. Track Level 1 Upline (Immediate Recruiter)
    level_1_upline = buyer.get("upline")
    if not level_1_upline:
        # If no upline is assigned yet, no commissions can be distributed.
        return 

    # Distribute Level 1 Income (e.g., B earns from C)
    l1_rate = COMMISSION_RATES["b2b_50_bottles"]["level_1"]
    l1_payout = total_bottles * l1_rate
    add_commission_to_wallet(level_1_upline, l1_payout, buyer_username, level=1)

    # 2. Track Level 2 Upline (Recruiter's Recruiter)
    l1_user_profile = get_user_data(level_1_upline)
    if l1_user_profile:
        level_2_upline = l1_user_profile.get("upline")
        
        # Distribute Level 2 Income (e.g., A earns from C)
        if level_2_upline:
            l2_rate = COMMISSION_RATES["b2b_50_bottles"]["level_2"]
            l2_payout = total_bottles * l2_rate
            add_commission_to_wallet(level_2_upline, l2_payout, buyer_username, level=2)

# -------------------------------------------------------------------------
# WALLET UPDATE ENGINE
# -------------------------------------------------------------------------
def add_commission_to_wallet(username: str, amount: float, downline: str, level: int):
    """Credits the calculated reward into the respective user's wallet ledger."""
    if "ledger" not in st.session_state:
        st.session_state.ledger = []
        
    if username in st.session_state.users_db:
        # Credit the user balance
        st.session_state.users_db[username]["wallet_balance"] = (
            st.session_state.users_db[username].get("wallet_balance", 0.0) + amount
        )
        
        # Append transaction history record
        st.session_state.ledger.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recipient": username,
            "amount": f"RM {amount:.2f}",
            "type": f"Level {level} Referral Bonus",
            "description": f"Earned from downline {downline} purchasing a B2B package."
        })
