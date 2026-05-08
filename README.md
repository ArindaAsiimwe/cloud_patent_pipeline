GLOBAL PATENT INTELLIGENCE DATA PIPELINE - PROJECT SUBMISSION

PROJECT OVERVIEW:
This project implements a complete data engineering pipeline that collects, 
cleans, stores, and analyzes patent data using Python, pandas, SQL, and 
interactive visualizations.

KEY LINKS

📊 INTERACTIVE DASHBOARD:
   https://cloudpatentpipeline-gy8xprrrcpniykfyy2aukb.streamlit.app/
   (Launch with: streamlit run dashboard.py)

🔗 GITHUB REPOSITORY:
   https://github.com/ArindaAsiimwe/cloud_patent_pipeline

PROJECT DELIVERABLES


📁 CODE FILES:
   ✓ patent_pipeline.py        - Main data pipeline script
   ✓ dashboard.py              - Streamlit interactive dashboard
   ✓ visualizations.py         - Static chart generation
   ✓ schema.sql                - Database schema definition

📁 CLEAN DATA FILES (in output/):
   ✓ clean_patents.csv         - Cleaned patent records
   ✓ clean_inventors.csv       - Cleaned inventor data
   ✓ clean_companies.csv       - Cleaned company data

📁 DATABASE:
   ✓ database/patents.db       - SQLite database with normalized schema

PIPELINE FEATURES


DATA PROCESSING:
✓ Loads 3 TSV datasets (~14GB) efficiently
✓ Cleans and validates all data
✓ Handles missing values and duplicates
✓ Memory-optimized for large files

DATABASE DESIGN:
✓ 6 normalized tables with proper relationships
✓ Patent-Inventor-Company relationships tracked
✓ Indexed queries for fast retrieval
✓ Support for abstracts and metadata

SQL QUERIES (7 Advanced Queries):
✓ Q1 - Top Inventors by patent count
✓ Q2 - Top Companies by patent count  
✓ Q3 - Country trends and percentages
✓ Q4 - Patents by year (trends analysis)
✓ Q5 - Complex JOIN query across relationships
✓ Q6 - CTE (Common Table Expression) queries
✓ Q7 - Window functions for ranking

VISUALIZATIONS:
✓ Interactive Streamlit Dashboard with 6 unique tabs
✓ Real-time patent analytics from SQLite database
✓ Advanced Plotly visualizations with hover details
✓ AI predictions with 5-year forecasting models

QUICK START GUIDE

1. INSTALL DEPENDENCIES:
   pip install pandas matplotlib seaborn streamlit plotly

2. RUN PIPELINE (on Kaggle or locally):
   python3 patent_pipeline.py
   
   This will:
   - Load and clean data
   - Create SQLite database with normalized schema
   - Run 7 SQL queries
   - Generate output CSVs and reports
   - Create static visualizations

3. LAUNCH INTERACTIVE DASHBOARD:
   streamlit run dashboard.py
   
   Access at: http://localhost:8501

4. VIEW STATIC CHARTS:
   See generated PNGs in output/ folder

5. GENERATE REPORTS:
   Console report is printed during pipeline execution
   JSON report saved to output/report.json

INTERACTIVE DASHBOARD FEATURES

The Streamlit dashboard provides real-time patent analytics with 6 unique tabs:

📊 KEY METRICS DASHBOARD (Top Section):
   ✓ Total Patents - Total number of patent records
   ✓ Total Inventors - Number of unique inventors
   ✓ Organizations - Count of companies/assignees
   ✓ Avg Patents - Average patents per inventor
   ✓ Coverage - Time period span (min-max years)

🏆 TAB 1: TOP INNOVATORS
   ✓ Bar chart showing top 20 patent inventors
   ✓ Ranked display with patent counts
   ✓ Country of origin for each inventor
   ✓ Quick stats: leader, median, average

🏢 TAB 2: ORGANIZATIONS
   ✓ Scatter plot visualization of top 30 companies
   ✓ Bubble sizing by patent count
   ✓ Color gradient showing patent distribution
   ✓ Top 10 organizations list with progress bars

🌍 TAB 3: GLOBAL MAP
   ✓ Horizontal bar chart of top 25 countries
   ✓ Patent concentration by nation
   ✓ Regional breakdown with percentages
   ✓ Diversity metrics and coverage analysis

📈 TAB 4: TRENDS & FORECASTING (Advanced)
   Subtab 1 - Historical Data:
   ✓ Area chart showing patent filings over time
   ✓ Complete historical trend visualization
   
   Subtab 2 - AI Predictions:
   ✓ Linear regression forecast for next 5 years
   ✓ Historical + predicted data comparison
   ✓ R² score showing prediction accuracy
   ✓ Forecasted patent counts for future years
   
   Subtab 3 - Analytics:
   ✓ 5-year growth rate calculation
   ✓ Peak year and peak value metrics
   ✓ Volatility analysis (standard deviation)
   ✓ Decade-by-decade comparison

🎯 TAB 5: PRODUCTIVITY ANALYSIS
   ✓ Bar chart: Average patents per inventor by country
   ✓ Scatter plot: Inventor count vs productivity correlation
   ✓ Regional comparison with bubble sizing
   ✓ Identifies most and least productive patent ecosystems

🔍 TAB 6: DEEP DIVE (Advanced Analytics)
   5 Custom Analysis Modes:
   
   1. Inventor Rankings by Country
      - Select any country to see top inventors
      - Detailed ranking with patent counts
      - Country-specific analysis
   
   2. Company Patent Distribution
      - Complete list of all organizations
      - Full dataset with counts
      - Exportable data view
   
   3. Yearly Growth Rates
      - Year-over-year growth calculations
      - Trend line with spline smoothing
      - Identifies growth patterns
   
   4. Patent Distribution Analysis
      - Histogram of patent distribution
      - Statistical metrics (mean, median, std dev)
      - Distribution shape analysis
   
   5. Top Countries Comparison
      - Side-by-side country metrics
      - Grouped bar charts
      - Comparative analysis

DASHBOARD CAPABILITIES:
✓ Real-time data querying from SQLite database
✓ Interactive Plotly visualizations with hover details
✓ No CSV dependencies - all data from database
✓ Responsive design for desktop and mobile
✓ Modern UI with custom styling
✓ Color-coded metrics with delta indicators
✓ Export-ready visualizations

DATABASE SCHEMA


TABLES:
├── patents (patent_id, title, filing_date, year)
├── inventors (inventor_id, name, country)
├── companies (company_id, name)
├── patent_inventor_relationships (patent_id, inventor_id)
├── patent_company_relationships (patent_id, company_id)
└── patent_abstracts (patent_id, abstract)

RELATIONSHIPS:
- Each patent can have multiple inventors
- Each patent can have multiple companies
- Each inventor belongs to a country
- Abstracts linked to patents

FOLDER STRUCTURE


patent-pipeline/
├── README.md                          # Main project documentation
├── readme.txt                         # This file
├── patent_pipeline.py                 # Main pipeline script
├── dashboard.py                       # Streamlit dashboard
├── visualizations.py                  # Static chart generation
├── schema.sql                         # Database schema
├── database/
│   └── patents.db                     # SQLite database
├── output/
│   ├── clean_patents.csv              # Cleaned patents
│   ├── clean_inventors.csv            # Cleaned inventors
│   ├── clean_companies.csv            # Cleaned companies
│   ├── top_inventors.csv              # Top 20 inventors query
│   ├── top_companies.csv              # Top 20 companies query
│   ├── country_trends.csv             # Country analysis
│   ├── patents_by_year.csv            # Trend analysis
│   ├── patent_details.csv             # Detailed patent info
│   ├── report.json                    # JSON report
│   ├── top_inventors.png              # Bar chart
│   ├── top_companies.png              # Bar chart
│   ├── patents_by_country.png         # Pie chart
│   └── patents_by_year.png            # Line chart
└── data/
    ├── g_patent.tsv                   # Raw patent data
    ├── g_patent_abstract.tsv          # Patent abstracts
    └── g_persistent_assignee.tsv      # Company assignments

TECHNOLOGIES USED


Backend & Processing:
✓ Python 3
✓ Pandas - Data manipulation and cleaning
✓ SQLite3 - Database management
✓ NumPy - Numerical computations

Visualization:
✓ Matplotlib - Static charts
✓ Seaborn - Advanced statistical plots
✓ Plotly - Interactive visualizations
✓ Streamlit - Interactive web dashboard

Database:
✓ SQLite - Lightweight relational database
✓ SQL - 7 advanced queries (JOINs, CTEs, Window Functions)

PERFORMANCE METRICS
Processing Speed:
✓ Optimized for large files (14GB+ datasets)
✓ Memory-efficient chunked reading
✓ Garbage collection management
✓ O(1) dictionary lookups for performance

Data Volume:
✓ Patents processed: ~millions
✓ Inventors generated: ~thousands
✓ Companies tracked: ~thousands
✓ Relationships: ~millions

Query Performance:
✓ Indexed tables for fast retrieval
✓ Optimized JOIN operations
✓ CTE and window function support


GitHub: https://github.com/ArindaAsiimwe/cloud_patent_pipeline

