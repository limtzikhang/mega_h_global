# mlm_logic.py - Complete Order and Multi-Level Commission Logic
import pandas as pd
import streamlit as st

def calculate_bottle_order(order_quantity, user_ctx):
    """
    Calculates the breakdown of pricing tiers, delivery metrics, and active rewards 
    for bottle order distributions.
    
    Tiered Rates:
    - 1 bottle = RM 248 each
    - 2 to 49 bottles = RM 198 each
    - 50 bottles (B2B Bulk Tier) = RM 148 each
    """
    # 1. Determine Tier Pricing & Classifications
    if order_quantity >= 50:
        price_per_bottle = 148.0
        tier_classification = "B2B Bulk Package"
    elif order_quantity >= 2:
        price_per_bottle = 198.0
        tier_classification = "Wholesale Tier"
    else:
        price_per_bottle = 248.0
        tier_classification = "Retail Tier"
        
    subtotal = order_quantity * price_per_bottle
    
    # 2. Check and Apply First-Time Sign-up Rewards
    is_signup_reward_applied = False
    free_reward_bottles = 0
    
    if user_ctx and not user_ctx.get("signup_reward_claimed", True):
        free_reward_bottles = 1
        is_signup_reward_applied = True

    total_delivery_bottles = order_quantity + free_reward_bottles
    
    return {
        "price_per_bottle": price_per_bottle,
        "subtotal": subtotal,
        "free_reward_bottles": free_reward_bottles,
        "tier_classification": tier_classification,
        "total_delivery_bottles": total_delivery_bottles,
        "is_signup_reward_applied": is_signup_reward_applied
    }

def get_user_by_id(user_id, users_df):
    """Helper function to fetch user data from the current state."""
    user_data = users_df[users_df['user_id'] == user_id]
    if not user_data.empty:
        return user_data.iloc[0]
    return None

def calculate_b2b_commission(buyer_id, product_tier, total_bottles, users_df):
    """
    Calculates 2-level commissions for B2B 50 Bottles Buyers.
    Level 1 Upline (Recruiter A from B): RM 5 / bottle
    Level 2 Upline (Upline A from C via B): RM 3 / bottle
    """
    commissions = []
    
    # Check if buyer qualifies under the B2B 50 Bottles package rule
    if product_tier != "B2B_50_BOTTLES" or total_bottles < 50:
        return commissions

    # Fetch buyer profile to find the current upline
    buyer = get_user_by_id(buyer_id, users_df)
    if not buyer or pd.isna(buyer.get('upline_id')) or not buyer.get('upline_id'):
        return commissions  # No upline assigned yet

    # --- LEVEL 1 COMMISSION (Direct Recruiter) ---
    level1_id = buyer['upline_id']
    level1_user = get_user_by_id(level1_id, users_df)
    
    if level1_user:
        l1_earnings = total_bottles * 5.0
        commissions.append({
            "recipient_id": level1_id,
            "recipient_name": level1_user.get('username', 'Unknown'),
            "level": 1,
            "rate_per_bottle": 5.0,
            "amount": l1_earnings,
            "description": f"L1 Bonus from buyer {buyer_id} ({total_bottles} bottles)"
        })
        
        # --- LEVEL 2 COMMISSION (Upline's Recruiter) ---
        level2_id = level1_user.get('upline_id')
        if level2_id and not pd.isna(level2_id):
            level2_user = get_user_by_id(level2_id, users_df)
            if level2_user:
                l2_earnings = total_bottles * 3.0
                commissions.append({
                    "recipient_id": level2_id,
                    "recipient_name": level2_user.get('username', 'Unknown'),
                    "level": 2,
                    "rate_per_bottle": 3.0,
                    "amount": l2_earnings,
                    "description": f"L2 Bonus from buyer {buyer_id} via {level1_id} ({total_bottles} bottles)"
                })
                
    return commissions

def process_b2b_order_earnings(order_id, buyer_id, product_tier, total_bottles, conn):
    """
    Executes database updates for the two-level commissions.
    This fetches the latest user hierarchy directly from the DB to support 
    instances where uplines were edited post-registration.
    """
    # 1. Fetch current users snapshot from database
    users_df = pd.read_sql("SELECT user_id, username, upline_id, role FROM users", conn)
    
    # 2. Compute commissions based on the real-time upline state
    payouts = calculate_b2b_commission(buyer_id, product_tier, total_bottles, users_df)
    
    # 3. Commit payouts to the earnings/wallet table
    cursor = conn.cursor()
    for payout in payouts:
        try:
            # Update Recipient's Wallet Balance
            cursor.execute(
                "UPDATE users SET wallet_balance = wallet_balance + ? WHERE user_id = ?",
                (payout['amount'], payout['recipient_id'])
            )
            
            # Log transaction history
            cursor.execute(
                """
                INSERT INTO transactions (order_id, user_id, amount, type, description, status) 
                VALUES (?, ?, ?, 'COMMISSION', ?, 'COMPLETED')
                """,
                (order_id, payout['recipient_id'], payout['amount'], payout['description'])
            )
        except Exception as e:
            st.error(f"Failed to distribute commission to {payout['recipient_id']}: {e}")
            conn.rollback()
            return False
            
    conn.commit()
    return True
