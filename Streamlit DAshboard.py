import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv(r"C:\Users\ASUS\.vscode\Factory-to-Customer Shipping Route Efficiency Analysis for Nassau Candy Distributor\Nassau Candy Distributor.csv")


df['Order Date'] = pd.to_datetime(df['Order Date'], format="%Y-%m-%d", errors="coerce")
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format="%Y-%m-%d", errors="coerce")
df['Lead_Time'] = (df['Ship Date'] - df['Order Date']).dt.days

# Title
st.title("📦 Nassau Candy Shipping Efficiency Dashboard")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
factory_filter = st.sidebar.selectbox("Select Factory", df['Factory'].unique())
ship_mode_filter = st.sidebar.selectbox("Select Ship Mode", df['Ship Mode'].unique())

# Date Range Filter
st.sidebar.subheader("📅 Date Range Filter")
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

# Threshold Slider
st.sidebar.subheader("📏 Threshold Settings")
threshold = st.sidebar.slider("Lead Time Threshold (days)", 0, 30, 7)

# Apply filters
filtered_df = df[(df['Factory'] == factory_filter) & 
                 (df['Ship Mode'] == ship_mode_filter) &
                 (df['Order Date'] >= pd.to_datetime(start_date)) &
                 (df['Order Date'] <= pd.to_datetime(end_date))]

# Handle empty data
if filtered_df.empty:
    st.warning("⚠️ No data available for selected filters. Please adjust filters.")
else:
    # KPIs Section
    st.subheader("📊 Key Performance Indicators (KPIs)")
    avg_lead = round(filtered_df['Lead_Time'].mean(), 2)
    total_shipments = filtered_df['Order ID'].count()
    fastest_route = filtered_df.groupby('Route')['Lead_Time'].mean().idxmin()
    slowest_route = filtered_df.groupby('Route')['Lead_Time'].mean().idxmax()
    delayed_orders = filtered_df[filtered_df['Lead_Time'] > threshold]
    delay_percent = round(len(delayed_orders) / len(filtered_df) * 100, 2)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📊 Avg Lead Time", f"{avg_lead} days")
    col2.metric("🚚 Total Shipments", total_shipments)
    col3.metric("⚡ Fastest Route", fastest_route)
    col4.metric("🐌 Slowest Route", slowest_route)
    col5.metric("🚨 Delay Frequency", f"{delay_percent}%")

    # Route Leaderboard
    st.subheader("🏆 Route Efficiency Leaderboard")
    route_summary = filtered_df.groupby('Route').agg({
        'Order ID':'count',
        'Lead_Time':'mean'
    }).reset_index()

    # Efficiency Score
    route_summary['Efficiency Score'] = 1 / (1 + route_summary['Lead_Time'])
    st.dataframe(route_summary.sort_values('Lead_Time'))

    # Bar Chart
    fig_bar = px.bar(route_summary.sort_values('Lead_Time'),
                     x='Route', y='Lead_Time',
                     color='Lead_Time',
                     color_continuous_scale='Viridis',
                     title="Average Lead Time by Route")
    fig_bar.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_bar)

    # Download Button
    st.download_button("⬇️ Download Filtered Data", 
                       filtered_df.to_csv(index=False).encode('utf-8'),
                       "filtered_data.csv",
                       "text/csv")

    # Heatmap
    st.subheader("🌍 Lead Time Heatmap")
    fig_heat = px.density_heatmap(filtered_df,
                                  x="State/Province", y="Factory",
                                  z="Lead_Time",
                                  color_continuous_scale="RdBu",
                                  title="Lead Time Heatmap by Factory & State")
    st.plotly_chart(fig_heat)

    # Choropleth Map
    st.subheader("🗺️ Geographic Lead Time Map")
    state_summary = filtered_df.groupby('State/Province').agg({
        'Order ID':'count',
        'Lead_Time':'mean'
    }).reset_index()

    fig_map = px.choropleth(state_summary,
                            locations='State/Province',
                            locationmode="USA-states",
                            color='Lead_Time',
                            scope="usa",
                            color_continuous_scale="Blues",
                            title="Average Lead Time by State")
    st.plotly_chart(fig_map)

    # Boxplot for Ship Mode comparison
    st.subheader("📦 Ship Mode Comparison")
    fig_box = px.box(df, x="Ship Mode", y="Lead_Time", color="Ship Mode",
                     title="Lead Time Distribution by Ship Mode")
    st.plotly_chart(fig_box)

    # Drill-Down Chart
    st.subheader("🔎 Route Drill-Down Timeline")
    selected_route = st.selectbox("Select Route for Drill-Down", filtered_df['Route'].unique())
    route_orders = filtered_df[filtered_df['Route'] == selected_route]
    fig_timeline = px.scatter(route_orders, 
                              x="Order Date", y="Lead_Time",
                              color="Ship Mode",
                              hover_data=["Order ID","Customer ID","State/Province"],
                              title=f"Shipment Timeline for {selected_route}")
    st.plotly_chart(fig_timeline)

    # Executive Summary
    st.subheader("📑 Executive Summary")
    summary_lines = [
        f"⚡ Fastest route is **{fastest_route}** with average lead time of {filtered_df.groupby('Route')['Lead_Time'].mean().min()} days.",
        f"🐌 Slowest route is **{slowest_route}** with average lead time of {filtered_df.groupby('Route')['Lead_Time'].mean().max()} days.",
        f"📊 Overall average lead time across selected filters is {avg_lead} days.",
        f"🚨 Delay frequency (> {threshold} days): {delay_percent}% of shipments."
    ]
    for line in summary_lines:
        st.write(line)
        

        
