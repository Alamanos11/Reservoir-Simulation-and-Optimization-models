# -*- coding: utf-8 -*-
"""
Created on Oct 2023

@author: Angelos Alamanos
"""

# Define the variables
n_months = 12
months = range(1, n_months + 1)

# Reservoir variables
S = {}  # Storage
R_u = {}  # Releases for urban use
R_irr = {}  # Releases for agricultural use
R_hydro = {}  # Releases for hydropower use
Spills = {}  # Spills from the reservoir

# Parameters (insert input data)
K = 80  # Reservoir capacity (million m³)
S0 = 30  # Initial storage (million m³)
S_min = 15  # Minimum required storage (million m³)

# Demand data (for each of the 12 months) (insert input data)
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

# Inflow and outflow data (for each of the 12 months) - (insert input data) 
# Inflows can be a river input, and/or Precipitation
# Outflows can be Evaporation or other unmanaged outflows
I = {
    1: 70, 2: 80, 3: 90, 4: 70, 5: 45, 6: 30,
    7: 20, 8: 15, 9: 40, 10: 70, 11: 90, 12: 80
}

O = {
    1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10,
    7: 10, 8: 10, 9: 10, 10: 10, 11: 10, 12: 10
}

# Additional parameters (insert input data)
Economic_Value_Water = 1  # $/m³
Cost_of_Treatment = 0.2  # $/m³
Crop_Sales = 2.50  # $/kg
Irrigation_Costs = 0.30  # $/m³
Electricity_Produced_per_m3 = 14.705  # kWh/m³ = 1/0.068 - the power typically produced by 1 m3
Electricity_Price = 0.15  # $/kWh
Hydropower_Operation_Costs = 0.03  # $/m³

Crop_Yields = {
    1: 0, 2: 0, 3: 0, 4: 100, 5: 200, 6: 500,
    7: 600, 8: 700, 9: 500, 10: 200, 11: 100, 12: 0
}  # in kg

# Simulation
for t in months:
    if t == 1:
        # Initial storage
        S[t] = S0 + I[t] - O[t]
    else:
        # Storage balance equation
        S[t] = S[t - 1] + I[t] - O[t]

    # Urban releases (meet urban demand first)
    R_u[t] = min(S[t], D_u[t])
    S[t] -= R_u[t]

    # Agricultural releases (if any surplus is available)
    R_irr[t] = min(S[t], D_irr[t])
    S[t] -= R_irr[t]

    # Hydropower releases (if any surplus is available)
    R_hydro[t] = min(S[t], D_hydro[t])
    S[t] -= R_hydro[t]

    # Calculate spills after applying capacity constraints
    Spills[t] = max(0, S[t] - K)

    # Apply storage capacity constraints
    S[t] = min(max(S_min, S[t]), K)


# Calculations for economic Benefits generated from the Releases (B_R) and C_sp
BR_urban = [((Economic_Value_Water * R_u[t]) - (Cost_of_Treatment * R_u[t])) for t in months]
BR_irr = [(Crop_Sales * Crop_Yields[t] - Irrigation_Costs * R_irr[t]) for t in months]
BR_hydro = [(Electricity_Produced_per_m3 * R_hydro[t] * Electricity_Price - Hydropower_Operation_Costs * R_hydro[t]) for t in months]

# Calculations for economic opportunity costs from the Spills (C_sp) - as shares of the potentially served uses
C_sp_urb = [Economic_Value_Water * 0.17 * Spills[t] for t in months]
C_sp_irr = [Irrigation_Costs * 0.52 * Spills[t] for t in months]
C_sp_hydro = [Electricity_Produced_per_m3 * Electricity_Price * 0.3 * Spills[t] for t in months]


# Print the results - Storage and Spills
print("Month\tStorage (million m³)\tSpills (million m³)")
for t in months:
    print(f"{t}\t{S[t]:.2f}\t\t\t{Spills[t]:.2f}")

# Print the results - Releases (Urban, Agriculture, Hydropower)
print("\nMonth\tUrban Releases (million m³)\tAgricultural Releases (million m³)\tHydropower Releases (million m³)")
for t in months:
    print(f"{t}\t{R_u[t]:.2f}\t\t\t\t{R_irr[t]:.2f}\t\t\t\t{R_hydro[t]:.2f}")

# Print the results - BR (Urban, Agriculture, Hydropower)
print("\nMonth\tBR_urban ($)\tBR_irr ($)\tBR_hydro ($)")
for t in months:
    print(f"{t}\t{BR_urban[t - 1]:.2f}\t\t{BR_irr[t - 1]:.2f}\t\t{BR_hydro[t - 1]:.2f}")

# Print the results - C_sp (Urban, Agriculture, Hydropower)
print("\nMonth\tC_sp_urb ($)\tC_sp_irr ($)\tC_sp_hydro ($)")
for t in months:
    print(f"{t}\t{C_sp_urb[t - 1]:.2f}\t\t{C_sp_irr[t - 1]:.2f}\t\t{C_sp_hydro[t - 1]:.2f}")


######################################################################################
#                             Results Visualization                         #

import matplotlib.pyplot as plt
import numpy as np

# Create lists for plotting
months_list = list(months)
storage_list = [S[t] for t in months]
spills_list = [Spills[t] for t in months]
urban_releases_list = [R_u[t] for t in months]
agricultural_releases_list = [R_irr[t] for t in months]
hydropower_releases_list = [R_hydro[t] for t in months]

# Create subplots for Reservoir Storage and Spills
fig, axs = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: Reservoir Storage
axs[0].plot(months_list, storage_list, marker='o', linestyle='-', color='b')
axs[0].set_title('Reservoir Storage')
axs[0].set_xlabel('Months')
axs[0].set_ylabel('Storage (million m³)')
# Add horizontal line for S_min
axs[0].axhline(y=S_min, color='black', linestyle='--')

# Plot 2: Spills
axs[1].plot(months_list, spills_list, marker='o', linestyle='-', color='orange')
axs[1].set_title('Reservoir Spills')
axs[1].set_xlabel('Months')
axs[1].set_ylabel('Spills (million m³)')
axs[1].axhline(y=0, color='black', linestyle='--')  # Add horizontal line at y=0

# Adjust layout
plt.tight_layout()
plt.show()

# Create subplots for Releases (Urban, Agriculture, Hydropower)
fig, axs = plt.subplots(1, 1, figsize=(12, 8))

# Plots for Releases
axs.plot(months_list, urban_releases_list, marker='o', linestyle='-', color='black', label='Urban Releases')
axs.plot(months_list, agricultural_releases_list, marker='o', linestyle='-', color='red', label='Agricultural Releases')
axs.plot(months_list, hydropower_releases_list, marker='o', linestyle='-', color='blue', label='Hydropower Releases')
axs.set_title('Releases to the water users')
axs.set_xlabel('Months')
axs.set_ylabel('Releases (million m³)')
axs.legend()

# Adjust layout
plt.tight_layout()
plt.show()


####################### Comparative Plots - Demand vs Releases  ###########################

# Create lists for plotting
urban_demands_list = [D_u[t] for t in months]
agricultural_demands_list = [D_irr[t] for t in months]
hydropower_demands_list = [D_hydro[t] for t in months]

# Create a figure with 3 subplots
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

# Bar widths
bar_width = 0.35

# X-axis positions for bars
x = np.arange(len(months_list))

# Bar diagrams for Urban Demand vs Releases
axs[0].bar(x - bar_width/2, urban_demands_list, bar_width, label='Urban Demand', color='b', alpha=0.7)
axs[0].bar(x + bar_width/2, urban_releases_list, bar_width, label='Urban Releases', color='g', alpha=0.7)
axs[0].set_title('Urban Demands vs Releases')
axs[0].set_xlabel('Months')
axs[0].set_ylabel('Million m³')
axs[0].set_xticks(x)
axs[0].set_xticklabels(months_list)
axs[0].legend()

# Bar diagrams for Agricultural Demand vs Releases
axs[1].bar(x - bar_width/2, agricultural_demands_list, bar_width, label='Agricultural Demand', color='b', alpha=0.7)
axs[1].bar(x + bar_width/2, agricultural_releases_list, bar_width, label='Agricultural Releases', color='r', alpha=0.7)
axs[1].set_title('Agricultural Demands vs Releases')
axs[1].set_xlabel('Months')
axs[1].set_ylabel('Million m³')
axs[1].set_xticks(x)
axs[1].set_xticklabels(months_list)
axs[1].legend()

# Bar diagrams for Hydropower Demand vs Releases
axs[2].bar(x - bar_width/2, hydropower_demands_list, bar_width, label='Hydropower Demand', color='b', alpha=0.7)
axs[2].bar(x + bar_width/2, hydropower_releases_list, bar_width, label='Hydropower Releases', color='purple', alpha=0.7)
axs[2].set_title('Hydropower Demands vs Releases')
axs[2].set_xlabel('Months')
axs[2].set_ylabel('Million m³')
axs[2].set_xticks(x)
axs[2].set_xticklabels(months_list)
axs[2].legend()

#######################  Benefits and Costs  ############################

# BR calculations per month
fig, axs = plt.subplots(3, 1, figsize=(12, 12))

# Plot B_R calculations for Urban
axs[0].plot(months_list, BR_urban, marker='o', linestyle='-', color='b', label='BR_urban ($)')
axs[0].set_title('Benefits from Urban Demand Coverage')
axs[0].set_xlabel('Months')
axs[0].set_ylabel('Value ($)')
axs[0].legend()

# Plot B_R calculations for Agricultural
axs[1].plot(months_list, BR_irr, marker='o', linestyle='-', color='r', label='BR_irr ($)')
axs[1].set_title('Benefits from Agricultural Demand Coverage')
axs[1].set_xlabel('Months')
axs[1].set_ylabel('Value ($)')
axs[1].legend()

# Plot B_R calculations for Hydropower
axs[2].plot(months_list, BR_hydro, marker='o', linestyle='-', color='purple', label='BR_hydro ($)')
axs[2].set_title('Benefits from Hydropower Demand Coverage')
axs[2].set_xlabel('Months')
axs[2].set_ylabel('Value ($)')
axs[2].legend()

plt.tight_layout()
plt.show()

# C_sp calculations per month
fig, axs = plt.subplots(3, 1, figsize=(12, 12))

# Plot C_sp calculations for Urban
axs[0].plot(months_list, C_sp_urb, marker='o', linestyle='-', color='b', label='C_sp_urb ($)')
axs[0].set_title('Opportunity Costs of Spills to Urban Demand')
axs[0].set_xlabel('Months')
axs[0].set_ylabel('Value ($)')
axs[0].legend()

# Plot C_sp calculations for Agricultural
axs[1].plot(months_list, C_sp_irr, marker='o', linestyle='-', color='r', label='C_sp_irr ($)')
axs[1].set_title('Opportunity Costs of Spills to Agricultural Demand')
axs[1].set_xlabel('Months')
axs[1].set_ylabel('Value ($)')
axs[1].legend()

# Plot C_sp calculations for Hydropower
axs[2].plot(months_list, C_sp_hydro, marker='o', linestyle='-', color='purple', label='C_sp_hydro ($)')
axs[2].set_title('Opportunity Costs of Spills to Hydropower Demand')
axs[2].set_xlabel('Months')
axs[2].set_ylabel('Value ($)')
axs[2].legend()

plt.tight_layout()
plt.show()
