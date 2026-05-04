# Global Patent Intelligence Data Pipeline

A data engineering project that collects, cleans, stores, and analyzes patent data using Python, pandas, SQL, and visualizations.

## Overview

Builds a complete pipeline that reads large patent TSV datasets, cleans them with pandas, stores data in a normalized SQLite schema, runs 7 advanced SQL queries, and generates reports, charts, and an interactive dashboard.

## Project Structure

```
patent-pipeline/
├── complete_patent_pipeline_optimized.py  # Main pipeline
├── visualizations.py                       # Static charts
├── dashboard.py                            # Streamlit dashboard
├── schema.sql                              # DB schema
├── clean_patents.csv / clean_inventors.csv / clean_companies.csv
├── database/patents.db
└── output/                                 # CSVs, JSONs, PNGs
```

## Quick Start

```bash
# Install dependencies
pip install pandas matplotlib seaborn streamlit plotly

# Run pipeline
python3 patent_pipeline.py

# Generate static charts
python3 visualizations.py

# Launch interactive dashboard
streamlit run dashboard.py
```

## Database Schema

| Table | Key Columns |
|-------|-------------|
| `patents` | patent_id, title, filing_date, year |
| `inventors` | inventor_id, name, country |
| `companies` | company_id, name |
| `patent_inventor_relationships` | patent_id, inventor_id |
| `patent_company_relationships` | patent_id, company_id |
| `patent_abstracts` | patent_id, abstract |

## SQL Queries (7 Total)

- **Q1** Top inventors by patent count
- **Q2** Top companies by patent count
- **Q3** Patent distribution by country
- **Q4** Patent trends over time (year > 1975)
- **Q5** Complex multi-table JOIN (patents + inventors + companies)
- **Q6** CTE — ranked inventor patent counts
- **Q7** Window functions — `ROW_NUMBER()` and `RANK()` over inventors

## Reports Generated

- **Console** — formatted summary (totals, top 10s)
- **CSV** — `top_inventors`, `top_companies`, `country_trends`, `patents_by_year`, `patent_details`
- **JSON** — full report with timestamp, stats, and all query results
- **Charts** — 7 PNGs (bar, pie, line) + Streamlit interactive dashboard

## Configuration

```python
DATA_FOLDER   = "data"
OUTPUT_FOLDER = "output"
DB_PATH       = "database/patents.db"
CHUNK_SIZE    = 50000   # chunked reading for large files
```

## 🔗 Data Source

[PatentsView Granted Patent Data](https://data.uspto.gov/bulkdata/datasets/pvgpatdis) — USPTO, 1976–2025, TSV format.

> **Note:** Raw TSV files are excluded from version control via `.gitignore`. Download them from the link above.

## Tech Stack

Python 3 · pandas · SQLite 3 · matplotlib · seaborn · Streamlit · Plotly

---

*Built for Cloud Computing coursework · Last updated May 4, 2026*