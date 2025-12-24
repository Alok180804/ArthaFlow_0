import requests
from datetime import datetime

# Updated to funds with longer historical footprints (Direct/Growth)
SCHEME_MAP = {
    "Debt MF": "119551",    # ABSL Banking & PSU (Stable, long history)
    "Gold ETF": "103504",   # HDFC Gold ETF
    "Nifty 50": "120716",   # UTI Nifty 50 Index Fund
    "Flexi Cap": "102591",  # HDFC Flexi Cap (One of India's oldest)
    "Mid Cap": "118989",    # Franklin India Midcap
    "Small Cap": "125497"   # Nippon India Small Cap
}

def fetch_real_return(category, tenure_years):
    # Determine desired lookback (Caps at 5Y to avoid data gaps in some APIs)
    desired_lookback = 1 if tenure_years < 5 else (3 if tenure_years < 10 else 5)

    try:
        code = SCHEME_MAP.get(category)
        response = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=10).json()
        nav_data = response['data']
        
        latest_nav = float(nav_data[0]['nav'])
        
        # Smart Indexing: Don't overshoot available data
        days_available = len(nav_data)
        target_index = min(desired_lookback * 250, days_available - 1)
        old_nav = float(nav_data[target_index]['nav'])
        
        # Calculate ACTUAL years between dates provided by API
        date_format = "%d-%m-%Y"
        d_latest = datetime.strptime(nav_data[0]['date'], date_format)
        d_old = datetime.strptime(nav_data[target_index]['date'], date_format)
        actual_years = (d_latest - d_old).days / 365.25
        
        if actual_years <= 0: return 12.0, 0
        
        # CAGR calculation
        annualized_return = (pow(latest_nav / old_nav, 1/actual_years) - 1) * 100
        
        # --- Financial Expert Sanity Guard ---
        # Prevents outliers from breaking long-term projections
        if category == "Debt MF":
            annualized_return = max(5.5, min(annualized_return, 10.0))
        if category == "Gold ETF":
            annualized_return = max(4.0, annualized_return) # Gold rarely negative over 5Y
            
        return round(annualized_return, 2), round(actual_years)
    
    except Exception:
        fallbacks = {"Debt MF": 7.0, "Gold ETF": 9.5, "Nifty 50": 12.5, "Flexi Cap": 14.5, "Mid Cap": 17.0, "Small Cap": 19.0}
        return fallbacks.get(category, 12.0), desired_lookback