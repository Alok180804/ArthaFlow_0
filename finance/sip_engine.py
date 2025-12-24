def calculate_fund_growth(initial_sip, years, step_up_pct, annual_return_pct):
    """
    Calculates month-by-month growth for a single fund with annual step-up.
    Returns a list of monthly corpus values.
    """
    monthly_rate = (1 + (annual_return_pct / 100)) ** (1 / 12) - 1
    step_up_factor = 1 + (step_up_pct / 100)
    
    corpus = 0.0
    total_invested = 0.0
    monthly_history = []
    
    for month in range(1, (years * 12) + 1):
        # Determine current year (0-indexed) to apply step-up
        year_index = (month - 1) // 12
        current_sip = initial_sip * (step_up_factor ** year_index)
        
        # Calculation logic: Invest then grow
        corpus = (corpus + current_sip) * (1 + monthly_rate)
        total_invested += current_sip
        
        # Store data points (optional: store only year-ends for charts, 
        # but we'll return all for flexibility)
        monthly_history.append(corpus)
        
    return monthly_history, total_invested