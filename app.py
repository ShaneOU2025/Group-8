import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the full dataset from the CSV in the repo
df = pd.read_csv("enhanced_poi_dataset_with_hours.csv")
df["Maximum Bending Moment (Ft-Kips)"] = pd.to_numeric(df["Maximum Bending Moment (Ft-Kips)"].astype(str).str.extract(r"([\d.]+)")[0], errors='coerce')





st.title("Transmission POI Structure Analyzer")
st.markdown("Compare the cost of reusing an existing deadend structure versus designing a custom one.")

# --- User Inputs ---
st.sidebar.header("Design Requirements")
required_moment = st.sidebar.number_input("Required Bending Moment (Ft-Kips)", min_value=0.0, value=2500.0)
required_height = st.sidebar.number_input("Required Structure Height (Feet)", min_value=0.0, value=90.0)

schedule = st.sidebar.selectbox("Project Schedule", ["Slow", "Normal", "Expedited"])
complexity = st.sidebar.selectbox("Project Complexity", ["Low", "Medium", "High"])

# --- Engineering Assumptions ---
steel_rate = 3.50  # $/lb
hourly_rate = 150  # $/hr
avg_weight = df["Weight (lbs)"].mean()
avg_engineer_hours = df["Engineer hours"].astype(float).mean()
avg_moment = df["Maximum Bending Moment (Ft-Kips)"].mean()

schedule_weights = {"Slow": -0.20, "Normal": 0.0, "Expedited": 0.40}
complexity_weights = {"Low": -0.10, "Medium": 0.0, "High": 0.15}

# --- Adjust Engineering Hours ---
adjusted_engineer_hours = avg_engineer_hours * (1 + schedule_weights[schedule] + complexity_weights[complexity])

# --- Estimate Custom Structure Cost ---
cost_steel_custom = steel_rate * (required_moment / avg_moment) * avg_weight
cost_engineering_custom = adjusted_engineer_hours * hourly_rate
custom_total_cost = cost_steel_custom + cost_engineering_custom

# --- Find Reusable Structures ---
matches = df[(df["Maximum Bending Moment (Ft-Kips)"] >= required_moment) &
             (df["Height (Feet)"] >= required_height)]

st.subheader("Reusable Structures That Meet Requirements")
st.write(f"Found {len(matches)} structure(s) that meet or exceed requirements.")
st.dataframe(matches[["Str #", "Height (Feet)", "Maximum Bending Moment (Ft-Kips)", "Weight (lbs)", "Cost"]])

# --- Compare Costs ---
st.subheader("Cost Comparison")

if not matches.empty:
    best_existing_cost = matches["Cost"].min()
    st.write(f"Lowest Cost of Reusable Structure: **${best_existing_cost:,.2f}**")
else:
    best_existing_cost = float('inf')
    st.write("No existing structure meets requirements.")

st.write(f"Estimated Custom Structure Cost: **${custom_total_cost:,.2f}**")

# --- Recommendation ---
if custom_total_cost < best_existing_cost:
    st.success("✅ Recommend: Design a Custom Structure")
else:
    st.success("✅ Recommend: Reuse an Existing Structure")

# --- Visualization ---
st.subheader("Visual Cost Comparison")
costs = {
    "Custom Design": custom_total_cost,
    "Best Existing": best_existing_cost if best_existing_cost < float('inf') else 0
}

fig, ax = plt.subplots()
ax.bar(costs.keys(), costs.values(), color=["purple", "green"])
ax.set_ylabel("Total Cost ($)")
ax.set_title("Custom vs Existing Structure Cost")
st.pyplot(fig)
