import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Patch, Rectangle
import numpy as np

historical_path = "./historical_snowstorm_predictions.csv"
current_path = "./current_snowstorm_predictions.csv"

output_dir = "./output/"
os.makedirs(output_dir, exist_ok=True)

historical_df = pd.read_csv(historical_path)
current_df = pd.read_csv(current_path)

print(f"Unique storms in historical file: {historical_df['storm_id'].nunique()}")
print(f"Unique storms in current file: {current_df['storm_id'].nunique()}")

df = pd.concat([historical_df, current_df], ignore_index=True)

df["stormCode"] = df["storm_id"].astype(str).str.strip()
df["stormCode_10"] = df["stormCode"].str[:10]

# Make predicted column numeric
df["pred_countts"] = pd.to_numeric(df["pred_countts"], errors="coerce")

storm_summary = (
    df.groupby("stormCode_10", as_index=False)
      .agg(
          pred_countts=("pred_countts", "sum")
      )
)

storm_summary["datetime"] = pd.to_datetime(
    storm_summary["stormCode_10"],
    format="%Y%m%d%H",
    errors="coerce"
)

storm_summary = storm_summary.dropna(subset=["datetime"]).copy()

storm_summary["year"] = storm_summary["datetime"].dt.year
storm_summary["month"] = storm_summary["datetime"].dt.month

# Create Oct-Apr winter season
def get_season(row):
    year = row["year"]
    month = row["month"]

    if month >= 10:
        return f"{year}-{year + 1}"
    elif month <= 4:
        return f"{year - 1}-{year}"
    else:
        return None

storm_summary["season"] = storm_summary.apply(get_season, axis=1)

# Keep only Oct-Apr storms
storm_summary = storm_summary[storm_summary["season"].notna()].copy()

start_season = "1979-1980"
end_season = "2022-2023"

storm_summary = storm_summary[
    (storm_summary["season"] >= start_season) &
    (storm_summary["season"] <= end_season)
].copy()

seasonal_summary = (
    storm_summary.groupby("season", as_index=False)
      .agg(
          n_storms=("stormCode_10", "nunique"),
          predicted_target=("pred_countts", "sum")
      )
)

# Average predicted target per storm
seasonal_summary["avg_predicted_per_storm"] = (
    seasonal_summary["predicted_target"] / seasonal_summary["n_storms"]
).round().astype(int)

# Round predicted target
seasonal_summary["predicted_target"] = (
    seasonal_summary["predicted_target"]
    .round()
    .astype(int)
)

# Save CSV
output_csv = os.path.join(output_dir, "seasonal_summary.csv")
seasonal_summary.to_csv(output_csv, index=False)

# Number of storms
storm_slope = 0.07692307692307693
storm_intercept = 9.346153846153847

# Predicted outages
outage_slope = 100.1995670995671
outage_intercept = 3062.7093073593073

# Seasonal index (starting at 0)
x = np.arange(len(seasonal_summary))

# Calculate Sen's slope trend lines
storm_trend = storm_slope * x + storm_intercept
outage_trend = outage_slope * x + outage_intercept

fig, ax1 = plt.subplots(figsize=(18, 7))

ax1.bar(
    seasonal_summary["season"],
    seasonal_summary["n_storms"],
    alpha=0.65,
    color="steelblue",
    label="Number of Storms"
)

ax1.plot(
    seasonal_summary["season"],
    storm_trend,
    color="darkblue",
    linestyle="--",
    linewidth=2.5,
    label="Linear Fit for Storms"
)

ax1.set_xlabel("Winter Season", fontsize=16)
ax1.set_ylabel("Number of Storms", fontsize=18, labelpad=12)

ax1.tick_params(axis="x", rotation=90, labelsize=12)
ax1.tick_params(axis="y", labelsize=16)

ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

ax2 = ax1.twinx()

ax2.plot(
    seasonal_summary["season"],
    seasonal_summary["predicted_target"],
    marker="o",
    linewidth=2,
    color="red",
    label="Predicted Outages"
)

ax2.plot(
    seasonal_summary["season"],
    outage_trend,
    color="darkred",
    linestyle="--",
    linewidth=2.5,
    label="Linear Fit for Predicted Outages"
)

ax2.set_ylabel("Predicted Outages", fontsize=18, labelpad=12)
ax2.tick_params(axis="y", labelsize=16)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax2.legend(
    lines1 + lines2,
    labels1 + labels2,
    loc="upper left",
    fontsize=13,
    frameon=True
)

border = Rectangle(
    (0.005, 0.005),
    0.99,
    0.99,
    transform=fig.transFigure,
    fill=False,
    edgecolor="black",
    linewidth=1.5,
    zorder=1000
)

fig.add_artist(border)

plt.tight_layout()

output_plot1 = os.path.join(
    output_dir,
    "seasonal_total_predicted.pdf"
)

plt.savefig(
    output_plot1,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print(f"Saved plot: {output_plot1}")

plt.figure(figsize=(18, 7))

plt.plot(
    seasonal_summary["season"],
    seasonal_summary["avg_predicted_per_storm"],
    marker="o",
    linewidth=2
)

plt.xlabel("Winter Season")
plt.ylabel("Average Predicted Outages per Storm")
plt.title("Seasonal Average Predicted Storm Strength")
plt.xticks(rotation=90)
plt.grid(True, alpha=0.3)
plt.tight_layout()

output_plot2 = os.path.join(output_dir, "seasonal_average_strength.png")
plt.savefig(output_plot2, dpi=300, bbox_inches="tight")
plt.close()
