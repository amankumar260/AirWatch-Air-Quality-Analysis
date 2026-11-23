Air Quality Intelligence Dashboard

A Python-based air-quality analysis and interactive visualization
project. AirWatch processes air-quality records, summarizes pollution
indicators, and presents the results through a Streamlit dashboard with
interactive charts.

> Dataset note: The supplied starter dataset is named
> `SYNTHETIC_demo_air_quality.csv`. It contains synthetic demonstration
> records, not verified real-world monitoring measurements. Do not
> present its values as official or live air-quality readings.

Project objectives

-   Load and inspect air-quality data stored in CSV format.
-   Clean and validate records before analysis.
-   Summarize AQI by city, category, and time period.
-   Visualize patterns and comparisons using interactive charts.
-   Provide a browser-based dashboard for exploring the dataset.

Technology stack

Technology / library   Role
  ---------------------- -------------------------------------------------------------
  Python                 Main programming language
  Streamlit              Interactive browser-based dashboard
  Pandas                 Reads, cleans, filters, groups, and summarizes tabular data
  NumPy                  Numerical operations
  Plotly Express         Interactive charts and visualizations
  Plotly Graph Objects   Lower-level chart construction
  pathlib                Builds file paths relative to the project directory
  io                     Input/output operations used by the application

Project structure

``` text
AirWatch_PBL/
├── app.py
├── requirements.txt
├── run_dashboard.bat
├── data/
│   ├── SYNTHETIC_demo_air_quality.csv
│   └── processed/
│       ├── air_quality_cleaned.csv
│       ├── city_category_counts.csv
│       ├── city_summary.csv
│       ├── data_quality_audit.csv
│       └── monthly_summary.csv
├── src/
│   ├── clean_analyze.py
│   ├── requirements.txt
│   └── airwatch_analysis.ipynb
├── report/
├── power_bi/
└── tableau/
```

The dashboard is run with `app.py`. Power BI and Tableau are not
required to run the Python dashboard.

Dataset fields

The supplied demonstration CSV contains:

-   `date` -- date associated with the observation
-   `city` -- city name
-   `state` -- state or region
-   `aqi` -- Air Quality Index value in the supplied dataset
-   `aqi_category` -- category assigned to the AQI record
-   `dominant_pollutant` -- pollutant recorded as dominant

The demonstration dataset contains 288 rows across 8 cities, with dates
ranging from 15 February 2022 to 15 December 2024. These are
characteristics of the supplied synthetic dataset, not real monitoring
coverage.

Data processing workflow

1.  Data input: Read the source CSV file.
2.  Inspection: Review column names, row count, dates, and missing
    values.
3.  Cleaning: Apply the cleaning and validation steps implemented in
    `src/clean_analyze.py`.
4.  Analysis: Generate summaries such as average and median AQI,
    city-level summaries, category counts, and monthly summaries.
5.  Output: Save processed CSV files and analysis outputs under
    `data/processed/`.
6.  Visualization: Load the available data in `app.py` and explore
    it through Streamlit.

Consult the generated audit file when describing the data-quality checks
and their results.

Run in Visual Studio Code (Windows)

1. Open the correct folder

Open the folder that directly contains `app.py` and `requirements.txt`
(`AirWatch_PBL`), not its parent folder.

2. Open a terminal

In VS Code, select **Terminal → New Terminal**.

3. Activate the virtual environment

``` powershell
.\.venv\Scripts\Activate.ps1
```

If `.venv` does not exist, create it first:

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

5. Start the dashboard

``` powershell
python -m streamlit run app.py
```

Streamlit normally makes the dashboard available at:

``` text
http://localhost:8501
```

Stop the server with `Ctrl + C` in the terminal.

Optional: run the data-cleaning script

From the project root, if the script and its input file are present:

``` powershell
python src/clean_analyze.py
```

The script writes processed outputs under `data/processed/`, according
to its implementation.

Expected outputs

The project workflow is designed to produce:

-   A cleaned air-quality CSV for dashboard use.
-   City-level summary data.
-   Monthly summary data.
-   AQI category counts.
-   A data-quality audit output.
-   Interactive visualizations in the Streamlit application.

Results depend on the CSV files supplied to the project. The included
synthetic dataset demonstrates the analysis and visualization workflow.

Limitations

-   The included demo dataset is synthetic, not live or official
    air-quality data.
-   Results are limited by the fields, coverage, and quality of the
    input CSV.
-   Patterns in synthetic demonstration data cannot establish actual
    pollution conditions or causes.
-   For a real-world study, replace the demo file with a documented
    dataset from a reliable monitoring source and retain its source and
    collection details.

Future enhancements

-   Integrate verified data from official air-quality monitoring
    sources.
-   Add source attribution, update timestamps, and data-freshness
    indicators.
-   Add pollutant-specific analysis when the input contains pollutant
    measurements.
-   Add maps when reliable geographic coordinates are available.
-   Add automated data validation and tests.
-   Deploy the Streamlit application to a hosting service.

GitHub upload

A suitable root-level `.gitignore` includes:

``` gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.ipynb_checkpoints/
.env
.env.*
.streamlit/secrets.toml
.vscode/
.DS_Store
Thumbs.db
*.log
```

Do not commit passwords, API keys, tokens, or private configuration
files.

Author and project details

Complete this section before submission:

-   Project: AirWatch -- Air Quality Intelligence Dashboard
-   Student name(s): Add all project team members
-   Department: Add your department
-   College / university: Add your institution
-   Project guide: Add your guide's name
-   Academic year: Add the applicable academic year

Acknowledgement

The project team would like to thank the project guide and department
faculty for their guidance and feedback during the development of
AirWatch. The team also acknowledges the developers and maintainers of
the open-source Python libraries used in this project.

------------------------------------------------------------------------

For academic submission: Clearly identify the supplied dataset as
synthetic demonstration data unless it has been replaced with verified
real-world data. Describe only the features and processing steps that
are actually present in the submitted code.
