"""
E-Commerce Sales Analytics Dashboard

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': '#F8F9FA',
    'axes.facecolor': '#F8F9FA',
    'axes.labelsize': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
})
PALETTE = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']

# ── 1. Load & Validate Data ──────────────────────────────────────────────────
print("=" * 60)
print("  E-COMMERCE SALES EDA")
print("=" * 60)

df = pd.read_csv('ecommerce_transactions.csv', parse_dates=['order_date'])
print(f"\n✅ Dataset loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"   Date range : {df['order_date'].min().date()} → {df['order_date'].max().date()}")

# ── 2. Data Cleaning ─────────────────────────────────────────────────────────
print("\n── Data Cleaning ──")
print(f"   Missing values : {df.isnull().sum().sum()}")
print(f"   Duplicate rows : {df.duplicated().sum()}")
df['order_date'] = pd.to_datetime(df['order_date'])
df['month_year'] = df['order_date'].dt.to_period('M')
print(f"   Data types OK  : ✅")

# ── 3. KPI Summary ──────────────────────────────────────────────────────────
delivered = df[df['order_status'] == 'Delivered']
print("\n── KPI Summary (Delivered Orders) ──")
total_rev   = delivered['total_price'].sum()
total_orders = len(delivered)
aov         = delivered['total_price'].mean()
unique_cust = delivered['customer_id'].nunique()
repeat_cust = delivered.groupby('customer_id').size()
repeat_rate = (repeat_cust > 1).mean() * 100

print(f"   Total Revenue        : ₹{total_rev:,.0f}")
print(f"   Total Orders         : {total_orders:,}")
print(f"   Avg Order Value (AOV): ₹{aov:,.2f}")
print(f"   Unique Customers     : {unique_cust:,}")
print(f"   Repeat Customer Rate : {repeat_rate:.1f}%")

# ── 4. Plots ─────────────────────────────────────────────────────────────────

# ── FIG 1: Monthly Revenue Trend ─────────────────────────────────────────────
monthly = (delivered.groupby(['year', 'month'])['total_price']
           .sum().reset_index())
monthly['period'] = pd.to_datetime(monthly[['year','month']].assign(day=1))
monthly = monthly.sort_values('period')

fig, ax = plt.subplots(figsize=(13, 4.5))
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F8F9FA')
ax.fill_between(monthly['period'], monthly['total_price']/1e6, alpha=0.15, color=PALETTE[0])
ax.plot(monthly['period'], monthly['total_price']/1e6, color=PALETTE[0], lw=2.5, marker='o', ms=4)
ax.set_title('Monthly Revenue Trend (2022–2024)')
ax.set_ylabel('Revenue (₹ Millions)')
ax.set_xlabel('')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{x:.1f}M'))
ax.tick_params(axis='x', rotation=30)
plt.tight_layout()
plt.savefig('plot1_monthly_revenue.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n✅ Plot 1 saved: Monthly Revenue Trend")

# ── FIG 2: Revenue by Category ────────────────────────────────────────────────
cat_rev = (delivered.groupby('category')['total_price'].sum()
           .sort_values(ascending=True))

fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor('#F8F9FA'); ax.set_facecolor('#F8F9FA')
bars = ax.barh(cat_rev.index, cat_rev.values / 1e6, color=PALETTE[:len(cat_rev)], edgecolor='white')
for bar, val in zip(bars, cat_rev.values):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'₹{val/1e6:.1f}M', va='center', fontsize=10)
ax.set_title('Revenue by Category')
ax.set_xlabel('Revenue (₹ Millions)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₹{x:.0f}M'))
plt.tight_layout()
plt.savefig('plot2_category_revenue.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 2 saved: Category Revenue")

# ── FIG 3: Customer Segmentation ─────────────────────────────────────────────
seg = delivered.groupby('customer_segment').agg(
    Revenue=('total_price', 'sum'),
    Orders=('order_id', 'count'),
    Customers=('customer_id', 'nunique')
).reset_index()

fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
fig.patch.set_facecolor('#F8F9FA')
fig.suptitle('Customer Segmentation Analysis', fontsize=14, fontweight='bold', y=1.01)

for ax, col, label, color in zip(
        axes,
        ['Revenue', 'Orders', 'Customers'],
        ['Revenue (₹M)', 'Total Orders', 'Unique Customers'],
        PALETTE[:3]):
    vals = seg[col] / (1e6 if col == 'Revenue' else 1)
    bars = ax.bar(seg['customer_segment'], vals, color=color, edgecolor='white', width=0.5)
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + vals.max()*0.02,
                f'{b.get_height():,.1f}' if col=='Revenue' else f'{b.get_height():,.0f}',
                ha='center', fontsize=9)
    ax.set_title(label, fontsize=11)
    ax.set_facecolor('#F8F9FA')

plt.tight_layout()
plt.savefig('plot3_customer_segments.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 3 saved: Customer Segmentation")

# ── FIG 4: Payment Method Share ───────────────────────────────────────────────
pay = delivered.groupby('payment_method')['order_id'].count().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(7, 5))
fig.patch.set_facecolor('#F8F9FA'); ax.set_facecolor('#F8F9FA')
wedges, texts, autotexts = ax.pie(
    pay.values, labels=pay.index, autopct='%1.1f%%',
    colors=PALETTE[:len(pay)], startangle=140,
    wedgeprops=dict(edgecolor='white', linewidth=2))
for at in autotexts:
    at.set_fontsize(9)
ax.set_title('Orders by Payment Method')
plt.tight_layout()
plt.savefig('plot4_payment_methods.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 4 saved: Payment Methods")

# ── FIG 5: Regional Revenue ───────────────────────────────────────────────────
city_rev = (delivered.groupby(['region', 'city'])['total_price']
            .sum().reset_index().sort_values('total_price', ascending=False).head(10))

fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor('#F8F9FA'); ax.set_facecolor('#F8F9FA')
colors = [PALETTE[0] if r == 'South' else PALETTE[1] if r == 'West'
          else PALETTE[2] if r == 'North' else PALETTE[3]
          for r in city_rev['region']]
bars = ax.bar(city_rev['city'], city_rev['total_price']/1e6, color=colors, edgecolor='white')
for b in bars:
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.2,
            f'₹{b.get_height():.1f}M', ha='center', fontsize=9)
ax.set_title('Top Cities by Revenue')
ax.set_ylabel('Revenue (₹ Millions)')
ax.tick_params(axis='x', rotation=30)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=PALETTE[0], label='South'),
                   Patch(facecolor=PALETTE[1], label='West'),
                   Patch(facecolor=PALETTE[2], label='North'),
                   Patch(facecolor=PALETTE[3], label='East')]
ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
plt.tight_layout()
plt.savefig('plot5_city_revenue.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 5 saved: City Revenue")

# ── FIG 6: Discount Impact ────────────────────────────────────────────────────
bins = [-0.001, 0, 0.10, 0.20, 0.30, 1.0]
labels = ['No Discount', '1-10%', '11-20%', '21-30%', '30%+']
delivered = delivered.copy()
delivered['discount_bucket'] = pd.cut(delivered['discount_pct'], bins=bins, labels=labels)

disc = delivered.groupby('discount_bucket', observed=True).agg(
    Orders=('order_id', 'count'),
    AvgOrderValue=('total_price', 'mean')
).reset_index()

fig, ax1 = plt.subplots(figsize=(9, 4.5))
fig.patch.set_facecolor('#F8F9FA'); ax1.set_facecolor('#F8F9FA')
bars = ax1.bar(disc['discount_bucket'], disc['Orders'], color=PALETTE[0], alpha=0.8, label='Orders')
ax2 = ax1.twinx()
ax2.plot(disc['discount_bucket'], disc['AvgOrderValue'], color=PALETTE[3], marker='o', lw=2.5, label='AOV')
ax1.set_title('Discount Bucket vs Orders & AOV')
ax1.set_xlabel('Discount Range')
ax1.set_ylabel('Number of Orders', color=PALETTE[0])
ax2.set_ylabel('Avg Order Value (₹)', color=PALETTE[3])
ax2.set_facecolor('#F8F9FA')
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
plt.tight_layout()
plt.savefig('plot6_discount_impact.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 6 saved: Discount Impact")

# ── FIG 7: YoY Revenue Comparison ────────────────────────────────────────────
yearly = delivered.groupby('year')['total_price'].sum()

fig, ax = plt.subplots(figsize=(7, 4.5))
fig.patch.set_facecolor('#F8F9FA'); ax.set_facecolor('#F8F9FA')
bars = ax.bar(yearly.index.astype(str), yearly.values / 1e6,
              color=PALETTE[:3], edgecolor='white', width=0.5)
for b in bars:
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.5,
            f'₹{b.get_height():.1f}M', ha='center', fontsize=10, fontweight='bold')
ax.set_title('Year-over-Year Revenue')
ax.set_ylabel('Revenue (₹ Millions)')
plt.tight_layout()
plt.savefig('plot7_yoy_revenue.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 7 saved: YoY Revenue")

# ── FIG 8: Order Status Distribution ─────────────────────────────────────────
status = df.groupby('order_status')['order_id'].count().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(7, 4.5))
fig.patch.set_facecolor('#F8F9FA'); ax.set_facecolor('#F8F9FA')
bars = ax.bar(status.index, status.values, color=PALETTE[:len(status)], edgecolor='white', width=0.5)
for b in bars:
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 100,
            f'{b.get_height():,}', ha='center', fontsize=10)
ax.set_title('Order Status Distribution')
ax.set_ylabel('Number of Orders')
plt.tight_layout()
plt.savefig('plot8_order_status.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Plot 8 saved: Order Status")

print("\n" + "="*60)
print("  ALL 8 PLOTS GENERATED SUCCESSFULLY")
print("="*60)
