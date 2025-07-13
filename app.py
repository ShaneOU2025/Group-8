import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt


# --- Sample Data (replace with your actual CSV or database logic) ---
data = {
    "Str #": ["3/17A", "3/17H", "26/2B", "26/2C", "26/6A", "26/6B", "71", "72", "128", "53"],
    "Height (Feet)": [105, 100, 90, 90, 90, 90, 120.5, 120.6, 135.5, 140.6],
    "Maximum Bending Moment (Ft-Kips)": [2959.91, 2794.86, 4962.98, 3708, 3328.93, 3073.23, 12375, 12375, 14624.1, 15382.1],
    "Weight (lbs)": [15921, 13637, 17294, 14164, 13346, 12775, 44377, 44377, 54790, 57879],
    "Cost": [49085.7, 45381.59, 54159.58, 44840.39, 42854.39, 41070.8, 113870.6, 113870.6, 139692.07, 146899.27]
}
df = pd.DataFrame(data)

# --- Sidebar Inputs ---
st.sidebar.title("Design Requirements")
moment_req = st.sidebar.number_input("Required Bending Moment (Ft-Kips)", min_value=0.0, value=2500.0, help="Minimum required at POI")
height_req = st.sidebar.number_input("Required Structure Height (Feet)", min_value=0.0, value=90.0, help="Minimum structure height")

st.sidebar.selectbox("Project Schedule", ["Slow", "Moderate", "Fast"], help="Speed of construction timeline")
st.sidebar.selectbox("Project Complexity", ["Low", "Medium", "High"], help="Site-specific and engineering challenges")

# --- Filter Structures Based on Requirements ---
filtered_df = df[(df["Maximum Bending Moment (Ft-Kips)"] >= moment_req) & (df["Height (Feet)"] >= height_req)]

# Optional: Sort by cost
sort_option = st.selectbox("Sort reusable structures by:", ["Cost", "Weight", "Height"])
sort_column = {"Cost": "Cost", "Weight": "Weight (lbs)", "Height": "Height (Feet)"}[sort_option]
filtered_df = filtered_df.sort_values(by=sort_column)

# --- Cost Comparison ---
lowest_cost = filtered_df["Cost"].min() if not filtered_df.empty else None
custom_cost = 38332.73  # Replace with dynamic calc if applicable

# --- Title ---
st.title("Transmission POI Structure Analyzer")
st.write("Compare the cost of reusing an existing deadend structure versus designing a custom one.")

# --- Table Display ---
st.subheader("Reusable Structures That Meet Requirements")
st.write(f"Found {len(filtered_df)} structure(s) that meet or exceed requirements.")
st.dataframe(filtered_df, use_container_width=True)

# --- Cost Metric Comparison ---
st.subheader("Cost Comparison")
col1, col2 = st.columns(2)
col1.metric("Lowest Reuse Structure Cost", f"${lowest_cost:,.2f}" if lowest_cost else "N/A")
col2.metric("Estimated Custom Cost", f"${custom_cost:,.2f}")

# --- Recommendation Box ---
if lowest_cost and lowest_cost > custom_cost:
    st.success("✅ Custom structure is recommended.\nLower cost and tailored performance.")
elif lowest_cost:
    st.warning("⚠️ Consider using an existing structure.\nIt may save cost if schedule or complexity are key.")
else:
    st.error("❌ No reusable structures meet the requirements.\nCustom structure required.")

# --- Optional: Highlight recommended structure
if lowest_cost:
    rec_row = filtered_df[filtered_df["Cost"] == lowest_cost].iloc[0]
    st.markdown(f"""
    ### 🏗️ Recommended Structure
    - **Structure ID**: `{rec_row["Str #"]}`
    - **Height**: `{rec_row["Height (Feet)"]} ft`
    - **Moment Capacity**: `{rec_row["Maximum Bending Moment (Ft-Kips)"]} Ft-Kips`
    - **Cost**: `${rec_row["Cost"]:,.2f}`
    """)

# --- Interactive Altair Bar Chart ---
import pandas as pd
import altair as alt

st.subheader("Visual Cost Comparison")

# Prepare data
cost_data = pd.DataFrame({
    'Structure Type': ['Custom', 'Lowest Reuse'],
    'Cost': [custom_cost, lowest_cost if lowest_cost else 0]
})

# Create Altair chart
chart = (
    alt.Chart(cost_data)
    .mark_bar()
    .encode(
        x=alt.X('Structure Type:N', title='Structure Type'),
        y=alt.Y('Cost:Q', title='Cost ($)', scale=alt.Scale(zero=True)),
        color=alt.Color('Structure Type:N', scale=alt.Scale(domain=['Custom', 'Lowest Reuse'],
                                                           range=['#7B2CBF', '#2B9348'])),
        tooltip=[alt.Tooltip('Structure Type:N'), alt.Tooltip('Cost:Q', format='$,.2f')]
    )
    .properties(
        width=500,
        height=300,
        title='Custom vs Existing Structure Cost'
    )
)

# Add labels on top of bars
text = (
    alt.Chart(cost_data)
    .mark_text(dy=-10, fontSize=14, fontWeight='bold')
    .encode(
        x='Structure Type:N',
        y='Cost:Q',
        text=alt.Text('Cost:Q', format='$,.0f')
    )
)

# Display chart
st.altair_chart(chart + text, use_container_width=True)
st.caption("This chart compares the estimated cost of a custom structure versus the lowest-cost reusable structure that meets requirements.")
