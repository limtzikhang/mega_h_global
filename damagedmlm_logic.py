import streamlit as st
from firebase_admin import firestore
from datetime import datetime

# =====================================================================
# MODULE CONSTANTS & PRICING BREAKS
# =====================================================================
COMMISSION_RATES = {
    "b2b_50_bottles": {
        "level_1": 5.0,  # Immediate recruiter gets RM5/bottle
        "level_2": 3.0   # Recruiter's recruiter gets RM3/bottle
    }
}

def calculate_bottle_order(quantity: int, user_context: dict = None) -> dict:
    """Calculates baseline individual bundle tier price breaks."""
    qty = max(1, int(quantity))
    if qty == 1:
        price_per_bottle = 248.0
        tier_classification = "Standard Retail Tier"
    elif 2 <= qty <= 49:
        price_per_bottle = 198.0
        tier_classification = "Volume Retail Pack"
    else:
        price_per_bottle = 148.0
        tier_classification = "B2B Wholesaler Bundle"

    subtotal = qty * price_per_bottle
    free_reward_bottles = 0
    is_signup_reward_applied = False
    
    if user_context and not user_context.get("signup_reward_claimed", False):
        if qty >= 2:
            free_reward_bottles = 1
            is_signup_reward_applied = True

    total_delivery_bottles = qty + free_reward_bottles
    return {
        "price_per_bottle": price_per_bottle,
        "subtotal": subtotal,
        "free_reward_bottles": free_reward_bottles,
        "total_delivery_bottles": total_delivery_bottles,
        "tier_classification": tier_classification,
        "is_signup_reward_applied": is_signup_reward_applied
    }

# =====================================================================
# FIRESTORE INTEGRATION HOOKS
# =====================================================================
def get_user_data(username: str) -> dict:
    """Extracts user profile details directly out of Firestore streams."""
    try:
        db = firestore.client()
        user_doc = db.collection("users").document(username).get()
        if user_doc.exists:
            return user_doc.to_dict()
    except Exception:
        pass
    return None

def update_upline(username: str, upline_username: str) -> bool:
    """Updates the missing upline for an account inside Firestore."""
    try:
        db = firestore.client()
        if username == upline_username:
            st.error("Looping structure blocked: You cannot recruit yourself.")
            return False
            
        recruiter_doc = db.collection("users").document(upline_username).get()
        if not recruiter_doc.exists:
            st.error(f"The recruiter account '{upline_username}' does not exist.")
            return False
            
        db.collection("users").document(username).update({"upline": upline_username})
        return True
    except Exception as e:
        st.error(f"Cloud update validation failure: {e}")
        return False

# =====================================================================
# TWO-LEVEL COMMISSION ENGINE
# =====================================================================
def calculate_b2b_commission(buyer_username: str, total_bottles: int = 50):
    """Calculates and awards two-level income for B2B package buyers."""
    if total_bottles < 50:
        return 

    db = firestore.client()
    buyer = get_user_data(buyer_username)
    if not buyer:
        return

    level_1_upline = buyer.get("upline")
    if not level_1_upline:
        return 

    l1_rate = COMMISSION_RATES["b2b_50_bottles"]["level_1"]
    l1_payout = total_bottles * l1_rate
    l1_profile = get_user_data(level_1_upline)
    
    if l1_profile:
        current_bal_l1 = float(l1_profile.get("wallet_balance", 0.0))
        new_bal_l1 = current_bal_l1 + l1_payout
        db.collection("users").document(level_1_upline).update({"wallet_balance": new_bal_l1})
        log_commission_transaction(db, level_1_upline, l1_payout, buyer_username, level=1)

        level_2_upline = l1_profile.get("upline")
        if level_2_upline:
            l2_profile = get_user_data(level_2_upline)
            if l2_profile:
                l2_rate = COMMISSION_RATES["b2b_50_bottles"]["level_2"]
                l2_payout = total_bottles * l2_rate
                current_bal_l2 = float(l2_profile.get("wallet_balance", 0.0))
                new_bal_l2 = current_bal_l2 + l2_payout
                db.collection("users").document(level_2_upline).update({"wallet_balance": new_bal_l2})
                log_commission_transaction(db, level_2_upline, l2_payout, buyer_username, level=2)

def log_commission_transaction(db, username: str, amount: float, downline: str, level: int):
    """Logs transparent historical transaction entries in a shared collection."""
    try:
        ledger_payload = {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "recipient": username,
            "amount": float(amount),
            "type": f"Level {level} B2B Referral Bonus",
            "description": f"Earned from downline member {downline} purchasing a 50-bottle wholesaler tier."
        }
        db.collection("ledger").add(ledger_payload)
    except Exception:
        pass
