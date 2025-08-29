# app.py
# ===========================
# STREAMLIT APP: MACHINE REPLACEMENT ANALYSIS (5-YEAR HORIZON)
# Fully commented, with labeled tables and a final decision sentence.
# Includes footer attribution: MADE BY ARPAN ARI(arpancodec) & ALL RIGHTS RESERVED 2025
# ===========================

# ---- Imports: core libraries ----
import streamlit as st           # Streamlit for the UI
import pandas as pd              # Pandas for tables
from dataclasses import dataclass # Lightweight structure for cash flows
from typing import List, Dict, Tuple # Type hints for clarity

# ---- Page setup ----
st.set_page_config(
    page_title="OptiMach — Machine Replacement Analyzer",
    page_icon="🛠️",
    layout="wide"
)

# ---- Title & subtitle ----
st.title("🛠️ OptiMach — Machine Replacement Analyzer")
st.caption("Analyze whether to keep an existing machine or buy a new one, using present-worth analysis over a 5-year horizon.")

# ---- Sidebar inputs: all key parameters are adjustable ----
with st.sidebar:
    st.header("Inputs")

    # Interest rate for discounting cash flows (default 10%)
    i = st.number_input("Interest rate (per year, as decimal)", value=0.10, min_value=0.0, max_value=1.0, step=0.01)

    # Horizon: fixed at 5 years per problem statement, but left editable
    horizon_years = st.number_input("Horizon (years)", value=5, min_value=1, max_value=20, step=1)

    st.markdown("---")
    st.subheader("Existing machine")
    # Existing machine current value and depreciation for next 3 years
    old_start_value = st.number_input("Current market value (now) — $", value=6000, step=500)
    old_depr_per_year = st.number_input("Value loss per year (next 3 years) — $", value=2000, step=500)
    # Old machine operating cost starts at 9000, increasing by 2000 per year of use
    old_op_first = st.number_input("Operating cost: first year — $", value=9000, step=500)
    old_op_increase = st.number_input("Operating cost increase per subsequent year — $", value=2000, step=500)
    # Old machine usable for at most 3 years
    old_max_years = st.number_input("Max years old machine can still be used", value=3, min_value=0, max_value=50, step=1)

    st.markdown("---")
    st.subheader("New machine")
    # New machine cost and depreciation schedule
    new_purchase = st.number_input("New machine purchase price — $", value=22000, step=1000)
    dep_first_two = st.number_input("Depreciation per year (years 1–2) — $", value=3000, step=500)
    dep_after_two = st.number_input("Depreciation per year (year 3+) — $", value=4000, step=500)
    # New machine operating cost starts at 6000, +1000 each year
    new_op_first = st.number_input("New machine operating cost: first year — $", value=6000, step=500)
    new_op_increase = st.number_input("New machine operating cost increase per subsequent year — $", value=1000, step=500)

# ---- Utility: Present value discounting ----
def pv(amount: float, t: float) -> float:
    """
    Present value of a cash flow at time t (years), discounted to t=0 at rate i.
    Timeline convention:
      - Beginning of Year 1 => t = 0
      - End of Year 1       => t = 1
      - Beginning of Year 2 => t = 1
      - ...
    Sign convention:
      - Outflows (costs) are negative
      - Inflows (salvage) are positive
    """
    return amount / ((1 + i) ** t)

# ---- Data class for a single cash flow ----
@dataclass
class CashFlow:
    t: float   # time of cash flow in years
    amt: float # cash amount (+ inflow, - outflow)

# ---- Build the new-machine depreciation schedule list long enough for horizon ----
new_depr_schedule = [dep_first_two, dep_first_two] + [dep_after_two] * (horizon_years + 5)  # padding

# ---- Strategy builder: keep old k years, then new if needed ----
def strategy_cashflows(k_keep_old: int) -> List[CashFlow]:
    """
    Build cash flows for strategy:
      1) Keep existing machine for k years (capped by old_max_years and horizon),
      2) If years remain, buy a new machine at beginning of the next year,
      3) Operating costs at the beginning of each used year,
      4) Salvage inflow when an asset is sold (end of last use).
    """
    cfs: List[CashFlow] = []

    # Years we actually use the old machine (cannot exceed its max or the horizon)
    use_old_years = min(k_keep_old, old_max_years, horizon_years)

    # Old-machine operating costs at beginning of each used year
    for y in range(1, use_old_years + 1):
        cost = old_op_first + (y - 1) * old_op_increase  # escalating op cost
        cfs.append(CashFlow(t=y - 1, amt=-cost))         # beginning of year y

    # Sell old when we stop using it:
    # If k=0, sell immediately at t=0; else at end of year 'use_old_years' (t=use_old_years)
    sell_time = 0 if use_old_years == 0 else use_old_years
    old_value_after_k = max(old_start_value - old_depr_per_year * use_old_years, 0)
    if old_value_after_k > 0:
        cfs.append(CashFlow(t=sell_time, amt=+old_value_after_k))

    # Remaining years after old usage
    years_remaining = horizon_years - use_old_years

    # If years remain, buy and use new machine
    if years_remaining > 0:
        # Purchase at beginning of next year (t = use_old_years)
        cfs.append(CashFlow(t=use_old_years, amt=-new_purchase))

        # New-machine operating costs for each used year, beginning of each year
        for y in range(1, years_remaining + 1):
            cost = new_op_first + (y - 1) * new_op_increase
            cfs.append(CashFlow(t=use_old_years + (y - 1), amt=-cost))

        # Salvage value of new at the end of the horizon
        total_depr = sum(new_depr_schedule[:years_remaining])
        new_salvage = max(new_purchase - total_depr, 0)
        cfs.append(CashFlow(t=use_old_years + years_remaining, amt=+new_salvage))

    return cfs

# ---- NPV of a given strategy ----
def pv_of_strategy(k_keep_old: int) -> Tuple[float, List[CashFlow]]:
    """
    Returns NPV (sum of discounted cash flows; + inflows reduce net cost) and the cash flows.
    """
    cfs = strategy_cashflows(k_keep_old)
    npv_val = sum(pv(cf.amt, cf.t) for cf in cfs)
    return npv_val, cfs

# ---- Evaluate strategies for k = 0..3 (keep old first k years) ----
results: Dict[int, Dict] = {}
for k in range(0, 4):
    npv_val, cfs = pv_of_strategy(k)
    results[k] = {"NPV": npv_val, "CashFlows": cfs}

# ---- Summary table: both NPV and Present Worth Cost (PWC) for clarity ----
summary_rows = []
for k, res in results.items():
    npv_here = res["NPV"]                         # usually negative (net cost)
    pwc_here = -npv_here                          # flip sign to show cost as positive
    summary_rows.append({
        "Keep old first (years) k": k, 
        f"NPV at {i:.1%} ($, inflows +)": round(npv_here, 2),
        f"Present Worth Cost at {i:.1%} ($)": round(pwc_here, 2)  # smaller is cheaper
    })
summary_df = pd.DataFrame(summary_rows).sort_values("Keep old first (years) k")

st.subheader("📊 Summary: Present Values by Strategy")
st.caption("NPV uses + for inflows and – for outflows; it’s typically negative (net cost). For readability, we also show Present Worth Cost (PWC) as a positive number — lower is better.")
st.dataframe(summary_df, use_container_width=True)

# ---- Select best strategy: highest NPV (equivalently, lowest PWC) ----
best_k = max(results.keys(), key=lambda kk: results[kk]["NPV"])
best_npv = results[best_k]["NPV"]
best_pwc = -best_npv

# ---- Detailed cash-flow table for the best strategy ----
def describe_cfs(cfs: List[CashFlow]) -> pd.DataFrame:
    """
    Convert list of cash flows to a detailed table with time, amount, and discounted present value.
    """
    rows = []
    for cf in sorted(cfs, key=lambda x: x.t):
        rows.append({
            "Time t (years)": cf.t,
            "Cash Flow ($) [+:inflow, −:outflow]": cf.amt,
            "Present Value at t=0 ($)": round(pv(cf.amt, cf.t), 2)
        })
    return pd.DataFrame(rows)

st.subheader(f"🧾 Detailed Cash Flows — Best Strategy (keep old for k={best_k} year(s))")
st.caption("This table shows every purchase, operating cost, and salvage with its discounted present value.")
st.dataframe(describe_cfs(results[best_k]["CashFlows"]), use_container_width=True)

# ---- Optional: details for all strategies ----
with st.expander("Show detailed cash flows for all strategies (k = 0, 1, 2, 3)"):
    for k in sorted(results.keys()):
        st.markdown(f"**Strategy k = {k}** (keep old for {k} year(s))")
        st.dataframe(describe_cfs(results[k]["CashFlows"]), use_container_width=True)

# ---- Final decision sentence (clear and actionable) ----
if best_k == 0:
    decision_sentence = (
        f"✅ At an interest rate of {i:.1%}, **sell the existing machine now and purchase a new one immediately**. "
        f"(Present Worth Cost ≈ ${best_pwc:,.2f}.)"
    )
else:
    decision_sentence = (
        f"✅ At an interest rate of {i:.1%}, **keep the existing machine for {best_k} year(s)** and "
        f"**purchase a new machine at the beginning of year {best_k + 1}**. "
        f"(Present Worth Cost ≈ ${best_pwc:,.2f}.)"
    )
st.success(decision_sentence)

# ---- Footer: attribution ----
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; font-size: 0.9rem; opacity: 0.8;">
        <strong>MADE BY ARPAN ARI (arpancodec) &nbsp;•&nbsp; ALL RIGHTS RESERVED 2025</strong>
    </div>
    """,
    unsafe_allow_html=True
)
