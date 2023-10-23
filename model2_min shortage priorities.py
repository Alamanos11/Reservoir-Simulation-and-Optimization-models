# -*- coding: utf-8 -*-
"""
Created on OCTOBER 2023

@author: Angelos Alamanos
"""

# Change to your path 
import os
os.chdir("D:/your/path/...")


# Import necessary libraries
import pulp
import matplotlib.pyplot as plt

# Define the variables
months = range(1, 13)

# Reservoir variables (example values - insert data)
S = pulp.LpVariable.dicts("Storage", months, lowBound=0, cat='Continuous')
K = 100000000  # Reservoir capacity (m^3)
S0 = 50000000  # Initial storage (m^3)

# Inflows  (example values - insert data)
I_values = [3000000, 2900000, 2700000, 2600000, 2200000, 2000000, 150000, 900000, 1500000, 1800000, 2000000, 2500000]
I = {t: I_values[t-1] for t in months}

# Outflows (example values - insert data)
O_values = [250000, 250000, 250000, 500000, 500000, 500000, 500000, 500000, 500000, 250000, 250000, 250000]
O = {t: O_values[t-1] for t in months}

# Releases for urban, agricultural, and hydropower
R_u = pulp.LpVariable.dicts("Release_Urban", months, lowBound=0, cat='Continuous')
R_irr = pulp.LpVariable.dicts("Release_Agricultural", months, lowBound=0, cat='Continuous')
R_hydro = pulp.LpVariable.dicts("Release_Hydropower", months, lowBound=0, cat='Continuous')

# Demand values for urban, agricultural, and hydropower (example values - insert data)
D_u_values = [1100000, 1100000, 1100000, 1200000, 1500000, 1700000, 1800000, 1700000, 1200000, 1100000, 1100000, 1100000]
D_irr_values = [1500000, 1500000, 2000000, 3000000, 5000000, 5500000, 5800000, 6000000, 4500000, 1500000, 1500000, 1500000]
D_hydro_values = [900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000]

D_u = {t: D_u_values[t-1] for t in months}
D_irr = {t: D_irr_values[t-1] for t in months}
D_hydro = {t: D_hydro_values[t-1] for t in months}

# Initialize the optimization model
model = pulp.LpProblem("Reservoir_Optimization", pulp.LpMaximize)

# Define the objective function to maximize total storage
model += pulp.lpSum([S[t] for t in months])

# Add constraints
for t in months:
    if t == 1:
        model += S[t] == S0 + I[t] - O[t] - R_u[t] - R_irr[t] - R_hydro[t]
    else:
        model += S[t] == S[t-1] + I[t] - O[t] - R_u[t] - R_irr[t] - R_hydro[t]
    model += S[t] <= K  # Storage capacity constraint

    # Conditional constraints for prioritizing demands
    # Priority 1: Urban demand
    if D_u[t] > 0:
        model += R_u[t] == D_u[t]
        model += R_irr[t] <= S[t] - R_u[t]
        model += R_hydro[t] <= S[t] - R_u[t]
    else:
        model += R_u[t] == 0
        model += R_irr[t] == 0
        model += R_hydro[t] == 0

    # Priority 2: Agricultural demand (minimum 40% coverage during specific months)
    if D_irr[t] > 0:
        model += R_irr[t] == D_irr[t] if t not in [6, 7, 8] else R_irr[t] == D_irr[t] * 0.4
        model += R_hydro[t] <= S[t] - R_u[t] - R_irr[t]
    else:
        model += R_irr[t] == 0

    # Priority 3: Hydropower demand
    if D_hydro[t] > 0:
        model += R_hydro[t] <= S[t] - R_u[t] - R_irr[t]
    else:
        model += R_hydro[t] == 0

# Solve the optimization problem
model.solve()

# Print the results
if pulp.LpStatus[model.status] == "Optimal":
    print("Optimal Solution Found:")
    print(f"Objective Value (Total Storage): {pulp.value(model.objective)}")
    print("\nDecision Variables:")
    for t in months:
        print(f"Month {t}:")
        print(f"Storage (S_{t}): {S[t].varValue} m^3")
        print(f"Release - Urban (R_u_{t}): {R_u[t].varValue} m^3")
        print(f"Release - Agricultural (R_irr_{t}): {R_irr[t].varValue} m^3")
        print(f"Release - Hydropower (R_hydro_{t}): {R_hydro[t].varValue} m^3")
else:
    print("No feasible solution found. Check the parameters and constraints.")

# Visualize the results (storage and releases)
plt.figure(figsize=(12, 8))

# Storage plot
plt.subplot(2, 1, 1)
plt.bar(months, [S[t].varValue for t in months])
plt.title("Optimized Storage over Time")
plt.xlabel("Month")
plt.ylabel("Storage (m^3)")

# Releases plot
plt.subplot(2, 1, 2)
plt.bar(months, [R_u[t].varValue for t in months], label="Urban")
plt.bar(months, [R_irr[t].varValue for t in months], bottom=[R_u[t].varValue for t in months], label="Agricultural")
plt.bar(months, [R_hydro[t].varValue for t in months], bottom=[R_u[t].varValue + R_irr[t].varValue for t in months], label="Hydropower")
plt.title("Optimized Releases over Time")
plt.xlabel("Month")
plt.ylabel("Release (m^3)")
plt.legend(loc="upper right")

plt.tight_layout()
plt.show()