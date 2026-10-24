from pathlib import Path
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

frames = []
for source, fname in FILES.items():
    df = pd.read_csv(RAW / fname, header=None, names=COLUMNS, dtype=str)
    df["source"] = source
    frames.append(df)

raw = pd.concat(frames, ignore_index=True)
print(raw.shape)
print(raw["source"].value_counts())
print((raw == "?").sum())