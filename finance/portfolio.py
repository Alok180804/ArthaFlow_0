from .sip_engine import calculate_fund_growth

def simulate_portfolio(total_sip, years, step_up_pct, funds_config):
    """
    funds_config: List of dicts {name, allocation_pct, return_pct}
    """
    combined_history = None
    fund_results = []
    total_portfolio_invested = 0.0

    for fund in funds_config:
        # Calculate fund-specific SIP based on allocation
        fund_sip = total_sip * (fund['allocation_pct'] / 100)
        
        history, invested = calculate_fund_growth(
            fund_sip, years, step_up_pct, fund['return_pct']
        )
        
        total_portfolio_invested += invested
        fund_results.append({
            "name": fund['name'],
            "final_value": history[-1],
            "total_invested": invested
        })
        
        # Aggregate history for the chart
        if combined_history is None:
            combined_history = [0.0] * len(history)
        
        for i in range(len(history)):
            combined_history[i] += history[i]
            
    return combined_history, fund_results, total_portfolio_invested