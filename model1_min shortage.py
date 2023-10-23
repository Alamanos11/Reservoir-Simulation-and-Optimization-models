# -*- coding: utf-8 -*-
"""
Created on Oct 2023

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
    model += R_u[t] >= D_u[t]  # Release constraints for urban
    model += R_irr[t] >= D_irr[t]  # Release constraints for agriculture
    model += R_hydro[t] >= D_hydro[t]  # Release constraints for hydropower

# Solve the optimization problem
model.solve()

# Print the results
if pulp.LpStatus[model.status] == "Optimal":
    print("Optimal Solution Found:")
    print(f"Objective Value (Total Storage): {pulp.value(model.objective)}")
    print("Decision Variables:")
    for t in months:
        print(f"Month {t}:")
        print(f"  Storage: {S[t].varValue}")
        print(f"  Release - Urban: {R_u[t].varValue}")
        print(f"  Release - Agricultural: {R_irr[t].varValue}")
        print(f"  Release - Hydropower: {R_hydro[t].varValue}")
else:
    print("No feasible solution found. Check the parameters and constraints.")

# Visualize the results using bar diagrams
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.bar(months, [S[t].varValue for t in months], color='blue', label='Optimized Storage (m^3)')
plt.xlabel('Month')
plt.ylabel('Storage (m^3)')
plt.title('Optimized Reservoir Storage Over Months')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.bar(months, [R_u[t].varValue for t in months], color='blue', label='Optimized Release - Urban (m^3)')
plt.bar(months, [D_u[t] for t in months], color='red', alpha=0.5, label='Demand - Urban (m^3)')
plt.xlabel('Month')
plt.ylabel('Release (m^3)')
plt.title('Optimized Releases - Urban vs. Demand')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
