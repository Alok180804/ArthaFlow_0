import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from finance.portfolio import simulate_portfolio
from finance.utils import format_currency, validate_inputs
from finance.data_fetcher import fetch_real_return

# UI Setup
st.set_page_config(page_title="ArthaFlow SIP Planner", layout="wide")

# --- 1. CONDENSED DISCLAIMER & DATA SOURCE ---
st.warning(
    "**⚠️ Disclaimer:** Simulation based on constant returns; not a guarantee of future results. "
    "Market data fetched in real-time from **MFAPI.in**."
)

# Initialize Default State (Balanced - Selected by Default)
if 'selected_profile' not in st.session_state:
    st.session_state.update({
        "Debt MF": 30, "Gold ETF": 10, "Nifty 50": 30, 
        "Flexi Cap": 20, "Mid Cap": 5, "Small Cap": 5,
        "selected_profile": "Balanced"
    })

# CSS for Flat UI (No white boxes/shadows)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    [data-testid="stMetric"] {
        border: none;
        box-shadow: none;
        background-color: transparent !important;
    }
    .stInfo {
        background-color: #f0f7ff;
        border: none;
        color: #1e3a8a;
    }
    </style>
    """, unsafe_allow_html=True)

def select_profile(name, d, g, n, f, m, s):
    st.session_state.update({
        "Debt MF": d, "Gold ETF": g, "Nifty 50": n, 
        "Flexi Cap": f, "Mid Cap": m, "Small Cap": s,
        "selected_profile": name
    })

st.title("🎯 ArthaFlow: Strategic Asset Planner")

# --- Sidebar: Global Settings ---
st.sidebar.header("1. Core Parameters")
base_sip = st.sidebar.number_input("Total Monthly SIP (₹)", min_value=0, value=20000, step=1000)
tenure = st.sidebar.number_input("Tenure (Years)", min_value=1, max_value=50, value=15)
step_up = st.sidebar.number_input("Annual Step-up (%)", min_value=0, value=10)

st.sidebar.header("2. Market Analysis")
use_live_data = st.sidebar.toggle("Use Adaptive Live Returns", value=True)

if use_live_data:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.sidebar.caption(f"🔄 **Last Sync:** {current_time} (2025)")

# --- Layout: Tabs ---
tab1, tab2 = st.tabs(["📋 Asset Allocation", "📈 Projection & Insight"])

with tab1:
    st.subheader("Configure Your Portfolio Strategy")
    
    # Risk Profile Quick Select (Balanced is Primary by Default)
    col_p1, col_p2, col_p3 = st.columns(3)
    
    if col_p1.button("🛡️ Conservative", use_container_width=True, type="primary" if st.session_state.selected_profile == "Conservative" else "secondary"):
        select_profile("Conservative", 60, 10, 20, 10, 0, 0)
        st.rerun()
    if col_p2.button("⚖️ Balanced", use_container_width=True, type="primary" if st.session_state.selected_profile == "Balanced" else "secondary"):
        select_profile("Balanced", 30, 10, 30, 20, 5, 5)
        st.rerun()
    if col_p3.button("🚀 Aggressive", use_container_width=True, type="primary" if st.session_state.selected_profile == "Aggressive" else "secondary"):
        select_profile("Aggressive", 10, 5, 25, 20, 20, 20)
        st.rerun()

    st.divider()

    input_col, chart_col = st.columns([2, 1])
    
    with input_col:
        categories = ["Debt MF", "Gold ETF", "Nifty 50", "Flexi Cap", "Mid Cap", "Small Cap"]
        funds = []
        total_alloc = 0
        
        sub_col1, sub_col2 = st.columns(2)
        for i, cat in enumerate(categories):
            target_col = sub_col1 if i < 3 else sub_col2
            with target_col:
                alloc = st.number_input(f"{cat} (%)", 0, 100, st.session_state[cat], key=f"in_{cat}")
                if use_live_data:
                    ret, period = fetch_real_return(cat, tenure)
                    st.caption(f"Market {period}Y CAGR: **{ret}%**")
                    current_ret = ret
                else:
                    current_ret = st.number_input(f"{cat} Return (%)", 0.0, 40.0, 12.0, key=f"manual_{cat}")
                
                funds.append({"name": cat, "allocation_pct": alloc, "return_pct": current_ret})
                total_alloc += alloc

    with chart_col:
        if total_alloc > 0:
            df_pie = pd.DataFrame(funds)
            fig = px.pie(df_pie, values='allocation_pct', names='name', hole=0.6,
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5),
                margin=dict(t=0, b=0, l=0, r=0), # Tight margins
                height=280,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    if total_alloc == 100 and base_sip > 0:
        history, fund_details, total_invested = simulate_portfolio(base_sip, tenure, step_up, funds)
        
        final_corpus = history[-1]
        wealth_gain = final_corpus - total_invested
        profit_pct = (wealth_gain / total_invested) * 100
        multiplier = final_corpus / total_invested

        # --- Dashboard Metrics ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Final Corpus", format_currency(final_corpus))
        m2.metric("Total Invested", format_currency(total_invested))
        m3.metric("Wealth Gain", format_currency(wealth_gain))
        m4.metric("Absolute Profit", f"{profit_pct:.1f}%")

        # --- Expert Summary Box ---
        st.info("### 🧐 ArthaFlow Advisor Analysis")
        
        # Standard India Inflation (6%)
        inflation_rate = 0.06
        real_value = final_corpus / ((1 + inflation_rate) ** tenure)
        
        # Calculating the avg period for the note (getting it from the last fetched fund)
        _, display_period = fetch_real_return("Nifty 50", tenure)
        
        st.write(f"""
        Your strategy is projected to grow your wealth **{multiplier:.1f} times** over the next {tenure} years. 

        **The Inflation Reality:**
        While the total sum of **{format_currency(final_corpus)}** sounds large, inflation will erode its value. 
        In today's purchasing power, this is equivalent to **{format_currency(real_value)}**. 

        **Advisor's Note:**
        Because your return basis is calculated using an adaptive **{display_period}Y CAGR** from real market data (via MFAPI.in), your projection is grounded in historical reality. Your current **{st.session_state.selected_profile}** stance is {'beating' if profit_pct > 100 else 'matching'} the cost of living.
        """)

        # --- Visuals ---
        st.subheader("Wealth Accumulation Curve")
        yearly_data = history[11::12]
        chart_df = pd.DataFrame({"Year": range(1, tenure + 1), "Portfolio Value": yearly_data}).set_index("Year")
        st.line_chart(chart_df)
        
        

        # --- Table ---
        st.subheader("Asset-wise Performance Breakdown")
        df_funds = pd.DataFrame(fund_details)
        df_funds["Allocation"] = [f"{f['allocation_pct']}%" for f in funds]
        df_funds["Return Basis"] = [f"{f['return_pct']}%" for f in funds]
        df_funds["Maturity Value"] = df_funds["final_value"].apply(format_currency)
        st.table(df_funds[["name", "Allocation", "Return Basis", "Maturity Value"]])
    else:
        st.info("Please ensure the total allocation equals 100% in the 'Asset Allocation' tab.")