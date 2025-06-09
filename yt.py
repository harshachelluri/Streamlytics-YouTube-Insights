import streamlit as st
import pandas as pd
import mysql.connector
from datetime import timedelta, datetime
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="YouTube Channel Dashboard", layout="wide")

# MySQL connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",  # Add your password
        database="channel"
    )

# Load data from MySQL with caching
@st.cache_data
def load_data():
    conn = get_connection()
    query = """
        SELECT 
            DATE,
            SUBSCRIBERS_GAINED,
            SUBSCRIBERS_LOST,
            VIEWS,
            WATCH_HOURS,
            LIKES,
            COMMENTS,
            SHARES,
            TOTAL_SUBSCRIBERS
        FROM channel_data
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['NET_SUBSCRIBERS'] = df['SUBSCRIBERS_GAINED'] - df['SUBSCRIBERS_LOST']
    return df

# Custom quarterly function
def custom_quarter(date):
    month = date.month
    year = date.year
    if month in [2, 3, 4]:
        return pd.Period(year=year, quarter=1, freq='Q')
    elif month in [5, 6, 7]:
        return pd.Period(year=year, quarter=2, freq='Q')
    elif month in [8, 9, 10]:
        return pd.Period(year=year, quarter=3, freq='Q')
    else:
        return pd.Period(year=year if month != 1 else year-1, quarter=4, freq='Q')

# Aggregation logic
def aggregate_data(df, freq):
    if freq == 'Q':
        df = df.copy()
        df['CUSTOM_Q'] = df['DATE'].apply(custom_quarter)
        df_agg = df.groupby('CUSTOM_Q').agg({
            'VIEWS': 'sum',
            'WATCH_HOURS': 'sum',
            'NET_SUBSCRIBERS': 'sum',
            'LIKES': 'sum',
            'COMMENTS': 'sum',
            'SHARES': 'sum',
        })
        return df_agg
    else:
        return df.resample(freq, on='DATE').agg({
            'VIEWS': 'sum',
            'WATCH_HOURS': 'sum',
            'NET_SUBSCRIBERS': 'sum',
            'LIKES': 'sum',
            'COMMENTS': 'sum',
            'SHARES': 'sum',
        })

# Aggregation shortcuts
def get_weekly_data(df): return aggregate_data(df, 'W-MON')
def get_monthly_data(df): return aggregate_data(df, 'M')
def get_quarterly_data(df): return aggregate_data(df, 'Q')

def format_with_commas(number): return f"{number:,}"

def is_period_complete(date, freq):
    today = datetime.now()
    if freq == 'D':
        return date.date() < today.date()
    elif freq == 'W':
        return date + timedelta(days=6) < today
    elif freq == 'M':
        next_month = date.replace(day=28) + timedelta(days=4)
        return next_month.replace(day=1) <= today
    elif freq == 'Q':
        current_quarter = custom_quarter(today)
        return date < current_quarter

def calculate_delta(df, column):
    if len(df) < 2:
        return 0, 0
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-2]
    delta = current_value - previous_value
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent

def display_metric(col, title, value, df, column, color, time_frame):
    with col:
        with st.container():
            delta, delta_percent = calculate_delta(df, column)
            st.metric(title, format_with_commas(value), delta=f"{delta:+,.0f} ({delta_percent:+.2f}%)")

# Load and preprocess data
with st.spinner("Loading data..."):
    df = load_data()

# Sidebar controls
with st.sidebar:
    st.title("YouTube Channel Dashboard")
    st.header("⚙️ Settings")
    
    max_date = df['DATE'].max().date()
    min_date = df['DATE'].min().date()
    start_date = st.date_input("Start date", max_date - timedelta(days=365), min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", max_date, min_value=min_date, max_value=max_date)
    time_frame = st.selectbox("Select time frame", ("Daily", "Weekly", "Monthly", "Quarterly"))

# Prepare data
if time_frame == 'Daily':
    df_display = df.set_index('DATE')
elif time_frame == 'Weekly':
    df_display = get_weekly_data(df)
elif time_frame == 'Monthly':
    df_display = get_monthly_data(df)
else:
    df_display = get_quarterly_data(df)

# All-time metrics summary
st.subheader("All-Time Statistics")
metrics = [
    ("Total Subscribers", "NET_SUBSCRIBERS", '#29b5e8'),
    ("Total Views", "VIEWS", '#FF9F36'),
    ("Total Watch Hours", "WATCH_HOURS", '#D45B90'),
    ("Total Likes", "LIKES", '#7D44CF')
]

cols = st.columns(4)
for col, (title, column, color) in zip(cols, metrics):
    total_value = df[column].sum()
    display_metric(col, title, total_value, df_display, column, color, time_frame)

# Filter by date range
st.subheader("Selected Duration")
if time_frame == 'Quarterly':
    start_quarter = custom_quarter(start_date)
    end_quarter = custom_quarter(end_date)
    mask = (df_display.index >= start_quarter) & (df_display.index <= end_quarter)
else:
    mask = (df_display.index >= pd.Timestamp(start_date)) & (df_display.index <= pd.Timestamp(end_date))
df_filtered = df_display.loc[mask]

if df_filtered.empty:
    st.warning("No data available for the selected date range.")
else:
    # Filtered metrics summary
    cols = st.columns(4)
    for col, (title, column, color) in zip(cols, metrics):
        display_metric(col, title.split()[-1], df_filtered[column].sum(), df_filtered, column, color, time_frame)

    # CHART CONTROLS OVER GRAPH
    with st.container():
        st.subheader("📊 Chart Controls")
        col1, col2 = st.columns([1, 2])
        with col1:
            chart_selection = st.selectbox("Chart Type", ("Bar", "Area"), key="chart_type")
        with col2:
            chart_metric = st.selectbox(
                "Metric",
                ["NET_SUBSCRIBERS", "VIEWS", "WATCH_HOURS", "LIKES", "COMMENTS", "SHARES"],
                key="metric_selection"
            )

        # Show chart
        st.subheader(f"{chart_metric.replace('_', ' ').title()} Chart ({time_frame})")

        chart_data = df_filtered[[chart_metric]].copy()
        if time_frame == 'Quarterly':
            chart_data.index = chart_data.index.strftime('%Y Q%q')

        if chart_selection == 'Bar':
            st.bar_chart(chart_data, height=300)
        else:
            st.area_chart(chart_data, height=300)

    # Download and DataFrame display
    st.download_button("📥 Download Filtered Data", df_filtered.to_csv(index=True), file_name="filtered_youtube_data.csv")
    with st.expander("See DataFrame (Selected time frame)"):
        st.dataframe(df_filtered)
