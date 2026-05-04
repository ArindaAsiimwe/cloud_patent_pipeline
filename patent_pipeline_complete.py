#!/usr/bin/env python3
"""
Patent Intelligence Data Pipeline
Complete script to load, clean, and analyze US patent data from USPTO
"""

import pandas as pd
import sqlite3
import json
from datetime import datetime
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths - adjust these to your folder structure
DATA_FOLDER = "data"  # Where you put g_patent.tsv, g_patent_abstract.tsv, etc.
OUTPUT_FOLDER = "output"
DB_PATH = "database/patents.db"

# Create output folders if they don't exist
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
Path("database").mkdir(exist_ok=True)

# ============================================================================
# PHASE 1: LOAD DATA FROM TSV FILES
# ============================================================================

print("=" * 70)
print("PHASE 1: LOADING DATA FROM TSV FILES")
print("=" * 70)

# Load g_patent (main patent data)
print("\n1. Loading g_patent.tsv (this might take a minute)...")
try:
    patents_df = pd.read_csv(
        f"{DATA_FOLDER}/g_patent.tsv",
        sep="\t",
        dtype={"patent_id": str},
        low_memory=False
    )
    print(f"   ✓ Loaded {len(patents_df):,} patents")
    print(f"   Columns: {list(patents_df.columns)[:5]}...")
except Exception as e:
    print(f"   ✗ Error loading g_patent.tsv: {e}")
    exit(1)

# Load g_patent_abstract (descriptions) - this is large, so we'll be careful
print("\n2. Loading g_patent_abstract.tsv (this is 1.7 GB, might take 2-5 minutes)...")
try:
    abstract_df = pd.read_csv(
        f"{DATA_FOLDER}/g_patent_abstract.tsv",
        sep="\t",
        dtype={"patent_id": str},
        low_memory=False
    )
    print(f"   ✓ Loaded {len(abstract_df):,} patent abstracts")
except Exception as e:
    print(f"   ✗ Error loading g_patent_abstract.tsv: {e}")
    print("   Continuing without abstracts...")
    abstract_df = pd.DataFrame()

# Load g_persistent_assignee if available (companies)
print("\n3. Looking for g_persistent_assignee.tsv...")
if os.path.exists(f"{DATA_FOLDER}/g_persistent_assignee.tsv"):
    try:
        assignee_df = pd.read_csv(
            f"{DATA_FOLDER}/g_persistent_assignee.tsv",
            sep="\t",
            dtype={"patent_id": str},
            low_memory=False
        )
        print(f"   ✓ Loaded {len(assignee_df):,} company assignments")
        print(f"     Columns: {list(assignee_df.columns)}")
    except Exception as e:
        print(f"   ✗ Error loading assignee file: {e}")
        assignee_df = pd.DataFrame()
else:
    print("   ⚠ g_persistent_assignee.tsv not found - will skip company analysis")
    assignee_df = pd.DataFrame()

# ============================================================================
# PHASE 2: CLEAN THE DATA
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 2: CLEANING DATA")
print("=" * 70)

# Clean patents dataframe
print("\n1. Cleaning patent data...")
print(f"   Before: {len(patents_df)} patents")

# Remove duplicates
patents_df = patents_df.drop_duplicates(subset=["patent_id"])
print(f"   After removing duplicates: {len(patents_df)} patents")

# Keep only essential columns
essential_cols = ["patent_id", "patent_title", "patent_date"]
available_cols = [col for col in essential_cols if col in patents_df.columns]
patents_df = patents_df[available_cols]

# Handle missing values
patents_df["patent_title"] = patents_df["patent_title"].fillna("Unknown Title")
patents_df["patent_date"] = patents_df["patent_date"].fillna("Unknown")

# Extract year from patent_date
patents_df["year"] = pd.to_datetime(
    patents_df["patent_date"],
    errors="coerce"
).dt.year

print(f"   ✓ Patent data cleaned")

# Clean abstracts
if not abstract_df.empty:
    print("\n2. Cleaning abstract data...")
    abstract_df = abstract_df.drop_duplicates(subset=["patent_id"])
    abstract_df["patent_abstract"] = abstract_df["patent_abstract"].fillna("No abstract available")
    print(f"   ✓ Abstract data cleaned ({len(abstract_df):,} abstracts)")

# Clean assignees (companies)
if not assignee_df.empty:
    print("\n3. Cleaning company data...")
    
    # Rename columns to be consistent
    if "assignee_id" in assignee_df.columns and "disambig_assignee_organization" in assignee_df.columns:
        assignee_df = assignee_df[["patent_id", "assignee_id", "disambig_assignee_organization"]]
        assignee_df.columns = ["patent_id", "assignee_id", "assignee_name"]
    elif "assignee_organization" in assignee_df.columns:
        assignee_df = assignee_df[["patent_id", "assignee_organization"]]
        assignee_df.columns = ["patent_id", "assignee_name"]
    
    assignee_df = assignee_df.drop_duplicates(subset=["patent_id"])
    assignee_df["assignee_name"] = assignee_df["assignee_name"].fillna("Unknown Company")
    print(f"   ✓ Company data cleaned")

# ============================================================================
# PHASE 3: CREATE DATABASE & SCHEMA
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 3: CREATING DATABASE")
print("=" * 70)

# Connect to database (will create if doesn't exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(f"\n1. Creating tables in {DB_PATH}...")

# Drop existing tables if they exist (for clean rebuild)
cursor.execute("DROP TABLE IF EXISTS patent_abstracts")
cursor.execute("DROP TABLE IF EXISTS patent_companies")
cursor.execute("DROP TABLE IF EXISTS patents")

# Create patents table
cursor.execute("""
    CREATE TABLE patents (
        patent_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        patent_date TEXT,
        year INTEGER
    )
""")

# Create abstracts table
cursor.execute("""
    CREATE TABLE patent_abstracts (
        patent_id TEXT PRIMARY KEY,
        abstract TEXT,
        FOREIGN KEY(patent_id) REFERENCES patents(patent_id)
    )
""")

# Create companies table
cursor.execute("""
    CREATE TABLE patent_companies (
        patent_id TEXT,
        assignee_name TEXT,
        FOREIGN KEY(patent_id) REFERENCES patents(patent_id)
    )
""")

conn.commit()
print("   ✓ Tables created")

# Load data into database
print("\n2. Loading data into database...")

# Insert patents
patents_df_db = patents_df[["patent_id", "patent_title", "patent_date", "year"]].copy()
patents_df_db.columns = ["patent_id", "title", "patent_date", "year"]
patents_df_db.to_sql("patents", conn, if_exists="append", index=False)
print(f"   ✓ Inserted {len(patents_df_db):,} patents")

# Insert abstracts
if not abstract_df.empty:
    abstract_df_db = abstract_df[["patent_id", "patent_abstract"]].copy()
    abstract_df_db.columns = ["patent_id", "abstract"]
    abstract_df_db.to_sql("patent_abstracts", conn, if_exists="append", index=False)
    print(f"   ✓ Inserted {len(abstract_df_db):,} abstracts")

# Insert companies
if not assignee_df.empty:
    assignee_df_db = assignee_df[["patent_id", "assignee_name"]].copy()
    assignee_df_db.to_sql("patent_companies", conn, if_exists="append", index=False)
    print(f"   ✓ Inserted {len(assignee_df_db):,} company assignments")

conn.commit()
print("   ✓ Database populated successfully")

# ============================================================================
# PHASE 4: RUN SQL QUERIES
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 4: RUNNING ANALYSIS QUERIES")
print("=" * 70)

# Q1: Patents by Year (Trends Over Time)
print("\nQ1: Patents Granted by Year...")
q1_result = pd.read_sql("""
    SELECT year, COUNT(*) as patent_count
    FROM patents
    WHERE year IS NOT NULL AND year > 1975
    GROUP BY year
    ORDER BY year DESC
    LIMIT 50
""", conn)
print(f"   ✓ Retrieved {len(q1_result)} years of data")

# Q2: Top Companies (if data available)
print("\nQ2: Top Companies by Patents...")
if not assignee_df.empty:
    q2_result = pd.read_sql("""
        SELECT assignee_name, COUNT(*) as patent_count
        FROM patent_companies
        GROUP BY assignee_name
        ORDER BY patent_count DESC
        LIMIT 20
    """, conn)
    print(f"   ✓ Top company: {q2_result.iloc[0]['assignee_name']} ({q2_result.iloc[0]['patent_count']} patents)")
else:
    q2_result = pd.DataFrame()
    print("   ⚠ Company data not available")

# Q3: Patents by Decade
print("\nQ3: Patents by Decade...")
q3_result = pd.read_sql("""
    SELECT 
        (year / 10 * 10) as decade,
        COUNT(*) as patent_count
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY decade
    ORDER BY decade DESC
""", conn)
print(f"   ✓ Retrieved data for {len(q3_result)} decades")

# Q4: Recent Patents (Last 5 Years)
print("\nQ4: Recent Patents (Last 5 Years)...")
q4_result = pd.read_sql("""
    SELECT year, COUNT(*) as patent_count
    FROM patents
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year DESC
    LIMIT 5
""", conn)
print(f"   ✓ Retrieved recent patent data")

# Q5: Patents with Details (Sample JOIN)
print("\nQ5: Patent Details with Abstracts...")
q5_result = pd.read_sql("""
    SELECT 
        p.patent_id,
        p.title,
        p.year,
        a.abstract
    FROM patents p
    LEFT JOIN patent_abstracts a ON p.patent_id = a.patent_id
    LIMIT 100
""", conn)
print(f"   ✓ Retrieved {len(q5_result)} patent details")

# Q6: Company-Patent Summary
print("\nQ6: Company Patent Statistics...")
if not assignee_df.empty:
    q6_result = pd.read_sql("""
        SELECT 
            assignee_name,
            COUNT(*) as total_patents,
            MIN(p.year) as first_patent_year,
            MAX(p.year) as latest_patent_year
        FROM patent_companies pc
        JOIN patents p ON pc.patent_id = p.patent_id
        GROUP BY assignee_name
        ORDER BY total_patents DESC
        LIMIT 20
    """, conn)
    print(f"   ✓ Retrieved company statistics")
else:
    q6_result = pd.DataFrame()

# Q7: Patent Count Statistics
print("\nQ7: Patent Statistics...")
q7_result = pd.read_sql("""
    SELECT 
        COUNT(*) as total_patents,
        MIN(year) as earliest_year,
        MAX(year) as latest_year,
        ROUND(AVG(year), 0) as avg_year
    FROM patents
    WHERE year IS NOT NULL
""", conn)
total_patents = q7_result.iloc[0]["total_patents"]
print(f"   ✓ Total patents: {int(total_patents):,}")

# ============================================================================
# PHASE 5: GENERATE REPORTS
# ============================================================================

print("\n" + "=" * 70)
print("PHASE 5: GENERATING REPORTS")
print("=" * 70)

# 1. CONSOLE REPORT
print("\n" + "=" * 70)
print("PATENT INTELLIGENCE REPORT")
print("=" * 70)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

print(f"Total Patents: {int(total_patents):,}")
print(f"Years Covered: {int(q7_result.iloc[0]['earliest_year'])} - {int(q7_result.iloc[0]['latest_year'])}\n")

print("PATENTS GRANTED BY YEAR (Recent):")
for idx, row in q1_result.head(10).iterrows():
    if pd.notna(row["year"]):
        print(f"  {int(row['year'])}: {int(row['patent_count']):,} patents")

if not q2_result.empty:
    print("\nTOP 10 COMPANIES:")
    for idx, row in q2_result.head(10).iterrows():
        print(f"  {idx+1}. {row['assignee_name']} - {int(row['patent_count']):,} patents")

print("\nPATENTS BY DECADE:")
for idx, row in q3_result.iterrows():
    if pd.notna(row["decade"]):
        print(f"  {int(row['decade'])}s: {int(row['patent_count']):,} patents")

# 2. CSV EXPORTS
print("\n\nExporting CSV files...")
q1_result.to_csv(f"{OUTPUT_FOLDER}/patents_by_year.csv", index=False)
print(f"   ✓ {OUTPUT_FOLDER}/patents_by_year.csv")

if not q2_result.empty:
    q2_result.to_csv(f"{OUTPUT_FOLDER}/top_companies.csv", index=False)
    print(f"   ✓ {OUTPUT_FOLDER}/top_companies.csv")

q3_result.to_csv(f"{OUTPUT_FOLDER}/patents_by_decade.csv", index=False)
print(f"   ✓ {OUTPUT_FOLDER}/patents_by_decade.csv")

if not q6_result.empty:
    q6_result.to_csv(f"{OUTPUT_FOLDER}/company_statistics.csv", index=False)
    print(f"   ✓ {OUTPUT_FOLDER}/company_statistics.csv")

# 3. JSON REPORT
print("\nGenerating JSON report...")
report = {
    "generated": datetime.now().isoformat(),
    "total_patents": int(total_patents),
    "date_range": {
        "from": int(q7_result.iloc[0]['earliest_year']),
        "to": int(q7_result.iloc[0]['latest_year'])
    },
    "patents_by_year": q1_result.head(20).to_dict(orient='records'),
    "patents_by_decade": q3_result.to_dict(orient='records'),
}

if not q2_result.empty:
    report["top_companies"] = q2_result.head(20).to_dict(orient='records')

if not q6_result.empty:
    report["company_statistics"] = q6_result.to_dict(orient='records')

with open(f"{OUTPUT_FOLDER}/report.json", 'w') as f:
    json.dump(report, f, indent=2)
print(f"   ✓ {OUTPUT_FOLDER}/report.json")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("✓ PIPELINE COMPLETE!")
print("=" * 70)
print(f"\nDatabase: {DB_PATH}")
print(f"Output Folder: {OUTPUT_FOLDER}/")
print("\nGenerated Files:")
print(f"  - patents_by_year.csv")
print(f"  - patents_by_decade.csv")
if not q2_result.empty:
    print(f"  - top_companies.csv")
    print(f"  - company_statistics.csv")
print(f"  - report.json")
print("\nNext Steps:")
print("  1. Review the CSV files in the output folder")
print("  2. Check report.json for the full analysis")
print("  3. Create visualizations with matplotlib/plotly")
print("  4. Push to GitHub!")
print("\n" + "=" * 70)

conn.close()
