E-Commerce Customer & Sales Analytics — India (2024–2025)

A full end-to-end data analytics project analyzing customer behavior and sales performance on a simulated Indian e-commerce platform across a 24-month period.

Tools: Excel · SQL (SQLite) · Python (Pandas, Matplotlib, Seaborn) · Tableau Public

📊 View Live Tableau Dashboard


📌 Project Overview

MetricValueTotal Orders7,600 (raw) → 6,699 (after cleaning)Total Customers2,400Cities Covered28 (across Tier 1, 2, 3)Product Categories7Time PeriodJan 2024 – Dec 2025Total Revenue (Delivered)₹91.03 Lakh


🔑 Key Findings


Electronics is the top revenue category (₹29.6L, 32.6% of revenue) driven by high average order value despite not being the most-ordered category
Champions segment (304 customers, 12.7% of base) generates 28.5% of total revenue — identified via RFM segmentation
Tier 1 cities (Mumbai, Delhi, Bengaluru) contribute 76.9% of revenue
UPI dominates payment methods at 37.4% of all orders
19.85% return rate flagged as a key business risk — concentrated in Books, Home & Kitchen, and Electronics
Cohort retention analysis shows most customers churn within 2 months of signup, with only 10–15% retained by month 6



🗂️ Project Structure

├── data/
│   ├── orders_raw.csv           # Raw orders data (with injected quality issues)
│   ├── customers_raw.csv        # Raw customer data
│   ├── orders_clean.csv         # Cleaned orders data
│   └── customers_clean.csv      # Cleaned customer data
│
├── analysis/
│   ├── sql_analysis.sql         # 13 SQL queries (revenue, category, city, RFM, etc.)
│   ├── python_analysis.py       # RFM segmentation + cohort retention analysis
│   ├── rfm_segments.csv         # RFM scores and segments per customer
│   ├── rfm_segment_summary.csv  # Summary stats by segment
│   └── cohort_retention.csv     # Monthly cohort retention matrix
│
├── charts/
│   ├── chart_monthly_revenue.png
│   ├── chart_category_revenue.png
│   ├── chart_rfm_segments.png
│   ├── chart_rfm_revenue.png
│   ├── chart_cohort_retention.png
│   └── chart_payment_status.png
│
└── Ecommerce_Analytics_Report.docx   # Full case study report (7 pages)


🔧 Pipeline

Stage 1 — Excel (Data Cleaning)

Raw data contained intentional real-world quality issues:


114 duplicate order records → removed by order_id
Inconsistent city names (e.g., "Bangalore" → "Bengaluru") → standardized
Null values in discount_pct and payment_method → filled with 0 / "Unknown"
Inconsistent category casing → standardized to title case
Invalid quantity (zero) → corrected to 1
Mixed date formats → standardized to YYYY-MM-DD


Stage 2 — SQL (Analysis)

13 queries covering:


Overall revenue, AOV, order count
Monthly revenue trend
Revenue by category and city
Top 10 cities, city tier breakdown
Payment method distribution
Order status and return rate by category
Top 10 products by revenue
RFM base query (recency, frequency, monetary per customer)


Stage 3 — Python (Modeling)

python# RFM Segmentation
rfm["R_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5,4,3,2,1])
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5])
rfm["M_score"] = pd.qcut(rfm["monetary"], 5, labels=[1,2,3,4,5])


8 actionable customer segments: Champions, Loyal Customers, Potential Loyalists, New Customers, At Risk (High Value), Need Attention, Hibernating, Lost
Monthly cohort retention heatmap using signup date as cohort anchor


Stage 4 — Tableau (Dashboard)

Published interactive dashboard with:


Monthly revenue trend (2024–2025)
Revenue by category and city
RFM segment distribution and revenue contribution
Cohort retention heatmap
Filters: city tier, payment method, order status, customer segment



💡 Business Recommendations


Win-back campaign for "At Risk (High Value)" segment (181 customers, ₹14.2L historical revenue)
Investigate return rate (19.85%) — likely product description mismatches in Books and Electronics
Tier 2 city promotions — currently only 18.5% of revenue despite large population base
Loyalty incentive for New Customers — cohort data shows most churn within 2 months
UPI-linked offers to drive repeat purchases at near-zero friction



🚀 How to Run

bash# Install dependencies
pip install pandas numpy matplotlib seaborn

# Run Python analysis
python analysis/python_analysis.py

# Open SQL queries in DB Browser for SQLite
# Load orders_clean.csv and customers_clean.csv as tables


👩‍💻 Author

Ragha Akshaya


GitHub: github.com/akshaya0027
LinkedIn: linkedin.com/in/ragha-akshaya-30b0a42bb
Tableau: Tableau Public Profile
Email: raghaakshaya941@gmail.com
