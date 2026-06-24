"""
PYTHON ANALYSIS STAGE
======================
1. Exploratory Data Analysis (sales trends, category performance)
2. RFM (Recency, Frequency, Monetary) customer segmentation
3. Cohort retention analysis (monthly signup cohorts)
Outputs: PNG charts + rfm_segments.csv + cohort_retention.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 120

OUT = "/home/claude/ecommerce_project"

orders = pd.read_csv(f"{OUT}/orders_clean.csv", parse_dates=["order_date"])
customers = pd.read_csv(f"{OUT}/customers_clean.csv", parse_dates=["signup_date"])

delivered = orders[orders["order_status"] == "Delivered"].copy()

# ============================================================
# 1. EDA — Monthly Revenue Trend
# ============================================================
monthly = delivered.set_index("order_date").resample("ME")["net_amount"].sum().reset_index()
monthly["month_label"] = monthly["order_date"].dt.strftime("%b %Y")

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(monthly["order_date"], monthly["net_amount"], marker="o", color="#2E5266", linewidth=2)
ax.fill_between(monthly["order_date"], monthly["net_amount"], alpha=0.1, color="#2E5266")
ax.set_title("Monthly Revenue Trend (2024–2025)", fontsize=14, fontweight="bold")
ax.set_ylabel("Revenue (₹)")
ax.set_xlabel("")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUT}/chart_monthly_revenue.png")
plt.close()

# ============================================================
# 2. EDA — Revenue by Category
# ============================================================
cat_rev = delivered.groupby("category")["net_amount"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 5))
colors = sns.color_palette("crest", len(cat_rev))
ax.barh(cat_rev.index, cat_rev.values, color=colors)
ax.set_title("Revenue by Category", fontsize=14, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L"))
ax.set_xlabel("Revenue")
plt.tight_layout()
plt.savefig(f"{OUT}/chart_category_revenue.png")
plt.close()

# ============================================================
# 3. RFM Segmentation
# ============================================================
ref_date = delivered["order_date"].max() + pd.Timedelta(days=1)

rfm = delivered.groupby("customer_id").agg(
    recency_days=("order_date", lambda x: (ref_date - x.max()).days),
    frequency=("order_id", "count"),
    monetary=("net_amount", "sum")
).reset_index()

# Score 1-5 for each dimension (5 = best)
rfm["R_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5,4,3,2,1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["M_score"] = pd.qcut(rfm["monetary"], 5, labels=[1,2,3,4,5]).astype(int)

rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

def segment(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    elif r >= 4 and f >= 3:
        return "Loyal Customers"
    elif r >= 4 and f <= 2:
        return "New Customers"
    elif r == 3 and f >= 3:
        return "Potential Loyalists"
    elif r <= 2 and f >= 4 and m >= 4:
        return "At Risk (High Value)"
    elif r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    elif r <= 2:
        return "Hibernating"
    else:
        return "Need Attention"

rfm["segment"] = rfm.apply(segment, axis=1)
rfm = rfm.merge(customers[["customer_id","city","city_tier"]], on="customer_id", how="left")
rfm.to_csv(f"{OUT}/rfm_segments.csv", index=False)

seg_summary = rfm.groupby("segment").agg(
    customers=("customer_id","count"),
    avg_recency=("recency_days","mean"),
    avg_frequency=("frequency","mean"),
    avg_monetary=("monetary","mean"),
    total_revenue=("monetary","sum")
).sort_values("total_revenue", ascending=False).round(1)
seg_summary.to_csv(f"{OUT}/rfm_segment_summary.csv")

print("=== RFM Segment Summary ===")
print(seg_summary)

# RFM segment chart
fig, ax = plt.subplots(figsize=(10, 5.5))
seg_counts = rfm["segment"].value_counts().sort_values(ascending=True)
colors2 = sns.color_palette("crest", len(seg_counts))
ax.barh(seg_counts.index, seg_counts.values, color=colors2)
ax.set_title("Customer Segments (RFM Analysis)", fontsize=14, fontweight="bold")
ax.set_xlabel("Number of Customers")
for i, v in enumerate(seg_counts.values):
    ax.text(v + 5, i, str(v), va="center", fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUT}/chart_rfm_segments.png")
plt.close()

# Treemap-style: revenue contribution by segment (using simple bar instead, treemap needs squarify)
fig, ax = plt.subplots(figsize=(10, 5.5))
seg_rev = seg_summary["total_revenue"].sort_values(ascending=True)
ax.barh(seg_rev.index, seg_rev.values, color=sns.color_palette("flare", len(seg_rev)))
ax.set_title("Revenue Contribution by Customer Segment", fontsize=14, fontweight="bold")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e5:.1f}L"))
plt.tight_layout()
plt.savefig(f"{OUT}/chart_rfm_revenue.png")
plt.close()

# ============================================================
# 4. Cohort Retention Analysis
# ============================================================
df = delivered.merge(customers[["customer_id","signup_date"]], on="customer_id", how="left")
df["cohort_month"] = df["signup_date"].dt.to_period("M")
df["order_month"] = df["order_date"].dt.to_period("M")

# period number = months since cohort signup month
df["period_number"] = (df["order_month"] - df["cohort_month"]).apply(lambda x: x.n)
df = df[df["period_number"] >= 0]  # safety filter

cohort_data = df.groupby(["cohort_month","period_number"])["customer_id"].nunique().reset_index()
cohort_pivot = cohort_data.pivot(index="cohort_month", columns="period_number", values="customer_id")

# True cohort size = total customers who SIGNED UP in that month (not just those who ordered in month 0)
customers["cohort_month"] = customers["signup_date"].dt.to_period("M")
cohort_sizes = customers.groupby("cohort_month")["customer_id"].nunique()
cohort_sizes = cohort_sizes.reindex(cohort_pivot.index)

retention = cohort_pivot.divide(cohort_sizes, axis=0).round(3)

# limit to cohorts with enough history and first 6 periods for readability
retention_display = retention.iloc[:18, :7]  # first ~18 monthly cohorts, 7 months out
retention.to_csv(f"{OUT}/cohort_retention.csv")

fig, ax = plt.subplots(figsize=(11, 8))
sns.heatmap(retention_display, annot=True, fmt=".0%", cmap="YlGnBu", ax=ax,
            cbar_kws={'label': 'Retention Rate'}, vmin=0, vmax=1)
ax.set_title("Monthly Cohort Retention Heatmap", fontsize=14, fontweight="bold")
ax.set_xlabel("Months Since Signup")
ax.set_ylabel("Signup Cohort")
plt.tight_layout()
plt.savefig(f"{OUT}/chart_cohort_retention.png")
plt.close()

print("\n=== Cohort Retention (first 6 cohorts) ===")
print(retention_display.head(6))

# ============================================================
# 5. Payment & order status chart
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
pay_counts = orders["payment_method"].value_counts()
axes[0].pie(pay_counts.values, labels=pay_counts.index, autopct="%1.1f%%",
            colors=sns.color_palette("crest", len(pay_counts)), startangle=90)
axes[0].set_title("Payment Method Distribution", fontweight="bold")

status_counts = orders["order_status"].value_counts()
axes[1].pie(status_counts.values, labels=status_counts.index, autopct="%1.1f%%",
            colors=["#2E8B57","#E07A5F","#81B29A"], startangle=90)
axes[1].set_title("Order Status Breakdown", fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/chart_payment_status.png")
plt.close()

print("\nAll charts and CSVs saved.")
