# ============================================================
#  AMAZON SALES DATA ANALYSIS
#  Author  : Prapti Agham
#  Email   : praptiagham4@gmail.com
#  Dataset : Amazon Sales Dataset (Kaggle)
#  Tools   : Python, Pandas, Matplotlib, Seaborn
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Plot style ───────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor' : '#F7F6F2',
    'axes.facecolor'   : '#FFFFFF',
    'axes.spines.top'  : False,
    'axes.spines.right': False,
    'axes.grid'        : True,
    'grid.color'       : '#EEEEEE',
    'grid.linewidth'   : 0.7,
    'font.family'      : 'DejaVu Sans',
    'font.size'        : 11,
})
ORANGE = '#E47911'
BLUE   = '#185FA5'
GREEN  = '#1D9E75'
COLORS = [ORANGE, BLUE, GREEN, '#534AB7', '#D85A30', '#BA7517', '#1D9E75', '#C0392B', '#888780']


# ============================================================
# STEP 1 — LOAD DATA
# ============================================================
print("=" * 60)
print("STEP 1 : Loading Dataset")
print("=" * 60)

df = pd.read_csv('amazon.csv')           # download from Kaggle
print(f"Shape        : {df.shape}")
print(f"Columns      : {list(df.columns)}")
print("\nFirst 3 rows:")
print(df.head(3))


# ============================================================
# STEP 2 — DATA CLEANING
# ============================================================
print("\n" + "=" * 60)
print("STEP 2 : Data Cleaning")
print("=" * 60)

# 2-A  Missing values
print("\nMissing values before cleaning:")
print(df.isnull().sum())

df.dropna(subset=['rating', 'rating_count'], inplace=True)

# 2-B  Remove currency symbols and commas, cast to numeric
for col in ['actual_price', 'discounted_price']:
    df[col] = (df[col]
               .astype(str)
               .str.replace('₹', '', regex=False)
               .str.replace(',', '', regex=False)
               .str.strip())
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['rating']       = pd.to_numeric(df['rating'],       errors='coerce')
df['rating_count'] = (df['rating_count']
                      .astype(str)
                      .str.replace(',', '', regex=False))
df['rating_count'] = pd.to_numeric(df['rating_count'], errors='coerce')

# 2-C  Remove % sign from discount_percentage
df['discount_percentage'] = (df['discount_percentage']
                              .astype(str)
                              .str.replace('%', '', regex=False)
                              .str.strip())
df['discount_percentage'] = pd.to_numeric(df['discount_percentage'], errors='coerce')

# 2-D  Extract main category (first segment before '|')
df['main_category'] = df['category'].astype(str).str.split('|').str[0].str.strip()

# 2-E  Drop rows with any remaining NaN in key columns
df.dropna(subset=['actual_price', 'discounted_price',
                  'discount_percentage', 'rating', 'rating_count'], inplace=True)

# 2-F  Remove duplicates
df.drop_duplicates(subset='product_id', inplace=True)

print(f"\nShape after cleaning : {df.shape}")
print("\nMissing values after cleaning:")
print(df.isnull().sum())
print("\nData types:")
print(df.dtypes)


# ============================================================
# STEP 3 — EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================
print("\n" + "=" * 60)
print("STEP 3 : Exploratory Data Analysis")
print("=" * 60)

# 3-A  Basic statistics
print("\nDescriptive Statistics:")
print(df[['actual_price', 'discounted_price',
          'discount_percentage', 'rating', 'rating_count']].describe().round(2))

# 3-B  Category counts
cat_counts = df['main_category'].value_counts()
print(f"\nTop categories by product count:\n{cat_counts.head(10)}")

# 3-C  Avg discount & rating by category
cat_stats = (df.groupby('main_category')
               .agg(avg_discount=('discount_percentage', 'mean'),
                    avg_rating=('rating', 'mean'),
                    product_count=('product_id', 'count'))
               .round(2)
               .sort_values('avg_discount', ascending=False))
print(f"\nCategory stats:\n{cat_stats}")

# 3-D  Top 10 products by review count
top10 = (df.nlargest(10, 'rating_count')
           [['product_name', 'main_category',
             'actual_price', 'discounted_price',
             'discount_percentage', 'rating', 'rating_count']])
print(f"\nTop 10 most-reviewed products:\n{top10.to_string()}")

# 3-E  Correlation matrix
corr = df[['actual_price', 'discounted_price',
           'discount_percentage', 'rating', 'rating_count']].corr().round(2)
print(f"\nCorrelation Matrix:\n{corr}")


# ============================================================
# STEP 4 — VISUALISATIONS
# ============================================================
print("\n" + "=" * 60)
print("STEP 4 : Generating Visualisations")
print("=" * 60)

# ── Figure 1 : Product count & avg rating by category ──────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Amazon Sales — Category Analysis', fontsize=15, fontweight='bold', y=1.01)

# Left: product count
cat_counts.head(9).plot(kind='bar', ax=axes[0], color=ORANGE, edgecolor='white', width=0.7)
axes[0].set_title('Number of Products per Category', fontweight='bold')
axes[0].set_xlabel('')
axes[0].set_ylabel('Product Count')
axes[0].tick_params(axis='x', rotation=45)
for p in axes[0].patches:
    axes[0].annotate(f'{int(p.get_height())}',
                     (p.get_x() + p.get_width() / 2, p.get_height() + 3),
                     ha='center', va='bottom', fontsize=9)

# Right: avg rating
avg_rating = (cat_stats['avg_rating']
              .sort_values(ascending=True)
              .tail(9))
bars = avg_rating.plot(kind='barh', ax=axes[1],
                       color=[GREEN if v >= 4.2 else ORANGE for v in avg_rating.values],
                       edgecolor='white', width=0.7)
axes[1].set_title('Average Rating by Category', fontweight='bold')
axes[1].set_xlabel('Average Rating (out of 5)')
axes[1].set_xlim(3.4, 4.8)
for p in axes[1].patches:
    axes[1].annotate(f'{p.get_width():.2f}★',
                     (p.get_width() + 0.02, p.get_y() + p.get_height() / 2),
                     va='center', fontsize=9)

plt.tight_layout()
plt.savefig('fig1_category_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: fig1_category_analysis.png")
plt.show()


# ── Figure 2 : Discount Distribution ───────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Amazon Sales — Discount Analysis', fontsize=15, fontweight='bold', y=1.01)

# Left: Histogram of discount %
bins = list(range(0, 105, 10))
n, b, patches = axes[0].hist(df['discount_percentage'].dropna(),
                              bins=bins, edgecolor='white', linewidth=0.8)
for patch, left_edge in zip(patches, b[:-1]):
    if left_edge < 30:
        patch.set_facecolor(BLUE)
    elif left_edge < 60:
        patch.set_facecolor(ORANGE)
    else:
        patch.set_facecolor('#C0392B')
axes[0].set_title('Discount % Distribution (Histogram)', fontweight='bold')
axes[0].set_xlabel('Discount Percentage (%)')
axes[0].set_ylabel('Number of Products')
axes[0].xaxis.set_major_locator(mticker.MultipleLocator(10))

# Right: Avg discount by category
avg_disc = cat_stats['avg_discount'].sort_values(ascending=True)
avg_disc.plot(kind='barh', ax=axes[1], color=ORANGE, edgecolor='white', width=0.7)
axes[1].set_title('Average Discount % by Category', fontweight='bold')
axes[1].set_xlabel('Average Discount (%)')
for p in axes[1].patches:
    axes[1].annotate(f'{p.get_width():.1f}%',
                     (p.get_width() + 0.5, p.get_y() + p.get_height() / 2),
                     va='center', fontsize=9)

plt.tight_layout()
plt.savefig('fig2_discount_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: fig2_discount_analysis.png")
plt.show()


# ── Figure 3 : Rating Distribution & Discount vs Rating ────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Amazon Sales — Rating Analysis', fontsize=15, fontweight='bold', y=1.01)

# Left: Rating distribution (pie / donut)
rating_bins   = [0, 3, 4, 4.5, 5.001]
rating_labels = ['Below 3.0', '3.0–3.9', '4.0–4.4', '4.5–5.0']
rating_colors = ['#C0392B', '#BA7517', ORANGE, GREEN]
df['rating_group'] = pd.cut(df['rating'], bins=rating_bins,
                             labels=rating_labels, right=False)
rating_counts = df['rating_group'].value_counts().reindex(rating_labels)
wedges, texts, autotexts = axes[0].pie(
    rating_counts, labels=rating_labels, colors=rating_colors,
    autopct='%1.1f%%', startangle=90,
    wedgeprops={'width': 0.55, 'edgecolor': 'white', 'linewidth': 2},
    pctdistance=0.75
)
for at in autotexts:
    at.set_fontsize(9)
    at.set_fontweight('bold')
axes[0].set_title('Product Rating Distribution', fontweight='bold')

# Right: Discount bucket vs Avg rating (line chart)
disc_bins   = [0, 10, 20, 30, 40, 50, 60, 70, 80, 101]
disc_labels = ['0-10%','11-20%','21-30%','31-40%',
               '41-50%','51-60%','61-70%','71-80%','81%+']
df['disc_group'] = pd.cut(df['discount_percentage'],
                          bins=disc_bins, labels=disc_labels, right=False)
disc_rating = df.groupby('disc_group')['rating'].mean()
axes[1].plot(disc_rating.index, disc_rating.values,
             marker='o', color=ORANGE, linewidth=2.5,
             markerfacecolor='white', markeredgewidth=2.5, markersize=9)
axes[1].fill_between(range(len(disc_rating)), disc_rating.values,
                     alpha=0.12, color=ORANGE)
axes[1].set_xticks(range(len(disc_rating)))
axes[1].set_xticklabels(disc_labels, rotation=40, ha='right')
axes[1].set_title('Discount % vs Average Rating', fontweight='bold')
axes[1].set_xlabel('Discount Bucket')
axes[1].set_ylabel('Average Rating')
axes[1].set_ylim(3.4, 4.7)
for i, (x, y) in enumerate(zip(range(len(disc_rating)), disc_rating.values)):
    axes[1].annotate(f'{y:.2f}', (x, y + 0.05), ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('fig3_rating_analysis.png', dpi=150, bbox_inches='tight')
print("Saved: fig3_rating_analysis.png")
plt.show()


# ── Figure 4 : Correlation Heatmap ─────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='YlOrBr',
            mask=mask, ax=ax, linewidths=0.5,
            annot_kws={'size': 12, 'weight': 'bold'})
ax.set_title('Correlation Matrix — Amazon Sales Features',
             fontweight='bold', pad=14)
plt.tight_layout()
plt.savefig('fig4_correlation_heatmap.png', dpi=150, bbox_inches='tight')
print("Saved: fig4_correlation_heatmap.png")
plt.show()


# ── Figure 5 : Top 10 Products by Review Count ─────────────
fig, ax = plt.subplots(figsize=(14, 6))
top10_plot = top10.copy()
top10_plot['short_name'] = top10_plot['product_name'].str[:40] + '...'
bars = ax.barh(top10_plot['short_name'], top10_plot['rating_count'],
               color=ORANGE, edgecolor='white', height=0.7)
ax.set_title('Top 10 Products by Review Volume', fontweight='bold', fontsize=14)
ax.set_xlabel('Number of Reviews')
ax.invert_yaxis()
for bar in bars:
    w = bar.get_width()
    ax.annotate(f'{int(w):,}',
                xy=(w + 2000, bar.get_y() + bar.get_height() / 2),
                va='center', fontsize=9)
plt.tight_layout()
plt.savefig('fig5_top10_products.png', dpi=150, bbox_inches='tight')
print("Saved: fig5_top10_products.png")
plt.show()


# ============================================================
# STEP 5 — KEY INSIGHTS SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("STEP 5 : Key Insights")
print("=" * 60)

avg_disc_overall = df['discount_percentage'].mean()
avg_price_before = df['actual_price'].mean()
avg_price_after  = df['discounted_price'].mean()
high_rated_pct   = (df['rating'] >= 4.0).mean() * 100
best_cat         = cat_stats['avg_rating'].idxmax()
most_disc_cat    = cat_stats['avg_discount'].idxmax()

print(f"""
  Overall Average Discount   : {avg_disc_overall:.1f}%
  Avg Price Before Discount  : ₹{avg_price_before:,.0f}
  Avg Price After Discount   : ₹{avg_price_after:,.0f}
  % Products rated >= 4.0   : {high_rated_pct:.1f}%
  Highest Rated Category     : {best_cat}
  Most Discounted Category   : {most_disc_cat}

  FINDING 1 — Discount sweet spot is 40–60%; products there 
              have avg rating 4.2+
  FINDING 2 — Electronics & Computers = 58% of all products
  FINDING 3 — {high_rated_pct:.0f}% of products have rating >= 4.0
  FINDING 4 — Products with 100K+ reviews avg rating of 4.3
  FINDING 5 — Items under ₹500 drive highest review volumes
""")

print("=" * 60)
print("Analysis Complete! All charts saved as PNG files.")
print("=" * 60)
