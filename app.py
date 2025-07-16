import streamlit as st
import pandas as pd
import datetime

# --- Configuration ---
DATA_FILE = 'freelance_data.csv'

# --- Load Data ---
# @st.cache_data tells Streamlit to run this function only once and cache its result
# This makes the app fast, as it doesn't reload data every time you interact with the dashboard.
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    # Extract Month-Year for grouping income trends
    df['Month_Year'] = df['Date'].dt.to_period('M')
    # Calculate effective hourly rate for each project
    # Handle cases where Hours_Worked might be 0 to avoid division by zero
    df['Effective_Hourly_Rate'] = df.apply(
        lambda row: row['Payment_Received_USD'] / row['Hours_Worked'] if row['Hours_Worked'] and row['Hours_Worked'] > 0 else 0,
        axis=1
    )
    return df

# Load the data when the app starts
df = load_data()

# --- Dashboard UI ---
# Set basic page configuration for a wider layout
st.set_page_config(layout="wide", page_title="Freelance Income Dashboard")

st.title("💰 Simple Freelance & Side-Hustle Income Dashboard")

st.write("---") # A simple horizontal line for separation

# --- Section 1: Overall Performance Metrics ---
st.header("Overall Performance")
# Divide the section into 3 columns for neat display
col1, col2, col3 = st.columns(3)

with col1:
    total_income = df['Payment_Received_USD'].sum()
    st.metric(label="Total Income Earned", value=f"${total_income:,.2f}") # Format as currency
with col2:
    total_hours = df['Hours_Worked'].sum()
    st.metric(label="Total Hours Logged", value=f"{total_hours:,.0f} hrs") # Format as hours
with col3:
    # Calculate the overall average hourly rate from all projects
    avg_hourly_rate = df['Effective_Hourly_Rate'].mean()
    st.metric(label="Avg. Effective Hourly Rate", value=f"${avg_hourly_rate:,.2f}/hr")

st.write("---") # Separator

# --- Section 2: Income Trend Over Time ---
st.header("Income Trend Over Time")
# Group data by Month_Year and sum the income for each month
monthly_income = df.groupby('Month_Year')['Payment_Received_USD'].sum().reset_index()
# Convert 'Month_Year' (Period object) to Timestamp for better plotting with Streamlit
monthly_income['Month_Year'] = monthly_income['Month_Year'].dt.to_timestamp()
# Display a line chart
st.line_chart(monthly_income.set_index('Month_Year')['Payment_Received_USD'])

st.write("---") # Separator

# --- Section 3: Performance by Platform & Skill ---
st.header("Performance by Platform & Skill")
# Divide into two columns for side-by-side charts
col_platform, col_skill = st.columns(2)

with col_platform:
    # Group by platform and sum income, then sort
    platform_income = df.groupby('Platform')['Payment_Received_USD'].sum().sort_values(ascending=False)
    st.subheader("Income by Platform")
    st.bar_chart(platform_income) # Display as a bar chart

with col_skill:
    # Group by skill and sum income, then sort
    skill_income = df.groupby('Skill')['Payment_Received_USD'].sum().sort_values(ascending=False)
    st.subheader("Income by Skill")
    st.bar_chart(skill_income) # Display as a bar chart

st.write("---") # Separator

# --- Section 4: User Query Section (Simple ML/Logic) ---
st.header("🚀 Optimize Your Earnings")

# Display the calculated average hourly rate as a reference
st.write(f"Based on your historical data, your average effective hourly rate is **${avg_hourly_rate:,.2f}**.")

st.subheader("1. How much can I earn by investing 'X' hours?")
# Input field for user to enter hours
hours_to_invest = st.number_input(
    "Enter hours you plan to invest:",
    min_value=0, # Minimum value is 0 hours
    value=10,    # Default value is 10 hours
    step=1,      # Increment by 1 hour
    help="How many hours do you plan to work?"
)

if hours_to_invest > 0:
    # Simple calculation: hours * average_rate
    estimated_earnings = hours_to_invest * avg_hourly_rate
    st.success(f"By investing **{hours_to_invest} hours**, you can expect to earn approximately **${estimated_earnings:,.2f}**.")
else:
    st.info("Enter a positive number of hours to get an estimate.")


st.subheader("2. How many hours do I need to earn '$Y' amount?")
# Input field for user to enter target income
target_income = st.number_input(
    "Enter your target income ($):",
    min_value=0.0, # Minimum value is $0
    value=500.0,   # Default value is $500
    step=50.0,     # Increment by $50
    help="What's your income goal?"
)

# Perform calculation only if target income and average rate are positive
if target_income > 0 and avg_hourly_rate > 0:
    estimated_hours_needed = target_income / avg_hourly_rate
    st.success(f"To earn **${target_income:,.2f}**, you'll need to work approximately **{estimated_hours_needed:,.1f} hours**.")
elif target_income > 0 and avg_hourly_rate <= 0:
    st.warning("Cannot estimate hours needed, as your average hourly rate is zero or negative. Please log some income data with hours worked.")
else:
    st.info("Enter a positive target income to get an estimate.")

st.write("---")
st.info("💡 This dashboard provides insights based on your historical data. Predictions are simple averages and actual results may vary.")