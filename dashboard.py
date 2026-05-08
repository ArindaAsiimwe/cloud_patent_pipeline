#!/usr/bin/env python3
"""
Patent Intelligence Data Pipeline - ADVANCED STREAMLIT DASHBOARD
Modern, interactive dashboard with unique analytics and insights
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Hub",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
    <style>
    /* Main styling */
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom metric cards */
    [data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.95);
        border: 2px solid rgba(102, 126, 234, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Custom headers */
    h1, h2, h3 {
        color: #1f1f1f;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Tabs styling */
    [data-testid="stTabs"] {
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_db_connection():
    """Connect to SQLite database"""
    db_paths = [
        "/kaggle/working/database/patents.db",
        "database/patents.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            return sqlite3.connect(db_path)
    
    st.error("Database not found!")
    st.stop()

@st.cache_data
def load_data():
    """Load data from database using SQL queries"""
    try:
        conn = get_db_connection()
        
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
        df_countries = pd.read_sql("""
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
        df_trends = pd.read_sql("""
            SELECT 
                year,
                COUNT(*) as patent_count
            FROM patents
            WHERE year IS NOT NULL AND year > 1975
            GROUP BY year
            ORDER BY year ASC
        """, conn)
        
        # Overall stats
        df_patents = pd.read_sql("SELECT * FROM patents", conn)
        df_inventors = pd.read_sql("SELECT * FROM inventors", conn)
        
        # Advanced analytics: Inventor productivity
        df_inventor_productivity = pd.read_sql("""
            SELECT 
                i.country,
                COUNT(DISTINCT i.inventor_id) as inventor_count,
                COUNT(DISTINCT pir.patent_id) as patent_count,
                ROUND(COUNT(DISTINCT pir.patent_id) * 1.0 / COUNT(DISTINCT i.inventor_id), 2) as avg_patents_per_inventor
            FROM inventors i
            LEFT JOIN patent_inventor_relationships pir ON i.inventor_id = pir.inventor_id
            GROUP BY i.country
            ORDER BY avg_patents_per_inventor DESC
        """, conn)
        
        conn.close()
        return (df_patents, df_inventors, df_top_inventors, df_top_companies, 
                df_countries, df_trends, df_inventor_productivity)
    except Exception as e:
        st.error(f"Error: Failed to query database. {e}")
        st.stop()

# HEADER
st.markdown("# 🔬 Patent Intelligence Hub")
st.markdown("*Advanced Patent Analytics & Insights Platform*")
st.markdown("---")

# Load all data
(df_patents, df_inventors, df_top_inventors, df_top_companies, 
 df_countries, df_trends, df_inventor_productivity) = load_data()

# SIDEBAR - Dashboard Controls
with st.sidebar:
    st.markdown("### 📊 Dashboard Controls")
    
    metric_focus = st.selectbox(
        "Select Analysis",
        ["Overview", "Top Innovators", "Organizations", "Geography", "Trends"]
    )
    
    st.markdown("---")
    st.markdown("### 📈 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Patents", f"{len(df_patents):,}")
    with col2:
        st.metric("Inventors", f"{len(df_inventors):,}")

# KEY METRICS - Enhanced
st.markdown("### 📊 Key Metrics Dashboard")
metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

with metric_col1:
    st.metric(
        "📑 Total Patents",
        f"{len(df_patents):,}",
        delta=f"{int(df_patents['year'].max() - df_patents['year'].min())} years"
    )

with metric_col2:
    st.metric(
        "👨‍💼 Total Inventors",
        f"{len(df_inventors):,}",
        delta="contributors"
    )

with metric_col3:
    total_companies = df_top_companies['company_id'].nunique() if 'company_id' in df_top_companies.columns else len(df_top_companies)
    st.metric(
        "🏢 Organizations",
        f"{total_companies:,}",
        delta="patent assignees"
    )

with metric_col4:
    avg_patents = df_top_inventors['patent_count'].mean()
    st.metric(
        "📈 Avg Patents",
        f"{avg_patents:.1f}",
        delta="per inventor"
    )

with metric_col5:
    year_min = int(df_patents['year'].min())
    year_max = int(df_patents['year'].max())
    st.metric(
        "📅 Coverage",
        f"{year_min}-{year_max}",
        delta=f"{year_max - year_min} years"
    )

st.markdown("---")

# TABS - Redesigned
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏆 Top Innovators",
    "🏢 Organizations",
    "🌍 Global Map",
    "📈 Trends",
    "🎯 Productivity",
    "🔍 Deep Dive"
])

# TAB 1: TOP INNOVATORS
with tab1:
    st.markdown("## 🏆 Top Patent Innovators")
    st.markdown("*Leading inventors by patent count*")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Bar chart - top inventors
        top_inv_data = df_top_inventors.head(20).copy()
        
        fig = px.bar(
            top_inv_data,
            x='patent_count',
            y='name',
            orientation='h',
            title='📊 Top 20 Patent Innovators',
            color='patent_count',
            color_continuous_scale='Viridis',
            hover_data={'country': True},
            labels={'patent_count': 'Patent Count', 'name': 'Inventor'}
        )
        fig.update_layout(height=500, showlegend=False)
        fig.update_yaxes(tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🥇 Top Rankings")
        top_5 = df_top_inventors.head(5).reset_index(drop=True)
        for idx, row in top_5.iterrows():
            medal = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][idx]
            st.markdown(f"{medal} **{row['name']}**")
            st.caption(f"{int(row['patent_count'])} patents • {row['country']}")
    
    with col3:
        st.markdown("### 📊 Statistics")
        st.metric("Leader", f"{df_top_inventors.iloc[0]['patent_count']:.0f}")
        st.metric("Median", f"{df_top_inventors['patent_count'].median():.0f}")
        st.metric("Avg", f"{df_top_inventors['patent_count'].mean():.0f}")

# TAB 2: ORGANIZATIONS
with tab2:
    st.markdown("## 🏢 Leading Patent Organizations")
    st.markdown("*Top companies & institutions*")
    
    if not df_top_companies.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Scatter with size and color
            scatter_data = df_top_companies.head(30).copy()
            
            fig = px.scatter(
                scatter_data,
                y='patent_count',
                size='patent_count',
                hover_name='name',
                title='🏢 Top 30 Organizations - Patent Distribution',
                labels={'patent_count': 'Patents'},
                color='patent_count',
                color_continuous_scale='Plasma',
                size_max=50
            )
            fig.update_xaxes(showticklabels=False)
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Top 10 Organizations")
            for idx, row in df_top_companies.head(10).iterrows():
                progress = row['patent_count'] / df_top_companies['patent_count'].max()
                st.progress(progress, text=f"{row['name'][:20]}... ({int(row['patent_count'])})")
    else:
        st.info("No company data available")

# TAB 3: GLOBAL MAP
with tab3:
    st.markdown("## 🌍 Global Patent Distribution")
    st.markdown("*Patent hotspots around the world*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Horizontal bar chart - geographic distribution
        top_25_countries = df_countries.head(25).sort_values('patent_count', ascending=True)
        
        fig = px.bar(
            top_25_countries,
            x='patent_count',
            y='country',
            orientation='h',
            title='🗺️ Patent Distribution by Country - Top 25',
            color='patent_count',
            color_continuous_scale='Blues',
            labels={'patent_count': 'Patent Count', 'country': 'Country'}
        )
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🌏 Regional Breakdown")
        
        top_countries = df_countries.head(10)
        total_patents = top_countries['patent_count'].sum()
        
        st.markdown("**Top 10 Countries:**")
        for idx, row in top_countries.iterrows():
            pct = (row['patent_count'] / df_countries['patent_count'].sum()) * 100
            st.write(f"🔹 {row['country']}: {int(row['patent_count']):,} ({pct:.1f}%)")
        
        st.markdown("---")
        st.metric("Diversity", f"{len(df_countries)} countries")
        st.metric("Top 10%", f"{(top_countries['patent_count'].sum() / df_countries['patent_count'].sum() * 100):.1f}%")

# TAB 4: TRENDS WITH PREDICTIONS
with tab4:
    st.markdown("## 📈 Patent Market Trends & Forecasts")
    st.markdown("*Historical patterns with AI predictions*")
    
    trends_data = df_trends.copy().sort_values('year')
    
    # Advanced trend analysis with predictions
    trend_tab1, trend_tab2, trend_tab3 = st.tabs(["📊 Historical Data", "🔮 Predictions", "📉 Analytics"])
    
    with trend_tab1:
        # Area chart with gradient
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trends_data['year'],
            y=trends_data['patent_count'],
            fill='tozeroy',
            name='Patents',
            line=dict(color='#636EFA', width=3),
            fillcolor='rgba(99, 110, 250, 0.2)',
            hovertemplate='<b>%{x|.0f}</b><br>%{y:,.0f} patents<extra></extra>'
        ))
        
        fig.update_layout(
            title='📊 Patent Filings Over Time',
            xaxis_title='Year',
            yaxis_title='Number of Patents',
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with trend_tab2:
        # Predictions using linear trend
        from scipy import stats
        
        # Fit trend to recent 10 years
        recent_data = trends_data.tail(10).copy()
        if len(recent_data) > 2:
            x_recent = np.array(range(len(recent_data)))
            y_recent = recent_data['patent_count'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_recent, y_recent)
            
            # Create prediction for next 5 years
            last_year = int(trends_data['year'].max())
            pred_years = np.array([last_year + i for i in range(1, 6)])
            pred_x = np.array(range(len(recent_data), len(recent_data) + 5))
            pred_y = slope * pred_x + intercept
            
            # Combine historical and predicted
            combined_years = np.concatenate([trends_data['year'].values, pred_years])
            combined_counts = np.concatenate([trends_data['patent_count'].values, pred_y])
            combined_type = np.concatenate([['Historical']*len(trends_data), ['Predicted']*5])
            
            pred_df = pd.DataFrame({
                'year': combined_years,
                'patent_count': combined_counts,
                'type': combined_type
            })
            
            # Plot with predictions
            fig = go.Figure()
            
            historical = pred_df[pred_df['type'] == 'Historical']
            fig.add_trace(go.Scatter(
                x=historical['year'],
                y=historical['patent_count'],
                fill='tozeroy',
                name='Historical',
                line=dict(color='#636EFA', width=3),
                fillcolor='rgba(99, 110, 250, 0.2)'
            ))
            
            predicted = pred_df[pred_df['type'] == 'Predicted']
            fig.add_trace(go.Scatter(
                x=predicted['year'],
                y=predicted['patent_count'],
                name='Predicted',
                line=dict(color='#FF6692', width=3, dash='dash'),
                fillcolor='rgba(255, 102, 146, 0.1)',
                fill='tozeroy'
            ))
            
            fig.update_layout(
                title='🔮 Patent Filings Forecast (Next 5 Years)',
                xaxis_title='Year',
                yaxis_title='Number of Patents',
                height=500,
                hovermode='x unified',
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display prediction metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Trend Slope", f"{slope:.0f} patents/year")
            with col2:
                st.metric("R² Score", f"{r_value**2:.3f}")
            with col3:
                st.metric("Predicted 2031", f"{int(pred_y[-1]):,.0f}")
        else:
            st.info("Insufficient data for predictions")
    
    with trend_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Trend Analysis")
            
            # Calculate growth
            recent_years = trends_data[trends_data['year'] >= trends_data['year'].max() - 5]
            if len(recent_years) > 1:
                growth = ((recent_years['patent_count'].iloc[-1] - recent_years['patent_count'].iloc[0]) / 
                         recent_years['patent_count'].iloc[0] * 100)
                st.metric("5-Year Growth", f"{growth:+.1f}%")
            
            st.metric("Peak Year", f"{trends_data.loc[trends_data['patent_count'].idxmax(), 'year']:.0f}")
            st.metric("Peak Value", f"{trends_data['patent_count'].max():,.0f}")
        
        with col2:
            st.markdown("### 🔢 Volatility Analysis")
            yearly_growth = trends_data['patent_count'].pct_change() * 100
            st.metric("Avg Annual Growth", f"{yearly_growth.mean():.2f}%")
            st.metric("Volatility (StdDev)", f"{yearly_growth.std():.2f}%")
            st.metric("Max Growth Year", f"{yearly_growth.max():.1f}%")
        
        st.markdown("---")
        st.markdown("**Decade Comparison:**")
        decades = pd.cut(trends_data['year'], bins=5)
        decade_totals = trends_data.groupby(decades)['patent_count'].sum()
        for decade, total in decade_totals.items():
            st.caption(f"{decade}: {int(total):,} patents")

# TAB 5: PRODUCTIVITY
with tab5:
    st.markdown("## 🎯 Inventor Productivity Analysis")
    st.markdown("*Patents per inventor by region*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Productivity bar chart
        fig = px.bar(
            df_inventor_productivity.head(15),
            x='avg_patents_per_inventor',
            y='country',
            orientation='h',
            title='📊 Average Patents per Inventor by Country',
            labels={'avg_patents_per_inventor': 'Avg Patents/Inventor', 'country': 'Country'},
            color='avg_patents_per_inventor',
            color_continuous_scale='Greens'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter: Correlation between inventors and productivity
        fig = px.scatter(
            df_inventor_productivity.head(20),
            x='inventor_count',
            y='avg_patents_per_inventor',
            size='patent_count',
            hover_name='country',
            title='👥 Inventor Count vs Productivity',
            labels={'inventor_count': 'Number of Inventors', 'avg_patents_per_inventor': 'Avg Patents/Inventor'},
            color='patent_count',
            color_continuous_scale='Sunset'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# TAB 6: DEEP DIVE
with tab6:
    st.markdown("## 🔍 Advanced Analysis")
    st.markdown("*Detailed exploration & custom analytics*")
    
    analysis_type = st.selectbox(
        "📊 Select Analysis Type",
        [
            "Inventor Rankings by Country",
            "Company Patent Distribution",
            "Yearly Growth Rates",
            "Patent Distribution Analysis",
            "Top Countries Comparison"
        ]
    )
    
    if analysis_type == "Inventor Rankings by Country":
        selected_country = st.selectbox(
            "🌐 Choose Country",
            sorted(df_inventors['country'].dropna().unique())
        )
        
        country_inventors = df_top_inventors[df_top_inventors['country'] == selected_country].head(20)
        
        if not country_inventors.empty:
            fig = px.bar(
                country_inventors,
                x='patent_count',
                y='name',
                orientation='h',
                title=f'🏆 Top Inventors from {selected_country}',
                color='patent_count',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 📋 Detailed Rankings")
            st.dataframe(
                country_inventors[['name', 'patent_count']].reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(f"No inventor data for {selected_country}")
    
    elif analysis_type == "Company Patent Distribution":
        st.markdown("### 🏢 All Organizations Data")
        st.dataframe(
            df_top_companies.head(100),
            use_container_width=True,
            hide_index=True
        )
    
    elif analysis_type == "Yearly Growth Rates":
        trends_data_copy = df_trends.copy()
        trends_data_copy['growth_rate'] = trends_data_copy['patent_count'].pct_change() * 100
        
        fig = px.line(
            trends_data_copy,
            x='year',
            y='growth_rate',
            title='📊 Year-over-Year Patent Growth Rate',
            labels={'growth_rate': 'Growth Rate (%)', 'year': 'Year'},
            markers=True,
            line_shape='spline'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Patent Distribution Analysis":
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                df_top_inventors,
                x='patent_count',
                nbins=30,
                title='📊 Inventor Patent Count Distribution',
                labels={'patent_count': 'Patents per Inventor'},
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Distribution Statistics")
            st.metric("Mean", f"{df_top_inventors['patent_count'].mean():.2f}")
            st.metric("Median", f"{df_top_inventors['patent_count'].median():.2f}")
            st.metric("Std Dev", f"{df_top_inventors['patent_count'].std():.2f}")
            st.metric("Max", f"{df_top_inventors['patent_count'].max():.0f}")
            st.metric("Min", f"{df_top_inventors['patent_count'].min():.0f}")
    
    elif analysis_type == "Top Countries Comparison":
        comparison_countries = df_countries.head(10)
        
        fig = px.bar(
            comparison_countries,
            x='country',
            y=['patent_count', 'percentage'],
            title='🌍 Top Countries Comparison',
            labels={'value': 'Count', 'country': 'Country'},
            barmode='group'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

# FOOTER
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 11px; padding: 20px;'>
    <p>🔬 Patent Intelligence Hub | Advanced Analytics Platform</p>
    <p>Data Source: Global Patent Database | Updated: {}</p>
    <p>Built with Streamlit, Plotly & SQLite</p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
