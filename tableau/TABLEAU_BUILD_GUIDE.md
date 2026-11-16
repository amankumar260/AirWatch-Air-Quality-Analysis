# Tableau build guide

## Connect and prepare
1. Run `src/clean_analyze.py` and create `data/processed/air_quality_cleaned.csv`.
2. In Tableau Desktop, choose **Connect → Text File** and select that CSV.
3. Confirm date, numeric and geographic data types. Assign City/State geographic roles only if Tableau recognizes them correctly; otherwise use the fields as text.
4. Verify date range, city count and row count against the Python audit.

## Worksheets
1. **AQI Trend:** continuous Date on Columns; AVG(AQI) on Rows; line mark.
2. **City Ranking:** City on Rows; AVG(AQI) on Columns; sort descending.
3. **Category Distribution:** AQI Category and COUNT of records; stacked bar.
4. **Seasonality Heatmap:** MONTH(Date) on Columns, City on Rows, AVG(AQI) on Color.
5. **City Detail:** City and Date filters, trend line and detail table.

## Dashboard
- Use a 2-dashboard design: Overview and City Exploration.
- Add Year/Date, City, State and AQI Category filters.
- Enable **Use as Filter** for the city-ranking chart where helpful.
- Add concise tooltips with date, city, average AQI and source context.
- Do not interpret correlation as causation. Do not label the results as a forecast unless a validated forecasting method is actually implemented.

## Server note
Tableau Server/Cloud publishing, permissions, groups and schedules depend on your institution's access/licensing. If no access is available, submit the packaged workbook and screenshots from Tableau Desktop, and explain that server publishing was outside the available environment.
