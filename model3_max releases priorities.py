# -*- coding: utf-8 -*-
"""
Created on October 2023

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
K = 10000000  # Reservoir capacity (m^3)
S0 = 5000000  # Initial storage (m^3)
S_min = 1000000  # Minimum required storage (m^3)

# Inflows (example values - insert data)
I_values = [8200000, 81000000, 8000000, 8000000, 8500000, 9000000, 9000000, 9000000, 8500000, 8000000, 81000000, 8200000]
I = {t: I_values[t-1] for t in months}

# Outflows (example values - insert data)
O_values = [20000, 20000, 20000, 50000, 45000, 45000, 45000, 45000, 45000, 20000,20000, 20000]
O = {t: O_values[t-1] for t in months}

# Releases for urban, agricultural, and hydropower (example values - insert data)
R_u = pulp.LpVariable.dicts("Release_Urban", months, lowBound=0, cat='Continuous')
R_irr = pulp.LpVariable.dicts("Release_Agricultural", months, lowBound=0, cat='Continuous')
R_hydro = pulp.LpVariable.dicts("Release_Hydropower", months, lowBound=0, cat='Continuous')

# Demand values for urban, agricultural, and hydropower (example values - insert data)
D_u_values = [100000, 100000, 130000, 140000, 160000, 180000, 190000, 170000, 140000, 120000, 110000, 110000]
D_irr_values = [900000, 1500000, 2000000, 5500000, 7200000, 7800000, 7800000, 7200000, 6500000, 3500000, 3500000, 900000]
D_hydro_values = [900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000]

D_u = {t: D_u_values[t-1] for t in months}
D_irr = {t: D_irr_values[t-1] for t in months}
D_hydro = {t: D_hydro_values[t-1] for t in months}

# Initialize the optimization model
model = pulp.LpProblem("Reservoir_Optimization", pulp.LpMaximize)

# Define the objective function to maximize total releases
model += pulp.lpSum([R_u[t] + R_irr[t] + R_hydro[t] for t in months])

# Add constraints
for t in months:
    if t == 1:
        model += S[t] == S0 + I[t] - O[t] - R_u[t] - R_irr[t] - R_hydro[t]
    else:
        model += S[t] == S[t-1] + I[t] - O[t] - R_u[t] - R_irr[t] - R_hydro[t]
    model += S_min == S[t]  # Minimum storage constraint (changed to equality)
    model += S[t] <= K  # Storage capacity constraint

    # Conditional constraints for prioritizing demands
    
    # Create binary variables for priorities
Urban_Priority = pulp.LpVariable.dicts("Urban_Priority", months, cat='Binary')
Agricultural_Priority = pulp.LpVariable.dicts("Agricultural_Priority", months, cat='Binary')
Hydropower_Priority = pulp.LpVariable.dicts("Hydropower_Priority", months, cat='Binary')

# Priority 1: Urban demand
for t in months:
    model += R_u[t] >= D_u[t] - (1 - Urban_Priority[t])
    model += R_irr[t] == 0
    model += R_hydro[t] == 0

# Priority 2: Agricultural demand
for t in months:
    if t in [6, 7, 8]:
        model += R_irr[t] >= D_irr[t] * 0.4 - (1 - Agricultural_Priority[t])
    else:
        model += R_irr[t] >= D_irr[t] - (1 - Agricultural_Priority[t])
    model += R_irr[t] <= D_irr[t]  # Upper bound constraint on agricultural demand

# Priority 3: Hydropower demand
for t in months:
    model += R_hydro[t] >= D_hydro[t] - (1 - Hydropower_Priority[t])
    model += R_hydro[t] <= D_hydro[t]  # Upper bound constraint on hydropower demand

# Solve the optimization problem
model.solve()

# Print the results
if pulp.LpStatus[model.status] == "Optimal":
    print("Optimal Solution Found:")
    print(f"Objective Value (Total Releases): {pulp.value(model.objective)}")
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



