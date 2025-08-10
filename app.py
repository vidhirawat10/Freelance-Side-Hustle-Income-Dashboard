import streamlit as st
import pandas as pd
import datetime
import plotly.express as px


DATA_FILE = 'freelance_data.csv'

# --- Streamlit Page Configuration ---
# Set page config for a wide layout and dark theme
st.set_page_config(
    page_title="Freelance & Side-Hustle Income Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    # For dark theme, ensure your Streamlit global settings are set to dark.
    # You can also manually configure via .streamlit/config.toml if needed.
)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month_Year'] = df['Date'].dt.to_period('M')
    df['Effective_Hourly_Rate'] = df.apply(
        lambda row: row['Payment_Received_USD'] / row['Hours_Worked'] if row['Hours_Worked'] and row['Hours_Worked'] > 0 else 0,
        axis=1
    )
    return df

df = load_data()

# --- Dashboard Title ---
st.title("Freelance & Side-Hustle Income Dashboard")
st.markdown("---") # Visual separator

# --- Row 1: Income Trend by Skill & Platform-wise Performance ---
st.header("Overall Trends")
col1, col2 = st.columns(2) # Two columns for these two charts

with col1:
    st.subheader("Income Trend by Skill")
    # Prepare data for Income Trend by Skill (Line Chart)
    # Group by Month_Year and Skill, then sum Payment_Received_USD
    skill_monthly_income = df.groupby(['Month_Year', 'Skill'])['Payment_Received_USD'].sum().unstack(fill_value=0)
    skill_monthly_income.index = skill_monthly_income.index.astype('datetime64[ns]') # Ensure datetime index for plotting # Convert Period to Timestamp for plotting
    st.line_chart(skill_monthly_income) # Use Streamlit's built-in line chart

with col2:
    st.subheader("Platform-wise Performance")
    # Prepare data for Platform-wise Performance (Donut Chart)
    platform_summary = df.groupby('Platform')['Payment_Received_USD'].sum().reset_index()
    platform_summary.columns = ['Platform', 'Total_Income']

    # Create a Donut Chart using Plotly Express
    fig_platform = px.pie(
        platform_summary,
        values='Total_Income',
        names='Platform',
        title='Income Distribution by Platform',
        hole=0.5, # This creates the donut shape
        color_discrete_sequence=px.colors.sequential.RdBu # You can experiment with color sequences
    )
    # Update layout to center title, adjust font, and remove legend title for cleaner look
    fig_platform.update_layout(
        showlegend=True,
        legend_title_text="", # Remove legend title
        title_x=0.5 # Center the title
    )
    fig_platform.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig_platform, use_container_width=True) # Display in Streamlit

st.markdown("---") # Visual separator

# --- Row 2: Time Spent vs Money Earned & High-Paying Niches ---
st.header("Deeper Insights")
col3, col4 = st.columns(2) # Two columns for these two charts

with col3:
    st.subheader("Time Spent vs Money Earned")
    # For simplicity and to match the visual, we'll represent a 50/50 split
    # In a real app, this might come from categorizing activities or using derived metrics.
    time_money_data = pd.DataFrame({
        'Category': ['Time Spent', 'Money Earned'],
        'Value': [50, 50] # Represents 50% for each
    })

    fig_time_money = px.pie(
        time_money_data,
        values='Value',
        names='Category',
        title='Proportion of Effort vs. Reward',
        hole=0.6, # Make it a donut chart
        color_discrete_sequence=['#4B0082', '#DA70D6'] # Custom colors (Purple/Orchid-like)
    )
    fig_time_money.update_layout(
        showlegend=False, # As percentages are in the middle, legend might be redundant
        title_x=0.5, # Center the title
        annotations=[dict(text='50%', x=0.5, y=0.5, font_size=20, showarrow=False)] # Middle text for 50%
    )
    fig_time_money.update_traces(textinfo='none', marker=dict(line=dict(color='#000000', width=1))) # No text labels on slices
    st.plotly_chart(fig_time_money, use_container_width=True)

with col4:
    st.subheader("High-Paying Niches")
    # Prepare data for High-Paying Niches (Horizontal Bar Chart)
    # Group by Skill and sum payment, then sort by income
    skill_income_ranking = df.groupby('Skill')['Payment_Received_USD'].sum().sort_values(ascending=False).reset_index()

    # Create a Horizontal Bar Chart using Plotly Express
    fig_niches = px.bar(
        skill_income_ranking,
        x='Payment_Received_USD',
        y='Skill',
        orientation='h', # Make it a horizontal bar chart
        title='Top Earning Skills/Niches',
        text='Payment_Received_USD', # Display values on bars
        color_discrete_sequence=px.colors.sequential.Plasma # Experiment with color sequences
    )
    fig_niches.update_layout(
        xaxis_title="Total Income Earned ($)",
        yaxis_title="Skill/Niche",
        yaxis_autorange="reversed", # Puts highest value at the top
        title_x=0.5 # Center the title
    )
    fig_niches.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig_niches, use_container_width=True)

st.markdown("---") # Visual separator

# --- Original User Query Section (Retained) ---
st.header("🚀 Optimize Your Earnings")

avg_hourly_rate = df['Effective_Hourly_Rate'].mean()
st.write(f"Based on your historical data, your average effective hourly rate is **${avg_hourly_rate:,.2f}**.")

st.subheader("1. How much can I earn by investing 'X' hours?")
hours_to_invest = st.number_input(
    "Enter hours you plan to invest:",
    min_value=0,
    value=10,
    step=1,
    help="How many hours do you plan to work?",
    key="hours_input" # Added key for uniqueness
)

if hours_to_invest > 0:
    estimated_earnings = hours_to_invest * avg_hourly_rate
    st.success(f"By investing **{hours_to_invest} hours**, you can expect to earn approximately **${estimated_earnings:,.2f}**.")
else:
    st.info("Enter a positive number of hours to get an estimate.")


st.subheader("2. How many hours do I need to earn '$Y' amount?")
target_income = st.number_input(
    "Enter your target income ($):",
    min_value=0.0,
    value=500.0,
    step=50.0,
    help="What's your income goal?",
    key="income_input" # Added key for uniqueness
)

if target_income > 0 and avg_hourly_rate > 0:
    estimated_hours_needed = target_income / avg_hourly_rate
    st.success(f"To earn **${target_income:,.2f}**, you'll need to work approximately **{estimated_hours_needed:,.1f} hours**.")
elif target_income > 0 and avg_hourly_rate <= 0:
    st.warning("Cannot estimate hours needed, as your average hourly rate is zero or negative. Please log some income data with hours worked.")
else:
    st.info("Enter a positive target income to get an estimate.")

st.markdown("---")
st.info("💡 This dashboard provides insights based on your historical data. Predictions are simple averages and actual results may vary.")
