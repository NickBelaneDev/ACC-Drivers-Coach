import pandas as pd, numpy as np, matplotlib.pyplot as plt

file_path = "assets/MoTec/Spa/Spa-ferrari_296_gt3-8-hotlap_2-17-880.csv"  # <- dein Pfad

# --- Laden ---
df_raw = pd.read_csv(file_path, skiprows=14).drop(0)
for c in df_raw.columns:
    df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce")
df = df_raw.dropna(subset=["Time","Distance","SPEED","G_LAT","ROTY"]).copy()

print(df_raw.columns)

# --- Einheiten & Glättung ---
df["v_ms"] = df["SPEED"] * (1000/3600)
df["roty_rad_s"] = np.deg2rad(df["ROTY"])
dt = df["Time"].diff().astype(float)
win = max(3, int(round(0.10 / float(dt.median()))))  # ~0.1 s Fenster

for col in ["v_ms","G_LAT","roty_rad_s","THROTTLE","BRAKE","STEERANGLE"]:
    df[col+"_sm"] = df[col].rolling(win, center=True, min_periods=1).mean()

# Longitudinal (optional, falls G_LON nicht existiert)
df["G_LON_sm"] = (df["v_ms_sm"].diff() / dt.replace(0, np.nan))

# --- Yaw-Fehler ---
eps = 1e-6
df["yaw_expected"] = df["G_LAT_sm"] / (df["v_ms_sm"].abs() + eps)   # rad/s
df["yaw_error"]    = df["roty_rad_s_sm"] - df["yaw_expected"]
df["rel_yaw_err"]  = df["yaw_error"] / (df["yaw_expected"].abs() + 1e-3)

# --- Flags in Kurven ---
LAT_G_MIN, REL_THR, ABS_YAW_THR = 1.5, 0.25, 0.3
in_corner = df["G_LAT_sm"].abs() > LAT_G_MIN
df["oversteer_flag"]  = in_corner & (df["rel_yaw_err"] >  REL_THR) & (df["roty_rad_s_sm"].abs() > ABS_YAW_THR)
df["understeer_flag"] = in_corner & (df["rel_yaw_err"] < -REL_THR) & (df["roty_rad_s_sm"].abs() > ABS_YAW_THR)

print("Oversteer points:", int(df["oversteer_flag"].sum()))
print("Understeer points:", int(df["understeer_flag"].sum()))

# --- Plots ---
plt.figure(figsize=(12,6))
plt.plot(df["Distance"], df["SPEED"], label="Speed [km/h]"); plt.legend(); plt.grid(True)
plt.xlabel("Distance [m]"); plt.ylabel("Speed [km/h]"); plt.title("Speed Trace")
plt.show()

plt.figure(figsize=(12,6))
plt.plot(df["Distance"], df["THROTTLE_sm"], label="Throttle [%] (sm)")
plt.plot(df["Distance"], df["BRAKE_sm"], label="Brake [%] (sm)")
plt.legend(); plt.grid(True)
plt.xlabel("Distance [m]"); plt.ylabel("Input [%]"); plt.title("Throttle/Brake")
plt.show()

plt.figure(figsize=(12,6))
plt.plot(df["Distance"], df["rel_yaw_err"], label="Rel. Yaw-Error")
plt.scatter(df.loc[df["oversteer_flag"],"Distance"], df.loc[df["oversteer_flag"],"rel_yaw_err"], s=5, color="red", label="Oversteer")
plt.scatter(df.loc[df["understeer_flag"],"Distance"], df.loc[df["understeer_flag"],"rel_yaw_err"], s=5,color="orange", label="Understeer")
plt.axhline(0.25, linestyle="--"); plt.axhline(-0.25, linestyle="--")
plt.legend(); plt.grid(True)
plt.xlabel("Distance [m]"); plt.ylabel("Yaw Error rel."); plt.title("Yaw-Error (Over/Under)")
plt.show()