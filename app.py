import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
# Note: Ensure your local finance module is in the same directory or PYTHONPATH
try:
    from finance.portfolio import simulate_portfolio
    from finance.utils import format_currency
    from finance.data_fetcher import fetch_real_return
except ImportError:
    # Fallback functions for demonstration if local modules aren't found
    def format_currency(val): return f"₹{val:,.0f}"
    def fetch_real_return(cat, tenure): return 12.0, tenure
    def simulate_portfolio(sip, ten, step, funds):
        total_inv = sip * 12 * ten # Simplistic fallback
        return [sip * 100] * (ten * 12), [{"name": f["name"], "final_value": 100000} for f in funds], total_inv

# UI Setup
st.set_page_config(page_title="ArthaFlow SIP Planner", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    
    /* Container for metrics to ensure white text is visible */
    [data-testid="stMetric"] {
        padding: 15px;
        border-radius: 10px;
        color: white !important;
    }
    
    /* Force metric labels and values to white */
    [data-testid="stMetricLabel"] p { color: #f8fafc !important; }
    [data-testid="stMetricValue"] div { color: #ffffff !important; font-size: 1.8rem; font-weight: 700; }
    
    /* Clean, flat tab styling */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 24px; 
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent !important;
        border: none !important;
        padding: 0px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { 
        color: #ef4444 !important;
        border-bottom: 2px solid #ef4444 !important;
    }

    /* Change primary button color to red for selection state */
    button[kind="primary"] {
        background-color: #ef4444 !important;
        border-color: #ef4444 !important;
        color: white !important;
    }
    button[kind="primary"]:hover {
        background-color: #dc2626 !important;
        border-color: #dc2626 !important;
    }

    /* Card-like container for parameters */
    .param-container {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: DATA TRANSPARENCY ---
with st.sidebar:
    st.title("🔍 Data Transparency")
    st.markdown("""
    ### Source: MFAPI.in
    We use real-time market data to calculate **CAGR (Compound Annual Growth Rate)** based on historical NAVs.
    
    **Fund Mappings:**
    - **Debt MF:** Liquid/Overnight Funds
    - **Gold ETF:** Nippon India Gold BeES
    - **Nifty 50:** UTI Nifty 50 Index Fund
    - **Flexi Cap:** Parag Parikh Flexi Cap
    - **Mid Cap:** HDFC Mid-Cap Opportunities
    - **Small Cap:** Nippon India Small Cap
    
    *Returns are calculated using the requested tenure or the maximum available history.*
    """)
    st.divider()
    st.info("**⚠️ Disclaimer:** Simulations use historical averages. Past performance does not guarantee future returns.")

# --- STATE MANAGEMENT ---
if 'selected_profile' not in st.session_state:
    st.session_state.update({
        "Debt MF": 30, "Gold ETF": 10, "Nifty 50": 30, 
        "Flexi Cap": 20, "Mid Cap": 5, "Small Cap": 5,
        "selected_profile": "Balanced"
    })

def select_profile(name, d, g, n, f, m, s):
    st.session_state.update({
        "Debt MF": d, "Gold ETF": g, "Nifty 50": n, 
        "Flexi Cap": f, "Mid Cap": m, "Small Cap": s,
        "selected_profile": name
    })

# --- MAIN CONTENT ---
st.title("🎯 ArthaFlow: Strategic Asset Planner")

# --- SECTION 1: CORE PARAMETERS (MAIN SPACE) ---
st.subheader("1. Investment Parameters")
with st.container():
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    with c1:
        base_sip = st.number_input("Monthly SIP Amount (₹)", min_value=500, value=20000, step=1000)
    with c2:
        tenure = st.number_input("Tenure (Years)", min_value=1, max_value=50, value=15)
    with c3:
        step_up = st.number_input("Annual Step-up (%)", min_value=0, max_value=50, value=10)
    with c4:
        st.write("Live Data")
        use_live_data = st.toggle("Use Live CAGR", value=True, label_visibility="collapsed")
        if use_live_data:
            st.caption(f"Sync: {datetime.now().strftime('%H:%M')}")

st.divider()

# --- SECTION 2: ALLOCATION & PROJECTION ---
tab1, tab2 = st.tabs(["📋 Strategy & Allocation", "📈 Projection Analysis"])

with tab1:
    st.subheader("Select Risk Profile")
    p1, p2, p3 = st.columns(3)
    if p1.button("🛡️ Conservative", use_container_width=True, type="primary" if st.session_state.selected_profile == "Conservative" else "secondary"):
        select_profile("Conservative", 60, 10, 20, 10, 0, 0); st.rerun()
    if p2.button("⚖️ Balanced", use_container_width=True, type="primary" if st.session_state.selected_profile == "Balanced" else "secondary"):
        select_profile("Balanced", 30, 10, 30, 20, 5, 5); st.rerun()
    if p3.button("🚀 Aggressive", use_container_width=True, type="primary" if st.session_state.selected_profile == "Aggressive" else "secondary"):
        select_profile("Aggressive", 10, 5, 25, 20, 20, 20); st.rerun()

    input_col, chart_col = st.columns([2, 1])
    categories = ["Debt MF", "Gold ETF", "Nifty 50", "Flexi Cap", "Mid Cap", "Small Cap"]
    funds = []
    total_alloc = 0

    with input_col:
        sc1, sc2 = st.columns(2)
        for i, cat in enumerate(categories):
            col = sc1 if i < 3 else sc2
            with col:
                alloc = st.number_input(f"{cat} (%)", 0, 100, st.session_state[cat], key=f"in_{cat}")
                if use_live_data:
                    ret, period = fetch_real_return(cat, tenure)
                    st.caption(f"Adaptive Return: **{ret}%**")
                    current_ret = ret
                else:
                    current_ret = st.number_input(f"{cat} Est. Return (%)", 0.0, 40.0, 12.0, key=f"manual_{cat}")
                
                funds.append({"name": cat, "allocation_pct": alloc, "return_pct": current_ret})
                total_alloc += alloc

    with chart_col:
        if total_alloc > 0:
            df_pie = pd.DataFrame(funds)
            # Use a thinner donut with a clean, high-contrast palette
            fig = px.pie(df_pie, values='allocation_pct', names='name', hole=0.75,
                         color_discrete_sequence=px.colors.sequential.RdBu_r)
            
            fig.update_traces(
                textposition='outside', 
                textinfo='percent',
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            
            fig.update_layout(
                height=400, 
                margin=dict(t=0, b=40, l=0, r=0), 
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                # Centered Annotation inside the hole
                annotations=[dict(text='Portfolio<br>Mix', x=0.5, y=0.5, font_size=16, showarrow=False, font_family="sans-serif")]
            )
            st.plotly_chart(fig, use_container_width=True)
            if total_alloc != 100:
                st.error(f"Total: {total_alloc}% (Must be 100%)")
            else:
                st.success("Allocation Balanced")

with tab2:
    if total_alloc == 100:
        history, fund_details, total_invested = simulate_portfolio(base_sip, tenure, step_up, funds)
        final_corpus = history[-1]
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Maturity Value", format_currency(final_corpus))
        m2.metric("Total Invested", format_currency(total_invested))
        m3.metric("Wealth Wealth Gain", format_currency(final_corpus - total_invested))
        m4.metric("Growth Multiplier", f"{(final_corpus/total_invested):.2f}x")

        # Visualizations
        st.subheader("Growth Projection")
        yearly_data = history[11::12]
        chart_df = pd.DataFrame({
            "Year": range(1, tenure + 1), 
            "Corpus": yearly_data
        }).set_index("Year")
        st.area_chart(chart_df, color="#ef4444")

        # Breakdown - Expanded by default
        with st.expander("Detailed Asset Performance", expanded=True):
            df_funds = pd.DataFrame(fund_details)
            df_funds["Allocation"] = [f"{f['allocation_pct']}%" for f in funds]
            df_funds["Return"] = [f"{f['return_pct']}%" for f in funds]
            df_funds["Final Value"] = df_funds["final_value"].apply(format_currency)
            st.dataframe(df_funds[["name", "Allocation", "Return", "Final Value"]], use_container_width=True)
            
        # Advisor Note
        inflation_rate = 0.06
        real_val = final_corpus / ((1 + inflation_rate) ** tenure)
        st.info(f"💡 **Advisor Note:** Adjusted for 6% inflation, your corpus of {format_currency(final_corpus)} will have the purchasing power of **{format_currency(real_val)}** today.")
    else:
        st.warning("Adjust your allocation to 100% in the 'Strategy' tab to see projections.")