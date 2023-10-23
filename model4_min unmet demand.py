# -*- coding: utf-8 -*-
"""
Created on OCTOBER 2023

@author: Angelos Alamanos
"""

import pulp

# Define the variables
n_months = 12
months = range(1, n_months + 1)

# Reservoir variables (example values - insert data)
S = pulp.LpVariable.dicts("Storage", months, lowBound=0, cat='Continuous')
K = 60  # Reservoir capacity (million m³)
S0 = 30  # Initial storage (million m³)
S_min = 2  # Minimum required storage (million m³)

# Demand data (for each of the 12 months) (example values - insert data)
D_u = {
    1: 5, 2: 5, 3: 5, 4: 5, 5: 6, 6: 7,
    7: 8, 8: 9, 9: 7, 10: 6, 11: 5, 12: 5
}

D_irr = {
    1: 10, 2: 14, 3: 15, 4: 20, 5: 22, 6: 30,
    7: 35, 8: 32, 9: 20, 10: 15, 11: 10, 12: 10
}

D_hydro = {
    1: 10, 2: 10, 3: 10, 4: 10, 5: 12, 6: 13,
    7: 15, 8: 15, 9: 12, 10: 10, 11: 10, 12: 10
}

# Inflow and outflow data (for each of the 12 months) (example values - insert data)
I = {
    1: 40, 2: 58, 3: 62, 4: 54, 5: 48, 6: 40,
    7: 42, 8: 40, 9: 56, 10: 64, 11: 62, 12: 60
}

O = {
    1: 20, 2: 20, 3: 20, 4: 20, 5: 20, 6: 25,
    7: 30, 8: 25, 9: 20, 10: 20, 11: 20, 12: 20
}

# Release variables
R_u = pulp.LpVariable.dicts("Release_Urban", months, lowBound=0, cat='Continuous')
R_irr = pulp.LpVariable.dicts("Release_Agricultural", months, lowBound=0, cat='Continuous')
R_hydro = pulp.LpVariable.dicts("Release_Hydropower", months, lowBound=0, cat='Continuous')

# Create the LP problem
model = pulp.LpProblem("Reservoir_Optimization", pulp.LpMinimize)

# Objective: Minimize unmet demand (shortage)
model += sum(D_u[t] - R_u[t] for t in months) + sum(D_irr[t] - R_irr[t] for t in months) + sum(D_hydro[t] - R_hydro[t] for t in months)

# Constraints
for t in months:
    if t == 1:
        # Initial storage
        model += S[t] == S0 + I[t] - O[t] - R_u[t] - R_irr[t] - R_hydro[t]
    else:
        # Storage balance equation
        model += S[t] == S[t - 1] + I[t] - O[t] - R_u[t] - R_irr[t] - R_hydro[t]

    # Storage capacity constraints
    model += S_min <= S[t]
    model += S[t] <= K

# Urban releases should be met every month
for t in months:
    model += R_u[t] == D_u[t]

# Agricultural releases only if there's surplus after meeting urban demand
for t in months:
    model += R_irr[t] >= (D_irr[t] - R_u[t])

# Hydropower releases only if there's surplus after meeting both urban and agricultural demand
for t in months:
    model += R_hydro[t] >= (D_hydro[t] - R_u[t] - R_irr[t])

# Solve the problem
model.solve()

# Print the results
if pulp.LpStatus[model.status] == "Optimal":
    print("Optimal Solution Found:")
    print("Objective Value (Unmet Demand):", pulp.value(model.objective))
    print("\nReleases - Urban:")
    for t in months:
        print(f"Month {t}: {R_u[t].varValue} million m³")
    print("\nReleases - Agricultural:")
    for t in months:
        print(f"Month {t}: {R_irr[t].varValue} million m³")
    print("\nReleases - Hydropower:")
    for t in months:
        print(f"Month {t}: {R_hydro[t].varValue} million m³")
    print("\nStorage:")
    for t in months:
        print(f"Month {t}: {S[t].varValue} million m³")
else:
    print("No feasible solution found. Check the parameters and constraints.")


#############  Visualize the results #########################

import matplotlib.pyplot as plt
import numpy as np

# 1) Reservoir Storage
reservoir_storage = [S[t].varValue for t in months]
plt.figure(figsize=(10, 6))
plt.bar(months, reservoir_storage, color='blue', label='Reservoir Storage')
plt.axhline(y=S_min, color='black', linestyle='--', label='Minimum Storage')
plt.title('Reservoir Storage')
plt.xlabel('Months')
plt.ylabel('million m³')
plt.xticks(months)
plt.legend()
plt.show()

# 2) Urban Demand vs Optimized Releases
urban_demand = np.array([D_u[t] for t in months])
urban_releases = np.array([R_u[t].varValue for t in months])
width = 0.4
x = np.arange(len(months))

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, urban_demand, width=width, color='blue', label='Urban Demand', alpha=0.7)
plt.bar(x + width/2, urban_releases, width=width, color='red', label='Urban Releases', alpha=0.7)
plt.title('Urban Demand vs Optimized Releases')
plt.xlabel('Months')
plt.ylabel('million m³')
plt.xticks(x, months)
plt.legend()
plt.show()

# 3) Agricultural Demand vs Optimized Releases
agricultural_demand = np.array([D_irr[t] for t in months])
agricultural_releases = np.array([R_irr[t].varValue for t in months])

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, agricultural_demand, width=width, color='blue', label='Agricultural Demand', alpha=0.7)
plt.bar(x + width/2, agricultural_releases, width=width, color='red', label='Agricultural Releases', alpha=0.7)
plt.title('Agricultural Demand vs Optimized Releases')
plt.xlabel('Months')
plt.ylabel('million m³')
plt.xticks(x, months)
plt.legend()
plt.show()

# 4) Hydropower Demand vs Optimized Releases
hydropower_demand = np.array([D_hydro[t] for t in months])
hydropower_releases = np.array([R_hydro[t].varValue for t in months])

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, hydropower_demand, width=width, color='blue', label='Hydropower Demand', alpha=0.7)
plt.bar(x + width/2, hydropower_releases, width=width, color='red', label='Hydropower Releases', alpha=0.7)
plt.title('Hydropower Demand vs Optimized Releases')
plt.xlabel('Months')
plt.ylabel('million m³')
plt.xticks(x, months)
plt.legend()
plt.show()

############################################################


