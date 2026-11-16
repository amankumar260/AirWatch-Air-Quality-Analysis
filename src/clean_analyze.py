"""
AirWatch reproducible analysis pipeline.
Works with the included synthetic demo CSV and common city-average AQI CSV layouts.
Inspect the input file and adjust column mappings if source column names differ.
"""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def standardize_columns(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
    aliases = {
        "city_name": "city", "city_average_aqi_value": "aqi", "aqi_value": "aqi",
        "aqi_category": "aqi_category", "category": "aqi_category",
        "date_of_observation": "date", "observation_date": "date",
        "conditional_pollutant": "dominant_pollutant", "pollutant": "dominant_pollutant",
        "state_name": "state"
    }
    return df.rename(columns={k:v for k,v in aliases.items() if k in df.columns})

def clean_data(df):
    df = standardize_columns(df)
    required = {"date", "city", "aqi"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Required columns not found: {sorted(missing)}. "
            f"Actual columns: {list(df.columns)}. Inspect the source CSV and update mappings."
        )
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["city"] = df["city"].astype("string").str.strip()
    df["aqi"] = pd.to_numeric(df["aqi"], errors="coerce")
    if "state" not in df.columns:
        df["state"] = "Unknown"
    if "aqi_category" not in df.columns:
        # India AQI bands are used for a descriptive category; validate against the dataset's own category field if present.
        bins = [-np.inf, 50, 100, 200, 300, 400, np.inf]
        labels = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
        df["aqi_category"] = pd.cut(df["aqi"], bins=bins, labels=labels)
    if "dominant_pollutant" not in df.columns:
        df["dominant_pollutant"] = "Not reported"
    df = df.dropna(subset=["date", "city", "aqi"])
    df = df[df["city"].str.len() > 0]
    df = df[df["aqi"] >= 0]
    df = df.drop_duplicates()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    return df.sort_values(["date", "city"]).reset_index(drop=True)

def make_outputs(df, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(outdir / "air_quality_cleaned.csv", index=False)
    df.groupby("city", dropna=False).agg(
        observations=("aqi", "count"), mean_aqi=("aqi", "mean"),
        median_aqi=("aqi", "median"), min_aqi=("aqi", "min"),
        max_aqi=("aqi", "max")
    ).round(2).sort_values("mean_aqi", ascending=False).to_csv(outdir / "city_summary.csv")
    df.groupby(["year", "month"], dropna=False).agg(
        mean_aqi=("aqi", "mean"), median_aqi=("aqi", "median"),
        observations=("aqi", "count")
    ).round(2).to_csv(outdir / "monthly_summary.csv")
    df.groupby(["city", "aqi_category"], dropna=False).size().rename("records").reset_index().to_csv(
        outdir / "city_category_counts.csv", index=False
    )
    audit = {
        "rows_after_cleaning": len(df),
        "date_min": str(df["date"].min().date()) if len(df) else None,
        "date_max": str(df["date"].max().date()) if len(df) else None,
        "cities": int(df["city"].nunique()),
        "missing_cells_after_cleaning": int(df.isna().sum().sum()),
        "duplicate_rows_after_cleaning": int(df.duplicated().sum()),
        "mean_aqi": round(float(df["aqi"].mean()), 2) if len(df) else None,
        "median_aqi": round(float(df["aqi"].median()), 2) if len(df) else None,
    }
    pd.Series(audit, name="value").to_csv(outdir / "data_quality_audit.csv")
    if len(df):
        sns.set_theme()
        city = df.groupby("city")["aqi"].mean().sort_values(ascending=False)
        plt.figure(figsize=(10, 6))
        city.plot(kind="bar")
        plt.title("Mean AQI by city")
        plt.ylabel("Mean AQI")
        plt.xlabel("City")
        plt.tight_layout()
        plt.savefig(outdir / "mean_aqi_by_city.png", dpi=160)
        plt.close()
        monthly = df.groupby(df["date"].dt.to_period("M"))["aqi"].mean()
        plt.figure(figsize=(11, 5))
        monthly.index = monthly.index.astype(str)
        monthly.plot()
        plt.title("Mean AQI over time")
        plt.ylabel("Mean AQI")
        plt.xlabel("Month")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(outdir / "mean_aqi_over_time.png", dpi=160)
        plt.close()
    return audit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/SYNTHETIC_demo_air_quality.csv")
    parser.add_argument("--output", default="data/processed")
    args = parser.parse_args()
    raw = pd.read_csv(args.input)
    print("Input columns:", list(raw.columns))
    print("Input rows:", len(raw))
    clean = clean_data(raw)
    audit = make_outputs(clean, args.output)
    print("Audit:", audit)
    print(f"Outputs saved to: {args.output}")

if __name__ == "__main__":
    main()
