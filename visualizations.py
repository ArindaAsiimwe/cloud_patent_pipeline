#!/usr/bin/env python3
"""
Patent Intelligence Data Pipeline - DATA VISUALIZATIONS
Generates charts and graphs for patent analysis from database
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

OUTPUT_FOLDER = "output"

Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

# Connect to database
print("Connecting to database...")
db_paths = [
    "/kaggle/working/database/patents.db",
    "database/patents.db"
]

conn = None
for db_path in db_paths:
    if os.path.exists(db_path):
        print(f"✓ Found database at {db_path}")
        conn = sqlite3.connect(db_path)
        break

if conn is None:
    print("✗ Database not found!")
    print("Make sure to run patent_pipeline.py on Kaggle first to generate the database.")
    exit(1)

# Load data from database using SQL queries
print("\nLoading data from database...")
try:
    # Q1: Top Inventors
    df_top_inventors = pd.read_sql("""
        SELECT 
            i.inventor_id,
            i.name,
            i.country,
            COUNT(DISTINCT pir.patent_id) as patent_count
        FROM inventors i
        LEFT JOIN patent_inventor_relationships pir ON i.inventor_id = pir.inventor_id
        GROUP BY i.inventor_id
        ORDER BY patent_count DESC
        LIMIT 100
    """, conn)
    
    # Q2: Top Companies
    df_top_companies = pd.read_sql("""
        SELECT 
            c.company_id,
            c.name,
            COUNT(DISTINCT pcr.patent_id) as patent_count
        FROM companies c
        LEFT JOIN patent_company_relationships pcr ON c.company_id = pcr.company_id
        GROUP BY c.company_id
        ORDER BY patent_count DESC
        LIMIT 100
    """, conn)
    
    # Q3: Countries
    df_country_trends = pd.read_sql("""
        SELECT 
            i.country,
            COUNT(DISTINCT pir.patent_id) as patent_count,
            ROUND(100.0 * COUNT(DISTINCT pir.patent_id) / (SELECT COUNT(DISTINCT patent_id) FROM patent_inventor_relationships), 2) as percentage
        FROM inventors i
        JOIN patent_inventor_relationships pir ON i.inventor_id = pir.inventor_id
        GROUP BY i.country
        ORDER BY patent_count DESC
    """, conn)
    
    # Q4: Trends Over Time
    df_patents_by_year = pd.read_sql("""
        SELECT 
            year,
            COUNT(*) as patent_count
        FROM patents
        WHERE year IS NOT NULL AND year > 1975
        GROUP BY year
        ORDER BY year ASC
    """, conn)
    
    # Load full tables for summary statistics
    df_patents = pd.read_sql("SELECT * FROM patents", conn)
    df_inventors = pd.read_sql("SELECT * FROM inventors", conn)
    
    print("✓ Data loaded successfully from database")
except Exception as e:
    print(f"✗ Error: {e}")
    conn.close()
    exit(1)

# VISUALIZATION 1: TOP INVENTORS
print("\n[1/6] Creating Top Inventors visualization...")

q_inventors = df_top_inventors.head(15)

fig, ax = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("husl", len(q_inventors))
bars = ax.barh(q_inventors['name'], q_inventors['patent_count'], color=colors)

ax.set_xlabel('Number of Patents', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Inventors by Patent Count', fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()

# Add value labels on bars
for i, (name, value) in enumerate(zip(q_inventors['name'], q_inventors['patent_count'])):
    ax.text(value + 0.5, i, f'{int(value)}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig(f"{OUTPUT_FOLDER}/top_inventors_chart.png", dpi=300, bbox_inches='tight')
print("      ✓ Saved: top_inventors_chart.png")
plt.close()

# VISUALIZATION 2: TOP COMPANIES
print("[2/6] Creating Top Companies visualization...")

q_companies = df_top_companies.head(15)

if not q_companies.empty:
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("husl", len(q_companies))
    bars = ax.barh(q_companies['name'], q_companies['patent_count'], color=colors)
    
    ax.set_xlabel('Number of Patents', fontsize=12, fontweight='bold')
    ax.set_title('Top 15 Companies by Patent Count', fontsize=14, fontweight='bold', pad=20)
    ax.invert_yaxis()
    
    # Add value labels on bars
    for i, (name, value) in enumerate(zip(q_companies['name'], q_companies['patent_count'])):
        ax.text(value + 0.5, i, f'{int(value)}', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_FOLDER}/top_companies_chart.png", dpi=300, bbox_inches='tight')
    print("      ✓ Saved: top_companies_chart.png")
    plt.close()
else:
    print("      ⚠ No company data available")

# VISUALIZATION 3: PATENTS BY YEAR (TRENDS)
print("[3/6] Creating Patent Trends visualization...")

q_trends = df_patents_by_year.sort_values('year')

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(q_trends['year'], q_trends['patent_count'], linewidth=2.5, marker='o', 
        markersize=4, color='#2E86AB')
ax.fill_between(q_trends['year'], q_trends['patent_count'], alpha=0.3, color='#2E86AB')

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Patents', fontsize=12, fontweight='bold')
ax.set_title('Patent Filing Trends Over Time', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{OUTPUT_FOLDER}/patent_trends.png", dpi=300, bbox_inches='tight')
print("      ✓ Saved: patent_trends.png")
plt.close()

# VISUALIZATION 4: TOP COUNTRIES (PIE CHART)
print("[4/6] Creating Countries Distribution visualization...")

q_countries = df_country_trends.head(12)

fig, ax = plt.subplots(figsize=(10, 8))
colors = sns.color_palette("Set3", len(q_countries))
wedges, texts, autotexts = ax.pie(q_countries['patent_count'], 
                                    labels=q_countries['country'],
                                    autopct='%1.1f%%',
                                    colors=colors,
                                    startangle=90)

for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(9)

for text in texts:
    text.set_fontsize(10)
    text.set_fontweight('bold')

ax.set_title('Patent Distribution by Country (Top 12)', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(f"{OUTPUT_FOLDER}/countries_distribution.png", dpi=300, bbox_inches='tight')
print("      ✓ Saved: countries_distribution.png")
plt.close()

# VISUALIZATION 5: PATENTS BY COUNTRY (BAR CHART)
print("[5/6] Creating Countries Bar Chart visualization...")

fig, ax = plt.subplots(figsize=(12, 6))
colors = sns.color_palette("husl", len(q_countries))
bars = ax.bar(range(len(q_countries)), q_countries['patent_count'], color=colors)

ax.set_xticks(range(len(q_countries)))
ax.set_xticklabels(q_countries['country'], rotation=45, ha='right', fontweight='bold')
ax.set_ylabel('Number of Patents', fontsize=12, fontweight='bold')
ax.set_title('Patents by Country (Top 12)', fontsize=14, fontweight='bold', pad=20)

# Add value labels on bars
for i, value in enumerate(q_countries['patent_count']):
    ax.text(i, value + 100, f'{int(value)}', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(f"{OUTPUT_FOLDER}/countries_bar_chart.png", dpi=300, bbox_inches='tight')
print("      ✓ Saved: countries_bar_chart.png")
plt.close()

# VISUALIZATION 6: RECENT TRENDS (LAST 10 YEARS)
print("[6/6] Creating Recent Trends visualization...")

q_recent = df_patents_by_year.tail(10).sort_values('year')

fig, ax = plt.subplots(figsize=(12, 6))
colors_gradient = sns.color_palette("coolwarm", len(q_recent))
bars = ax.bar(q_recent['year'].astype(str), q_recent['patent_count'], color=colors_gradient)

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Patents', fontsize=12, fontweight='bold')
ax.set_title('Patent Filings - Recent 10 Years', fontsize=14, fontweight='bold', pad=20)

# Add value labels on bars
for i, (year, value) in enumerate(zip(q_recent['year'], q_recent['patent_count'])):
    ax.text(i, value + 50, f'{int(value)}', ha='center', fontweight='bold')

plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{OUTPUT_FOLDER}/recent_trends.png", dpi=300, bbox_inches='tight')
print("      ✓ Saved: recent_trends.png")
plt.close()

# SUMMARY STATISTICS DASHBOARD
print("\nGenerating Summary Dashboard...")

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Get summary data
total_patents = len(df_patents)
total_inventors = len(df_inventors)
avg_patents_per_inventor = df_top_inventors['patent_count'].mean()

# 1. Top Inventors (smaller version)
ax1 = fig.add_subplot(gs[0, 0])
top_inv = df_top_inventors.head(8)
ax1.barh(top_inv['name'], top_inv['patent_count'], color=sns.color_palette("Blues_r", len(top_inv)))
ax1.set_xlabel('Patents')
ax1.set_title('Top 8 Inventors', fontweight='bold')
ax1.invert_yaxis()

# 2. Recent trends
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(q_recent['year'], q_recent['patent_count'], marker='o', linewidth=2, color='#FF6B6B')
ax2.fill_between(q_recent['year'], q_recent['patent_count'], alpha=0.3, color='#FF6B6B')
ax2.set_xlabel('Year')
ax2.set_ylabel('Patents')
ax2.set_title('Patents - Last 10 Years', fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. Top countries
ax3 = fig.add_subplot(gs[1, :])
top_countries = q_countries.head(10)
ax3.bar(range(len(top_countries)), top_countries['patent_count'], 
        color=sns.color_palette("husl", len(top_countries)))
ax3.set_xticks(range(len(top_countries)))
ax3.set_xticklabels(top_countries['country'], rotation=45, ha='right')
ax3.set_ylabel('Number of Patents')
ax3.set_title('Top 10 Countries by Patents', fontweight='bold')

# 4. Key Metrics
ax4 = fig.add_subplot(gs[2, :])
ax4.axis('off')

metrics_text = f"""
KEY STATISTICS

Total Patents: {total_patents:,}
Total Inventors: {total_inventors:,}
Average Patents per Inventor: {avg_patents_per_inventor:.2f}
"""

ax4.text(0.5, 0.5, metrics_text, transform=ax4.transAxes,
         fontsize=12, verticalalignment='center', horizontalalignment='center',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
         family='monospace', fontweight='bold')

fig.suptitle('Patent Intelligence Dashboard', fontsize=16, fontweight='bold', y=0.995)
plt.savefig(f"{OUTPUT_FOLDER}/dashboard.png", dpi=300, bbox_inches='tight')
print("      ✓ Saved: dashboard.png")
plt.close()

# COMPLETION SUMMARY

print("\n" + "=" * 80)
print("✓ VISUALIZATIONS COMPLETE")
print("=" * 80)

# Close database connection
conn.close()

print("\n VISUALIZATIONS CREATED:")
print("  ✓ top_inventors_chart.png")
if not df_top_companies.empty:
    print("  ✓ top_companies_chart.png")
print("  ✓ patent_trends.png")
print("  ✓ countries_distribution.png")
print("  ✓ countries_bar_chart.png")
print("  ✓ recent_trends.png")
print("  ✓ dashboard.png")

print("\nAll visualizations saved to: output/")
print("\n" + "=" * 80)
