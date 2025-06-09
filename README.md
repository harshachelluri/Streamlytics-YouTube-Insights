# Streamlytics-YouTube-Insights
# YouTube Channel Dashboard

A Streamlit-based dashboard for analyzing YouTube channel performance metrics, pulling data from a MySQL database and visualizing key statistics such as subscribers, views, watch hours, and engagement metrics.

## What I've Done

- **MySQL Data Integration**: Developed a connection to a MySQL database to fetch channel performance data from the `channel_data` table, including subscribers gained/lost, views, watch hours, likes, comments, shares, and total subscribers.
- **Data Aggregation**: Implemented custom aggregation logic for Daily, Weekly, Monthly, and Quarterly time frames, with a custom quarterly definition (Q1: Feb-Apr, Q2: May-Jul, Q3: Aug-Oct, Q4: Nov-Jan).
- **Interactive UI**: Built a Streamlit dashboard with a wide layout, featuring:
  - Sidebar controls for selecting date ranges and time frames.
  - Metrics display for all-time and filtered statistics with delta calculations (absolute and percentage changes).
  - Interactive Bar and Area charts for visualizing user-selected metrics.
- **Data Caching**: Utilized Streamlit’s `@st.cache_data` to optimize data loading performance from the MySQL database.
- **Data Export**: Added functionality to download filtered data as a CSV file.
- **Custom Date Filtering**: Implemented date range filtering with validation to ensure data availability, displaying warnings for empty datasets.
- **Chart Controls**: Created dynamic chart controls allowing users to switch between Bar and Area charts and select metrics for visualization.
- **Error Handling**: Included checks for incomplete periods and empty data ranges to improve user experience.

## Features

- **MySQL Integration**: Connects to a MySQL database to fetch channel performance data.
- **Dynamic Time Frames**: View data aggregated by Daily, Weekly, Monthly, or custom Quarterly periods.
- **Date Range Filtering**: Select custom start and end dates for analysis.
- **Key Metrics**: Displays total and filtered metrics for subscribers, views, watch hours, likes, comments, and shares with delta changes.
- **Interactive Charts**: Visualize metrics with Bar or Area charts based on user-selected time frames and metrics.
- **Data Download**: Export filtered data as a CSV file.
- **Responsive Layout**: Built with Streamlit's wide layout for an optimized viewing experience.

## Prerequisites

- Python 3.8+
- MySQL database with a `channel_data` table
- Required Python packages:
  ```bash
  pip install streamlit pandas mysql-connector-python matplotlib
