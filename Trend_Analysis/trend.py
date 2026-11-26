mport pandas as pd
import pymannkendall as mk

# File paths
path = "/shared/stormcenter/habiba/Eversource_Snowstorms/final/trend_analysis/output/seasonal_summary.csv"

df = pd.read_csv(path)
df = df.sort_values("season").reset_index(drop=True)

# n_storms
mk_n_storms = mk.original_test(df["n_storms"])

# predicted_target
mk_predicted = mk.original_test(df["predicted_target"])

mk_avg_predicted_per_storm=mk.original_test(df["avg_predicted_per_storm"])
mk_hr_n_storms = mk.hamed_rao_modification_test(df["n_storms"])
mk_hr_predicted = mk.hamed_rao_modification_test(df["predicted_target"])

mk_hr_avg_predicted_per_storm=mk.hamed_rao_modification_test(df["avg_predicted_per_storm"])

print("Lag-1 autocorrelation (n_storms):")
print(df["n_storms"].autocorr(lag=1))

print("Lag-1 autocorrelation (predicted_target):")
print(df["predicted_target"].autocorr(lag=1))

print("Lag-1 autocorrelation (avg_predicted_per_storm):")
print(df["avg_predicted_per_storm"].autocorr(lag=1))

print("Original Mann-Kendall: n_storms")

print(mk_n_storms)
print("Original Mann-Kendall: predicted_target")
print(mk_predicted)
print("Original Mann-Kendall: avg_predicted_per_storm")
print(mk_avg_predicted_per_storm)


print("Hamed-Rao MK: n_storms")
print(mk_hr_n_storms)

print("Hamed-Rao MK: predicted_target")
print(mk_hr_predicted)

print("Hamed-Rao MK: avg_predicted_per_storm")
print(mk_hr_avg_predicted_per_storm)
