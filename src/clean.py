from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("data/raw")
CLEAN = Path("data/clean")
REPORTS = Path("reports")
CLEAN.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

COLUMNS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
           "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"]
FILES = {
    "cleveland": "processed.cleveland.data",
    "hungarian": "processed.hungarian.data",
    "switzerland": "processed.switzerland.data",
    "va": "processed.va.data",
}

log = []  # every cleaning action gets recorded here


def record(step, column, rows_affected, action, reason):
    log.append({"step": step, "column": column, "rows_affected": int(rows_affected),
                "action": action, "reason": reason})


# ---------- 1. LOAD (raw files are only read, never modified) ----------
frames = []
for source, fname in FILES.items():
    d = pd.read_csv(RAW / fname, header=None, names=COLUMNS, dtype=str)
    d["source"] = source
    frames.append(d)
df = pd.concat(frames, ignore_index=True)
df = df.replace("?", np.nan)
df[COLUMNS] = df[COLUMNS].apply(pd.to_numeric, errors="coerce")
df.to_csv(CLEAN / "_before_snapshot.csv", index=False)  # used for before/after later

# ---------- 2. DISGUISED MISSING VALUES -> NaN ----------
n = (df["chol"] == 0).sum()
df.loc[df["chol"] == 0, "chol"] = np.nan
record(1, "chol", n, "set to missing", "Cholesterol of 0 mg/dl is physiologically impossible; means not measured")

n = (df["trestbps"] == 0).sum()
df.loc[df["trestbps"] == 0, "trestbps"] = np.nan
record(2, "trestbps", n, "set to missing", "Resting blood pressure of 0 is impossible")

n = (df["oldpeak"] < 0).sum()
df.loc[df["oldpeak"] < 0, "oldpeak"] = np.nan
record(3, "oldpeak", n, "set to missing", "ST depression cannot be negative per documentation; treated as invalid entries")

# ---------- 3. DUPLICATES ----------
n = df.duplicated().sum()
df = df.drop_duplicates().reset_index(drop=True)
record(4, "all", n, "dropped rows", "Exact duplicate records (same patient entered twice)")

# ---------- 4. DROP COLUMNS WITH >50% MISSING ----------
for col in ["ca", "thal"]:
    n = df[col].isna().sum()
    pct = df[col].isna().mean() * 100
    df = df.drop(columns=col)
    record(5, col, n, "dropped column",
           f"{pct:.0f}% missing, concentrated in 3 of 4 hospitals; imputing would invent most of the column")

# ---------- 5. DROP ROWS WITH NEGLIGIBLE MISSING ----------
n = df["restecg"].isna().sum()
df = df.dropna(subset=["restecg"]).reset_index(drop=True)
record(6, "restecg", n, "dropped rows", "Only a handful of rows (<1%); imputing not worth the bias")

# ---------- 6. IMPUTE (with a flag column so every fill is traceable) ----------
numeric_cols = ["trestbps", "chol", "thalach", "oldpeak"]
categorical_cols = ["fbs", "exang", "slope"]

for col in numeric_cols + categorical_cols:
    n = df[col].isna().sum()
    df[f"{col}_was_missing"] = df[col].isna().astype(int)
    if col in numeric_cols:
        fill = df[col].median()
        method = f"median ({fill})"
        why = "Median is robust to the outliers we deliberately kept"
    else:
        fill = df[col].mode().iloc[0]
        method = f"mode ({fill})"
        why = "Categorical/binary column; most frequent value used"
    df[col] = df[col].fillna(fill)
    record(7, col, n, f"imputed with {method}", why)

# ---------- 7. FIX TYPES ----------
int_cols = ["age", "sex", "cp", "fbs", "restecg", "exang", "slope", "num"]
df[int_cols] = df[int_cols].astype(int)

# ---------- 8. SAVE ----------
df.to_csv(CLEAN / "heart_disease_clean.csv", index=False)
pd.DataFrame(log).to_csv(REPORTS / "cleaning_log.csv", index=False)
print(pd.DataFrame(log).to_string(index=False))
print("\nFinal shape:", df.shape)
print("Remaining nulls:", int(df.isna().sum().sum()))