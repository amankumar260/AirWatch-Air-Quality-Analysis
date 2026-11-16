# Power BI build guide

## Recommended model
Import `air_quality_cleaned.csv` from `data/processed/` using **Get Data → Text/CSV**. Confirm `date` is Date/DateTime, `aqi` is Whole Number/Decimal Number, and `city`, `state`, `aqi_category`, `dominant_pollutant` are Text. If you have a separate Date table, relate `Date[Date]` to `air_quality_cleaned[date]`.

## Suggested measures (adjust table name if needed)
```DAX
Average AQI = AVERAGE(air_quality_cleaned[aqi])
Maximum AQI = MAX(air_quality_cleaned[aqi])
Minimum AQI = MIN(air_quality_cleaned[aqi])
Observation Count = COUNTROWS(air_quality_cleaned)
Cities Covered = DISTINCTCOUNT(air_quality_cleaned[city])
```
These measures describe the records in the selected filters; they are not a health-risk diagnosis.

## Page 1 — National overview
- KPI cards: Average AQI, Maximum AQI, Cities Covered, Observation Count.
- Line chart: Date on X-axis, Average AQI on Y-axis.
- Bar chart: City on axis, Average AQI as value.
- Donut or stacked bar: record count by AQI category.
- Slicers: year, city, state, category.

## Page 2 — City and seasonal comparison
- Matrix: city by month with Average AQI.
- Clustered bar: average AQI by city.
- Stacked column: AQI category counts by city.
- Slicers: year, city, dominant pollutant.

## Page 3 — Data quality and methodology (optional but recommended)
- Cards: cleaned row count, number of cities, date range.
- Table showing nulls/duplicates audit, if the audit CSV is imported.
- Add a visible note that source coverage varies by city and date.

## Formatting
Use clear titles and units, consistent category colors, readable labels, and alt text. Avoid 3D charts. Use the same date range and filters when comparing Power BI and Tableau. Verify any custom AQI category mapping against the source dataset's own definitions.
