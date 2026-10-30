# ======================================================================================================================
# FILE: mlm_logic.py - FULL PRODUCTION MLM NETWORK PRICING & LOGISTICS DISTRIBUTION LOGIC ENGINE
# ======================================================================================================================
import logging

# Configure logic engine logger tracking for production audits
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLM_Logic_Engine")

def calculate_bottle_order(quantity: int, current_user_data: dict = None) -> dict:
    """
    Executes tiered wholesale pricing logic, validates B2B target quotas, and determines 
    centralized company incentive rewards for new MLM member sign-ups.

    Operational Parameters:
    -----------------------
    - quantity (int): Enforced boundary between 1 to 50 bottles per checkout instance.
    - current_user_data (dict): Profile state variables loaded directly from Google Firestore.

    Pricing Tiers Enforced:
    -----------------------
    - Retail Tier (1 Bottle): RM 248 / bottle
    - Group Tier (2 to 49 Bottles): RM 198 / bottle
    - B2B Bulk Merchant Tier (Exactly 50 Bottles): RM 148 / bottle

    B2B Downline Distribution Rules:
    --------------------------------
    - Ordering 50 bottles registers the user as a B2B Merchant Agent.
    - B2B Agents unlock a recruitment capacity of 8 new downline network members.
    - B2B Agents handle physical product seeding by passing out 6 bottles to each recruit.
    - To support centralized operations, the company dispatches a 1-time free reward bottle 
      directly to new members during initial profile verification setup.
    """
    logger.info(f"Processing order payload logic execution for quantity block size: {quantity}")

    # 1. Enforce boundary values on input attributes (Minimum 1 bottle, Maximum 50 bottles)
    sanitized_quantity = int(quantity)
    if sanitized_quantity < 1:
        sanitized_quantity = 1
    elif sanitized_quantity > 50:
        sanitized_quantity = 50

    # 2. Evaluate specific tiered price vectors based on quantity bounds
    if sanitized_quantity == 1:
        price_per_bottle = 248
        tier_label = "Retail Consumer Node"
    elif 2 <= sanitized_quantity <= 49:
        price_per_bottle = 198
        tier_label = "Group Distribution Tier"
    else:  # Exactly 50 Bottles
        price_per_bottle = 148
        tier_label = "B2B Bulk Merchant Agent"

    # Compute financial subtotal values
    order_subtotal = sanitized_quantity * price_per_bottle
    is_b2b_active = (sanitized_quantity == 50)

    # 3. Assess the One-Time Corporate Registration Incentive Reward Condition
    # If the user profile context exists and 'signup_reward_claimed' flag evaluates to False,
    # the company grants 1 free promotional bottle via centralized logistics dispatch lines.
    free_reward_bottles = 0
    apply_signup_bonus = False

    if current_user_data:
        # Check if the user database profile state has explicitly locked out the reward already
        has_claimed = current_user_data.get("signup_reward_claimed", False)
        if not has_claimed:
            free_reward_bottles = 1
            apply_signup_bonus = True
            logger.info("New network registration detected: Appending 1-time corporate incentive reward bottle.")
    else:
        # Graceful default state fallback if connection context drops out or operates inside sandbox
        logger.warning("Profile context not verified by Firestore service layers. Defaulting reward calculation rules.")

    # 4. Construct complete network quota assignment metrics
    total_physical_delivery_volume = sanitized_quantity + free_reward_bottles
    
    if is_b2b_active:
        recruitment_quota_string = (
            "AUTHORIZED Privileges: Eligible to recruit up to 8 new members. "
            "Distribution strategy allows seeding 6 stock bottles per downline candidate node. "
            "Recruits can complete onboarding profiles via registration portal lines."
        )
    else:
        recruitment_quota_string = (
            "RESTRICTED Privileges: Retail tier accounts are locked from downlines tracking. "
            "Purchase exactly 50 bottles in a single checkout event to open B2B Merchant privileges."
        )

    # 5. Return calculated output data map parameters straight to Streamlit frontend views
    return {
        "ordered_quantity": sanitized_quantity,
        "price_per_bottle": price_per_bottle,
        "subtotal": order_subtotal,
        "tier_classification": tier_label,
        "free_reward_bottles": free_reward_bottles,
        "total_delivery_bottles": total_physical_delivery_volume,
        "is_signup_reward_applied": apply_signup_bonus,
        "network_b2b_recruitment_quota": recruitment_quota_string,
        "system_status_code": "ENGINE_CALCULATION_SUCCESS"
    }
