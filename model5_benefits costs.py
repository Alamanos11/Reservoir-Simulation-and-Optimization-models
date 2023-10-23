# -*- coding: utf-8 -*-
"""
Created on OCTOBER 2023

@author: Angelos Alamanos

"""

# Define your folder path 
import os
os.chdir("D:/your/path/...")

import pulp

# Define the variables
n_users = 3
months = range(1, 13)

# Reservoir variables (example values - insert data)
S = pulp.LpVariable.dicts("Storage", months, lowBound=0, cat='Continuous')
K = 100000000  # Reservoir capacity (m^3)

# User demands (12 different values for each month JAN-DEC) (example values - insert data)
D_u_values = [1100000, 1100000, 1100000, 1200000, 1500000, 1700000, 1800000, 1700000, 1200000, 1100000, 1100000, 1100000]
D_irr_values = [1500000, 1500000, 2000000, 3000000, 5000000, 5500000, 5800000, 6000000, 4500000, 1500000, 1500000, 1500000]
D_hydro_values = [900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000, 900000]

D_u = {t: D_u_values[t-1] for t in months}
D_irr = {t: D_irr_values[t-1] for t in months}
D_hydro = {t: D_hydro_values[t-1] for t in months}

# Spills and environmental flows
Sp = pulp.LpVariable.dicts("Spills", months, lowBound=0, cat='Continuous')
EF = pulp.LpVariable.dicts("Env_Flows", months, lowBound=0, cat='Continuous')

# 12 different values for MinEF, Inflows (I), Evaporation losses (E) and Precipitation (P) (example values - insert data)
MinEF_values = [500000, 500000, 750000, 750000, 750000, 1000000, 1000000, 1000000, 750000, 750000, 750000, 500000]
I_values = [3000000, 2900000, 2700000, 2600000, 2200000, 2000000, 150000, 900000, 1500000, 1800000, 2000000, 2500000]
E_values = [250000, 250000, 250000, 500000, 500000, 500000, 500000, 500000, 500000, 250000, 250000, 250000]
P_values = [1000000, 800000, 600000, 300000, 200000, 100000, 50000, 60000, 150000, 400000, 700000, 900000]

MinEF = {t: MinEF_values[t-1] for t in months}
I = {t: I_values[t-1] for t in months}
E = {t: E_values[t-1] for t in months}
P = {t: P_values[t-1] for t in months}

# Input data (here used just as an initial condition, it is not released later on) (example values - insert data)
S0 = 50000000

# Release variables
R_u = pulp.LpVariable.dicts("Release_Urban", months, lowBound=0, cat='Continuous')
R_irr = pulp.LpVariable.dicts("Release_Agricultural", months, lowBound=0, cat='Continuous')
R_hydro = pulp.LpVariable.dicts("Release_Hydropower", months, lowBound=0, cat='Continuous')

# Benefits and costs (example values - insert data)
Economic_Value_Water = 1  # $/m^3
Cost_Treatment = 0.2  # $/m^3

Crop_Sales = {'A': 2.50, 'B': 2.00, 'C': 1.50, 'D': 1.10}  # $/kg
Crop_Yields = {'A': 700, 'B': 950, 'C': 800, 'D': 600}    # kg
Irrigation_Costs = 0.30  # $/m^3

Electricity_Produced = 14.705  #  = 1/0.068 kWh/m3
Price_Electricity = 0.15  # $/kWh
Hydropower_Operation_Costs = 0.03  # $/m^3

# Cost Function for Environmental Flow Violations
PenaltyRate = 10  # $/m^3

# Define Objective Function
model = pulp.LpProblem("Reservoir_Optimization", pulp.LpMaximize)

# Benefits from releases
B_R_u = sum(Economic_Value_Water * R_u[t] - Cost_Treatment * R_u[t] for t in months)
B_R_irr = sum(Crop_Sales[crop] * Crop_Yields[crop] for crop in Crop_Sales) - Irrigation_Costs * sum(R_irr[t] for t in months)
B_R_hydro = sum(Electricity_Produced * Price_Electricity * R_hydro[t] - Hydropower_Operation_Costs * R_hydro[t] for t in months)
B_R = B_R_u + B_R_irr + B_R_hydro

# Calculate spill shares for each month
Sp_u = {t: 0.3 * Sp[t] for t in months}
Sp_irr = {t: 0.5 * Sp[t] for t in months}
Sp_hydro = {t: 0.2 * Sp[t] for t in months}

# Costs for spills (updated)
C_sp_u = Economic_Value_Water * sum(Sp_u[t] for t in months)
C_sp_irr = Irrigation_Costs * sum(Sp_irr[t] for t in months)
C_sp_hydro = Hydropower_Operation_Costs * sum(R_hydro[t] for t in months)
C_sp = C_sp_u + C_sp_irr + C_sp_hydro


# Binary variables for environmental flow violation
EF_violation = pulp.LpVariable.dicts("EF_Violation", months, cat='Binary')

# Cost for not meeting environmental flow
for t in months:
    model += EF[t] >= MinEF[t] - EF_violation[t]

C_EF = PenaltyRate * sum(EF_violation[t] for t in months)

# Objective function
model += B_R - C_sp - C_EF

# Constraints
# Storage balance equation
for t in months:
    if t == 1:
        model += S[t] == S0 + I[t] - E[t] + P[t] - (R_u[t] + R_irr[t] + R_hydro[t]) - Sp[t] - EF[t]
    else:
        model += S[t] == S[t - 1] + I[t] - E[t] + P[t] - (R_u[t] + R_irr[t] + R_hydro[t]) - Sp[t] - EF[t]

# Storage capacity constraint
for t in months:
    model += S[t] <= K

# Release constraints
for t in months:
    model += R_u[t] == D_u[t]
    model += R_irr[t] == D_irr[t]
    model += R_hydro[t] == D_hydro[t]

# Spill constraints
for t in months:
    model += Sp[t] <= S0

# Environmental flow constraints
model += EF[t] >= MinEF[t] - EF_violation[t]

# Solve the problem
model.solve()

# Print the results
if pulp.LpStatus[model.status] == "Optimal":
    print("Optimal Solution Found:")
    print(f"Objective Value: {pulp.value(model.objective)}")
    print("Storage:")
    for t in months:
        print(f"Month {t}: {S[t].varValue}")
    print("Spills:")
    for t in months:
        print(f"Month {t}: {Sp[t].varValue}")
    print("Env Flows:")
    for t in months:
        print(f"Month {t}: {EF[t].varValue}")
    print("Releases - Urban:")
    for t in months:
        print(f"Month {t}: {R_u[t].varValue}")
    print("Releases - Agriculture:")
    for t in months:
        print(f"Month {t}: {R_irr[t].varValue}")
    print("Releases - Hydropower:")
    for t in months:
        print(f"Month {t}: {R_hydro[t].varValue}")
else:
    print("No feasible solution found. Check the parameters and constraints.")

# -----------------------------------------------------------

#  Plots - results & optimized vs initial values

import matplotlib.pyplot as plt

# Assuming you have already solved the optimization problem and have the results
# Replace the following with your actual data
optimized_storage = [S[t].varValue for t in months]
optimized_spills = [Sp[t].varValue for t in months]
optimized_env_flows = [EF[t].varValue for t in months]
optimized_releases_urban = [R_u[t].varValue for t in months]
optimized_releases_agriculture = [R_irr[t].varValue for t in months]
optimized_releases_hydropower = [R_hydro[t].varValue for t in months]

initial_demand_urban = [D_u[t] for t in months]
initial_demand_agriculture = [D_irr[t] for t in months]
initial_demand_hydropower = [D_hydro[t] for t in months]

# Create subplots
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12, 10))

# Plot Storage
axes[0, 0].bar(months, optimized_storage, color='blue')
axes[0, 0].set_title('Optimized Storage (m³)')
axes[0, 0].set_xlabel('Month')
axes[0, 0].set_ylabel('Storage (m³)')

# Plot Spills
axes[0, 1].bar(months, optimized_spills, color='blue')
axes[0, 1].set_title('Optimized Spills (m³)')
axes[0, 1].set_xlabel('Month')
axes[0, 1].set_ylabel('Spills (m³)')

# Plot Env Flows
axes[1, 0].bar(months, optimized_env_flows, color='blue')
axes[1, 0].set_title('Optimized Environmental Flows (m³)')
axes[1, 0].set_xlabel('Month')
axes[1, 0].set_ylabel('Env Flows (m³)')

# Plot Releases - Urban
axes[1, 1].bar(months, optimized_releases_urban, color='blue', label='Optimized')
axes[1, 1].bar(months, initial_demand_urban, color='red', label='Initial Demand', alpha=0.5)
axes[1, 1].set_title('Urban Releases and Initial Demand (m³)')
axes[1, 1].set_xlabel('Month')
axes[1, 1].set_ylabel('Releases (m³)')
axes[1, 1].legend()

# Plot Releases - Agriculture
axes[2, 0].bar(months, optimized_releases_agriculture, color='blue', label='Optimized')
axes[2, 0].bar(months, initial_demand_agriculture, color='red', label='Initial Demand', alpha=0.5)
axes[2, 0].set_title('Agriculture Releases and Initial Demand (m³)')
axes[2, 0].set_xlabel('Month')
axes[2, 0].set_ylabel('Releases (m³)')
axes[2, 0].legend()

# Plot Releases - Hydropower
axes[2, 1].bar(months, optimized_releases_hydropower, color='blue', label='Optimized')
axes[2, 1].bar(months, initial_demand_hydropower, color='red', label='Initial Demand', alpha=0.5)
axes[2, 1].set_title('Hydropower Releases and Initial Demand (m³)')
axes[2, 1].set_xlabel('Month')
axes[2, 1].set_ylabel('Releases (m³)')
axes[2, 1].legend()

plt.tight_layout()
plt.show()

