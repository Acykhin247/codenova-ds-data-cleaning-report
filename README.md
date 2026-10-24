# Data Cleaning Report: UCI Heart Disease Dataset

CodeNova Internship Program, Batch 01, Data Science, **Task 2: Data Cleaning Report**

A reproducible Python pipeline that audits and cleans four hospital heart-disease files, and documents every decision with numbers.

## Results at a glance

| Metric | Before | After |
|---|---|---|
| Rows | 920 | 916 |
| Missing values | 1,759 | 0 |
| Impossible values (e.g. cholesterol = 0) | 185 | 0 |
| Duplicate rows | 2 | 0 |

Only 4 rows (0.4%) were removed. Full details are in the [Data Quality Audit Report](reports/data_quality_audit_report.md).

![Cholesterol before vs after](reports/chol_before_after.png)

## Features

- Loads four headerless files and combines them with a `source` column to track each hospital
- Detects explicit missing values (`?`), **disguised missing values** (impossible zeros and negatives), wrong data types and duplicates
- Detects outliers with the **IQR method**, then separates invalid values from real extremes
- Applies documented cleaning rules: median and mode imputation, dropping columns with over 50% missing
- Adds `<column>_was_missing` flags so imputed values stay traceable
- Writes a machine-readable **cleaning log** (action, rows affected, reason) for every step
- Produces before-and-after comparison tables and a chart
- Leaves raw data untouched

## Tech stack

Python 3, pandas, NumPy, matplotlib (all free and open source)

## Project structure

```
├── data/
│   ├── raw/                  # original files (never modified)
│   └── clean/                # script output
├── src/
│   ├── load.py               # Stage 1: load and combine
│   ├── diagnose.py           # Stages 2-3: missing values, zeros, duplicates, outliers
│   ├── clean.py              # Stage 4: full cleaning pipeline
│   └── compare.py            # Stage 5: before/after tables and chart
├── reports/
│   ├── data_quality_audit_report.md
│   ├── cleaning_log.csv
│   ├── before_after_summary.csv
│   ├── dropped_rows.csv  
│   ├── before_after_columns.csv
│   └── chol_before_after.png
└── README.md
```

## Setup and usage

```bash
pip install pandas numpy matplotlib
python src/clean.py      # produces data/clean/heart_disease_clean.csv and reports/cleaning_log.csv
python src/compare.py    # produces the before/after tables and chart
```

Run the commands from the project root. Run `clean.py` before `compare.py`.

## Key decisions

- Cholesterol and blood pressure of 0 were treated as "not measured", not as real readings
- `ca` (66% missing) and `thal` (53% missing) were dropped instead of imputed
- IQR outliers that are physiologically possible were **kept and flagged**, not deleted
- Imputation used the median (numeric) or mode (categorical) of the whole dataset

## Limitations

- All of Switzerland's cholesterol values were recorded as 0, so they are entirely imputed
- Median imputation reduces variance (cholesterol std 110.8 → 51.9, partly artificial)
- This project covers **data quality only**, not clinical conclusions

## Data Source and License

**Citation:** Janosi, A., Steinbrunn, W., Pfisterer, M., & Detrano, R. (1989). Heart Disease [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C52P4X

**License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/legalcode)

**Changes made:** The original files in `data/raw/` are unmodified. The files in `data/clean/` are an adapted version: impossible values were set to missing, duplicates and two columns were removed, and missing values were imputed, as documented in `reports/data_quality_audit_report.md`.

This project is an independent educational exercise and is not endorsed by the dataset creators.

## Author

Clement Yaw Amegashie, BSc Information Technology, University of Professional Studies, Accra
