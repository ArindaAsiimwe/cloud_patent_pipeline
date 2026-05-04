#!/usr/bin/env python3
"""
Patent Intelligence Data Pipeline - STREAMLIT DASHBOARD
Interactive dashboard for patent analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from CSV files"""
    try:
        df_patents = pd.read_csv("output/clean_patents.csv")
        df_inventors = pd.read_csv("output/clean_inventors.csv")
        df_top_inventors = pd.read_csv("output/top_inventors.csv")
        df_top_companies = pd.read_csv("output/top_companies.csv")
        df_countries = pd.read_csv("output/country_trends.csv")
        df_trends = pd.read_csv("output/patents_by_year.csv")
        return df_patents, df_inventors, df_top_inventors, df_top_companies, df_countries, df_trends
    except FileNotFoundError as e:
        st.error(f"Error: Output files not found. {e}")
        st.info("Please run patent_pipeline.py first to generate output files.")
        st.stop()

# HEADER

st.title("🔬 Patent Intelligence Dashboard")
st.markdown("---")

# Load all data
df_patents, df_inventors, df_top_inventors, df_top_companies, df_countries, df_trends = load_data()

# KEY METRICS

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_patents = len(df_patents)
    st.metric(label="Total Patents", value=f"{total_patents:,}")

with col2:
    total_inventors = len(df_inventors)
    st.metric(label="Total Inventors", value=f"{total_inventors:,}")

with col3:
    # Count unique companies
    total_companies = df_top_companies['company_id'].nunique() if 'company_id' in df_top_companies.columns else len(df_top_companies)
    st.metric(label="Total Companies", value=f"{total_companies:,}")

with col4:
    avg_patents = df_top_inventors['patent_count'].mean()
    st.metric(label="Avg Patents/Inventor", value=f"{avg_patents:.2f}")

st.markdown("---")

# TABS

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Top Inventors",
    "🏢 Top Companies",
    "🌍 Countries",
    "📊 Trends",
    "🔍 Data Explorer"
])

# TAB 1: TOP INVENTORS

with tab1:
    st.subheader("Top Inventors by Patent Count")
    
    # Get data
    top_inventors = df_top_inventors.head(20)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bar chart
        fig = px.bar(
            top_inventors.head(15),
            x="patent_count",
            y="name",
            orientation="h",
            title="Top 15 Inventors",
            labels={"patent_count": "Number of Patents", "name": "Inventor"},
            color="patent_count",
            color_continuous_scale="Blues"
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            top_inventors.head(10)[["name", "country", "patent_count"]],
            use_container_width=True,
            hide_index=True
        )

# TAB 2: TOP COMPANIES

with tab2:
    st.subheader("Top Companies by Patent Count")
    
    # Get data
    top_companies = df_top_companies.head(20)
    
    if not top_companies.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                top_companies.head(15),
                x="patent_count",
                y="name",
                orientation="h",
                title="Top 15 Companies",
                labels={"patent_count": "Number of Patents", "name": "Company"},
                color="patent_count",
                color_continuous_scale="Greens"
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                top_companies.head(10)[["name", "patent_count"]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.info("No company data available")

# TAB 3: COUNTRIES

with tab3:
    st.subheader("Patent Distribution by Country")
    
    # Get data
    countries = df_countries.head(15)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig = px.pie(
            countries,
            values="patent_count",
            names="country",
            title="Patent Distribution (Top 15)",
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart
        fig = px.bar(
            countries,
            x="country",
            y="patent_count",
            title="Patents by Country (Top 15)",
            labels={"patent_count": "Number of Patents", "country": "Country"},
            color="patent_count",
            color_continuous_scale="Viridis"
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.dataframe(
        countries.reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

# TAB 4: TRENDS

with tab4:
    st.subheader("Patent Trends Over Time")
    
    # Get data
    trends = df_trends[df_trends['year'] > 1975].copy() if 'year' in df_trends.columns else df_trends.copy()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Line chart
        fig = px.line(
            trends,
            x="year",
            y="patent_count",
            title="Patents Filed Per Year",
            labels={"patent_count": "Number of Patents", "year": "Year"},
            markers=True,
            line_shape="spline"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Recent trends table
        recent = trends.tail(10).sort_values("year", ascending=False)
        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )
        
        # Statistics
        st.metric("Latest Year", int(trends['year'].max()))
        st.metric("Patents (Latest Year)", int(trends['patent_count'].max()))

# TAB 5: DATA EXPLORER

with tab5:
    st.subheader("Data Explorer")
    
    explorer_type = st.selectbox(
        "Select View",
        [
            "Top Inventors by Country",
            "All Inventors",
            "All Companies",
            "All Countries"
        ]
    )
    
    if explorer_type == "Top Inventors by Country":
        # Get unique countries from inventors
        countries_list = sorted(df_inventors['country'].dropna().unique().tolist())
        
        selected_country = st.selectbox("Select Country", countries_list)
        
        # Filter inventors by country
        country_inventors = df_inventors[df_inventors['country'] == selected_country].copy()
        
        # Merge with top inventors to get patent counts
        country_top = df_top_inventors[df_top_inventors['country'] == selected_country].head(20)
        
        st.dataframe(
            country_top[["name", "country", "patent_count"]],
            use_container_width=True,
            hide_index=True
        )
    
    elif explorer_type == "All Inventors":
        # Filter and display
        st.dataframe(
            df_top_inventors.head(100),
            use_container_width=True,
            hide_index=True
        )
    
    elif explorer_type == "All Companies":
        st.dataframe(
            df_top_companies.head(100),
            use_container_width=True,
            hide_index=True
        )
    
    elif explorer_type == "All Countries":
        st.dataframe(
            df_countries,
            use_container_width=True,
            hide_index=True
        )

# FOOTER

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    <p>Patent Intelligence Data Pipeline | Generated: {}</p>
    <p>Data Source: PatentsView Granted Patent Disambiguated Data</p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
