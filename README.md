# 🛠️ OptiMach — Machine Replacement Analyzer

**Made by Arpan Ari (arpancodec) • All Rights Reserved 2025**

---

## 📌 Overview
OptiMach helps companies decide **whether to keep an existing machine or purchase a new one**, using **Present Worth Analysis** over a 5-year horizon.  

It compares different strategies:
- Keep the **existing machine** for `k` years (k = 0, 1, 2, 3)  
- Then (if needed) buy a **new machine** to cover the remaining years  

All purchases, operating costs, and salvage values are discounted at the chosen **interest rate** (default = 10%).

---

## 🚀 Features
- Interactive **Streamlit UI**
- Adjustable parameters:
  - Interest rate
  - Horizon (default = 5 years)
  - Existing machine costs & depreciation
  - New machine purchase, depreciation & operating costs
- 📊 **Summary Table**: Shows NPV and Present Worth Cost (PWC) by strategy
- 🧾 **Detailed Cash Flow Table** for the best strategy
- 🔍 Optional detailed tables for all strategies
- ✅ **Final recommendation sentence** for easy decision-making
- Clean footer with attribution

---

