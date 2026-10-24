from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("data/raw")
COLUMNS = ["age","sex","cp","trestbps","chol","fbs","restecg",
           "thalach","exang","oldpeak","slope","ca","thal","num"]
FILES = {
    "cleveland": "processed.cleveland.data",
    "hungarian": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va": "processed.va.data",
}

# --- load (same as Stage 1) ---
frames = []
for source, fname in FILES.items():
    d = pd.read_csv(RAW / fname, header=None, names=COLUMNS, dtype=str)
    d["source"] = source
    frames.append(d)
raw = pd.concat(frames, ignore_index=True)

# --- convert: "?" becomes NaN, text becomes numbers ---
df = raw.replace("?", np.nan)
df[COLUMNS] = df[COLUMNS].apply(pd.to_numeric, errors="coerce")

# 1. Missing values: count and percent
missing = df[COLUMNS].isna().sum()
pct = (missing / len(df) * 100).round(1)
print("MISSING VALUES")
print(pd.DataFrame({"missing": missing, "pct": pct})
      .sort_values("pct", ascending=False), "\n")

# 2. Where is it missing? Percent missing per hospital
print("MISSING % BY HOSPITAL")
print(df.groupby("source")[COLUMNS]
        .apply(lambda g: g.isna().mean() * 100).round(0).T, "\n")

# 3. Disguised missing: impossible zeros
print("ZEROS BY HOSPITAL")
print(df.assign(chol_zero=df["chol"] == 0, bp_zero=df["trestbps"] == 0)
        .groupby("source")[["chol_zero", "bp_zero"]].sum(), "\n")

# 4. Duplicates
print("Duplicate rows:", df.duplicated().sum())
print(df.dtypes)
# --- Stage 3: outliers ---
df.loc[df["chol"] == 0, "chol"] = np.nan
df.loc[df["trestbps"] == 0, "trestbps"] = np.nan

rows = []
for col in ["age", "trestbps", "chol", "thalach", "oldpeak"]:
    s = df[col].dropna()
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out = s[(s < low) | (s > high)]
    rows.append([col, q1, q3, low, high, len(out), out.min(), out.max()])

print("\nOUTLIERS (IQR method)")
print(pd.DataFrame(
    rows,
    columns=["col", "Q1", "Q3", "low_fence", "high_fence",
             "n_outliers", "min_outlier", "max_outlier"]
).round(1).to_string(index=False))