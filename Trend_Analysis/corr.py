import pandas as pd

from scipy.stats import pearsonr, spearmanr

# Read CSV files

sst_df = pd.read_csv("/shared/stormcenter/habiba/Eversource_Snowstorms/final/trend_analysis/winter_season_average_pdo.csv")

outage_df = pd.read_csv("/shared/stormcenter/habiba/Eversource_Snowstorms/final/trend_analysis/output/seasonal_summary.csv")


# Merge by Season

merged = pd.merge(sst_df, outage_df, on="season", how="inner")

print("Matched seasons:", len(merged))

print(merged.head())

# Exact column names

anomaly_col = "Average_pdo"

target_cols = ["n_storms", "predicted_target","avg_predicted_per_storm"]

results = []

for target_col in target_cols:

    temp = merged[[anomaly_col, target_col]].dropna()

    pearson_corr, pearson_p = pearsonr(temp[anomaly_col], temp[target_col])

    spearman_corr, spearman_p = spearmanr(temp[anomaly_col], temp[target_col])

    results.append({

        "Target_Column": target_col,

        "Pearson_Correlation": pearson_corr,

        "Pearson_p_value": pearson_p,

        "Spearman_Correlation": spearman_corr,

        "Spearman_p_value": spearman_p,

        

    })

corr_df = pd.DataFrame(results)

for _, row in corr_df.iterrows():

    print("\n===================================")
    print(f"Target: {row['Target_Column']}")
    print("===================================")

    print(f"Pearson Correlation : {row['Pearson_Correlation']:.4f}")
    print(f"Pearson p-value     : {row['Pearson_p_value']:.4f}")

    print(f"Spearman Correlation: {row['Spearman_Correlation']:.4f}")
    print(f"Spearman p-value    : {row['Spearman_p_value']:.4f}")

#corr_df.to_csv("/shared/stormcenter/habiba/Eversource_Snowstorms/final/trend_analysis/correlation_results_amo.csv", index=False)