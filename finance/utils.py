# def format_currency(amount):
#     return f"₹{amount:,.0f}"

# def validate_inputs(allocation_sum, sip, years):
#     if allocation_sum != 100:
#         return False, f"Total allocation must be 100% (Current: {allocation_sum}%)"
#     if sip <= 0 or years <= 0:
#         return False, "SIP amount and tenure must be greater than 0."
#     return True, ""

import locale

def format_currency(amount):
    """
    Formats a number into the Indian Numbering System (Lakhs/Crores).
    Example: 100000 -> ₹1,00,000
    """
    # Convert amount to integer for clean display
    amount = int(round(amount))
    s = str(amount)
    
    if len(s) <= 3:
        return f"₹{s}"
    
    # Split the last 3 digits and the rest
    last_three = s[-3:]
    remaining = s[:-3]
    
    # Group the remaining digits in pairs
    out = ""
    while len(remaining) > 2:
        out = "," + remaining[-2:] + out
        remaining = remaining[:-2]
    
    return f"₹{remaining}{out},{last_three}"

def validate_inputs(allocation_sum, sip, years):
    if allocation_sum != 100:
        return False, f"Total allocation must be 100% (Current: {allocation_sum}%)"
    if sip <= 0 or years <= 0:
        return False, "SIP amount and tenure must be greater than 0."
    return True, ""
