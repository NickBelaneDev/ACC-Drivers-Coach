import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the detailed telemetry data
telemetry_df = pd.read_csv('user_telemetry.csv')

# --- Analysis for T13 Les Fagnes Turn 02 ---
corner_name = 'T13 Les Fagnes Turn 02'
corner_df = telemetry_df[telemetry_df['cornerName'] == corner_name].copy()

# Ensure the data is sorted by distance or time
corner_df = corner_df.sort_values(by='Distance')

# 1. Steering Analysis
# Calculate the rate of change of the steering angle with respect to distance
corner_df['Steer_Rate_of_Change'] = corner_df['STEERANGLE'].diff() / corner_df['Distance'].diff()
# The first value will be NaN, so we fill it with 0
corner_df['Steer_Rate_of_Change'].fillna(0, inplace=True)

# Calculate the "Nervousness Score" - standard deviation of the rate of change
# We multiply by 1000 to get a more readable number
nervousness_score = corner_df['Steer_Rate_of_Change'].std() * 1000

# 2. Create Plots
fig, axes = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
fig.suptitle(f'Driver Input Analysis for: {corner_name}', fontsize=16)

# Plot 1: Steering Angle
axes[0].plot(corner_df['Distance'], corner_df['STEERANGLE'], label='Steering Angle', color='blue')
axes[0].set_ylabel('Steering Angle (deg)')
axes[0].set_title('Steering Input Smoothness')
axes[0].grid(True, linestyle='--', alpha=0.6)
axes[0].legend()
# Add nervousness score to the plot
axes[0].text(0.05, 0.95, f'Nervousness Score: {nervousness_score:.2f}',
             transform=axes[0].transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))


# Plot 2: Throttle Application
axes[1].plot(corner_df['Distance'], corner_df['THROTTLE'], label='Throttle', color='green')
axes[1].set_ylabel('Throttle (%)')
axes[1].set_title('Throttle Application Confidence')
axes[1].grid(True, linestyle='--', alpha=0.6)
axes[1].legend()

# Plot 3: Lateral G-Force
axes[2].plot(corner_df['Distance'], corner_df['G_LAT'], label='Lateral G-Force', color='red')
axes[2].set_xlabel('Distance (m)')
axes[2].set_ylabel('Lateral G-Force (g)')
axes[2].set_title('Vehicle Stability')
axes[2].grid(True, linestyle='--', alpha=0.6)
axes[2].legend()

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('driver_nervousness_analysis.png')

print(f"Analysis complete for {corner_name}.")
print(f"A quantitative 'Nervousness Score' based on steering inputs is: {nervousness_score:.2f}")
print("The lower the score, the smoother and more controlled the driver.")