from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CLEAN = Path("data/clean")
REPORTS = Path("reports")

before = pd.read_csv(CLEAN / "_before_snapshot.csv")
after = pd.read_csv(CLEAN / "heart_disease_clean.csv")


def impossible(d):
    """Count impossible values: chol=0, trestbps=0, oldpeak<0."""
    return int((d["chol"] == 0).sum() + (d["trestbps"] == 0).sum() + (d["oldpeak"] < 0).sum())


# ---- Table 1: dataset-level summary ----
feature_cols = [c for c in before.columns if c != "source"]
after_feature_cols = [c for c in after.columns if c != "source" and not c.endswith("_was_missing")]
summary = pd.DataFrame({
    "metric": ["rows", "feature columns", "missing values (NaN)", "impossible values", "duplicate rows"],
    "before": [len(before), len(feature_cols), int(before[feature_cols].isna().sum().sum()),
               impossible(before), int(before.duplicated().sum())],
    "after": [len(after), len(after_feature_cols), int(after[after_feature_cols].isna().sum().sum()),
              impossible(after), int(after.duplicated().sum())],
})
print(summary.to_string(index=False), "\n")

# ---- Table 2: per-column profile ----
num_cols = ["trestbps", "chol", "thalach", "oldpeak"]
rows = []
for c in num_cols:
    rows.append({
        "column": c,
        "nulls_before": int(before[c].isna().sum()), "nulls_after": int(after[c].isna().sum()),
        "mean_before": round(before[c].mean(), 1), "mean_after": round(after[c].mean(), 1),
        "median_before": round(before[c].median(), 1), "median_after": round(after[c].median(), 1),
        "std_before": round(before[c].std(), 1), "std_after": round(after[c].std(), 1),
    })
profile = pd.DataFrame(rows)
print(profile.to_string(index=False))

summary.to_csv(REPORTS / "before_after_summary.csv", index=False)
profile.to_csv(REPORTS / "before_after_columns.csv", index=False)

# ---- Chart: cholesterol before vs after ----
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
axes[0].hist(before["chol"].dropna(), bins=30, color="#d9534f")
axes[0].set_title("Cholesterol BEFORE (spike at 0 = not measured)")
axes[1].hist(after["chol"], bins=30, color="#5cb85c")
axes[1].set_title("Cholesterol AFTER (zeros fixed, imputed)")
for ax in axes:
    ax.set_xlabel("chol (mg/dl)")
axes[0].set_ylabel("Number of patients")
plt.tight_layout()
plt.savefig(REPORTS / "chol_before_after.png", dpi=200)
print("\nSaved chart.")