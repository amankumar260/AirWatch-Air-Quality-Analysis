from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = ROOT / "data" / "processed" / "air_quality_cleaned.csv"
FALLBACK_DATA = ROOT / "data" / "SYNTHETIC_demo_air_quality.csv"

st.set_page_config(page_title="AirWatch | Air Quality Intelligence", page_icon="🌫️", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme / styling ----------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(circle at 12% 0%, #14243b 0, #0a1220 36%, #080e18 100%); }
.block-container { padding-top: 1.35rem; padding-bottom: 2.2rem; max-width: 1600px; }
[data-testid="stSidebar"] { background: #0b1422; border-right: 1px solid #24354b; }
.hero { padding: 1.2rem 1.45rem; border: 1px solid #263b55; border-radius: 18px; background: linear-gradient(120deg, rgba(24,46,72,.95), rgba(14,25,42,.88)); margin-bottom: 1rem; }
.hero-kicker { color: #7dd3fc; text-transform: uppercase; letter-spacing: .16em; font-size: .73rem; font-weight: 700; }
.hero-title { color: #f2f7ff; font-size: 2.15rem; font-weight: 800; line-height: 1.15; margin: .3rem 0 .45rem 0; }
.hero-sub { color: #a9bdd3; font-size: .98rem; }
.metric-card { background: linear-gradient(145deg, rgba(21,38,59,.98), rgba(12,23,38,.98)); border: 1px solid #2a405a; border-radius: 15px; padding: 1rem 1.05rem; min-height: 112px; }
.metric-label { color: #9db3cb; font-size: .82rem; font-weight: 600; margin-bottom: .55rem; }
.metric-value { color: #f4f8ff; font-size: 1.8rem; font-weight: 800; line-height: 1.1; }
.metric-note { color: #76d9b0; font-size: .75rem; margin-top: .45rem; }
.section-title { color: #e8f1ff; font-size: 1.12rem; font-weight: 750; margin: .35rem 0 .15rem 0; }
.section-sub { color: #8fa7c1; font-size: .8rem; margin-bottom: .55rem; }
.panel { background: rgba(13,24,39,.62); border: 1px solid #243850; border-radius: 16px; padding: .6rem .7rem .15rem .7rem; }
.small-muted { color: #8fa7c1; font-size: .82rem; }
div[data-testid="stDownloadButton"] button { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file)
    elif DEFAULT_DATA.exists():
        raw = pd.read_csv(DEFAULT_DATA)
    elif FALLBACK_DATA.exists():
        raw = pd.read_csv(FALLBACK_DATA)
    else:
        return pd.DataFrame()
    raw.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in raw.columns]
    aliases = {"city_name":"city", "city_average_aqi_value":"aqi", "aqi_value":"aqi", "date_of_observation":"date", "observation_date":"date", "category":"aqi_category", "pollutant":"dominant_pollutant", "state_name":"state"}
    raw = raw.rename(columns={k:v for k,v in aliases.items() if k in raw.columns})
    needed = {"date", "city", "aqi"}
    if not needed.issubset(raw.columns):
        st.error(f"Dataset must contain date, city and aqi columns. Found: {list(raw.columns)}")
        return pd.DataFrame()
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw["city"] = raw["city"].astype("string").str.strip()
    raw["aqi"] = pd.to_numeric(raw["aqi"], errors="coerce")
    if "state" not in raw: raw["state"] = "Unknown"
    if "aqi_category" not in raw:
        raw["aqi_category"] = pd.cut(raw["aqi"], [-np.inf, 50, 100, 200, 300, 400, np.inf], labels=["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"])
    if "dominant_pollutant" not in raw: raw["dominant_pollutant"] = "Not reported"
    raw = raw.dropna(subset=["date", "city", "aqi"])
    raw = raw[(raw["city"].str.len() > 0) & (raw["aqi"] >= 0)].drop_duplicates().copy()
    raw["year"] = raw.date.dt.year
    raw["month"] = raw.date.dt.month
    raw["month_name"] = raw.date.dt.strftime("%b")
    raw["month_start"] = raw.date.dt.to_period("M").dt.to_timestamp()
    raw["aqi_category"] = raw["aqi_category"].astype("string").fillna("Unclassified")
    raw["dominant_pollutant"] = raw["dominant_pollutant"].astype("string").fillna("Not reported")
    return raw.sort_values("date")

def plot_theme(fig, height=330):
    fig.update_layout(template="plotly_dark", height=height, margin=dict(l=12,r=12,t=48,b=12), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Segoe UI, sans-serif", color="#dce8f7"), title_font=dict(size=15, color="#eef5ff"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(gridcolor="rgba(143,167,193,.13)", zerolinecolor="rgba(143,167,193,.15)")
    fig.update_yaxes(gridcolor="rgba(143,167,193,.13)", zerolinecolor="rgba(143,167,193,.15)")
    return fig

def metric(label, value, note):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("## 🌫️ AirWatch")
st.sidebar.caption("Air Quality Intelligence Platform")
uploaded = st.sidebar.file_uploader("Use your own CSV dataset", type=["csv"], help="Required columns: date, city, aqi. Optional: state, aqi_category, dominant_pollutant.")
df = load_data(uploaded)
if df.empty:
    st.warning("No usable data found. Keep the included demo CSV in data/ or upload a CSV with date, city and aqi columns.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### Filter the analysis")
min_date, max_date = df.date.min().date(), df.date.max().date()
date_range = st.sidebar.date_input("Observation period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = pd.Timestamp(min_date), pd.Timestamp(max_date)
base = df[df.date.between(start_date, end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))].copy()

def multi_filter(label, series):
    vals = sorted(series.dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, vals, default=vals)
city_options = multi_filter("City", base.city)
state_options = multi_filter("State", base.state)
category_options = multi_filter("AQI category", base.aqi_category)
pollutant_options = multi_filter("Dominant pollutant", base.dominant_pollutant)
filtered = base[base.city.astype(str).isin(city_options) & base.state.astype(str).isin(state_options) & base.aqi_category.astype(str).isin(category_options) & base.dominant_pollutant.astype(str).isin(pollutant_options)].copy()
if filtered.empty:
    st.warning("No records match these filters. Widen the filters in the sidebar.")
    st.stop()
st.sidebar.markdown("---")
st.sidebar.caption("Demo data is synthetic. Replace it with verified observations before presenting real-world conclusions.")

# ---------- Header ----------
st.markdown('''<div class="hero"><div class="hero-kicker">Environmental analytics · Live local dashboard</div><div class="hero-title">Air Quality Report</div><div class="hero-sub">Explore pollution patterns, city comparisons, category mix and short-horizon trend estimates — all from Python.</div></div>''', unsafe_allow_html=True)

# KPI metrics
avg = filtered.aqi.mean(); median = filtered.aqi.median(); peak = filtered.aqi.max(); cities = filtered.city.nunique(); records = len(filtered)
prev = base[base.date < start_date].aqi.mean() if start_date > df.date.min().normalize() else np.nan
cols = st.columns(5, gap="medium")
with cols[0]: metric("AVERAGE AQI", f"{avg:.1f}", "Mean across selected records")
with cols[1]: metric("PEAK AQI", f"{peak:.0f}", "Highest recorded value")
with cols[2]: metric("MEDIAN AQI", f"{median:.1f}", "Robust central value")
with cols[3]: metric("CITIES COVERED", f"{cities}", "Cities in current selection")
with cols[4]: metric("OBSERVATIONS", f"{records:,}", "Rows after filters")

# AQI Trend overview
st.markdown('<div class="section-title">AQI Trend Overview</div><div class="section-sub">Monthly mean AQI with a 3-month rolling average; filter selections apply to every chart.</div>', unsafe_allow_html=True)
monthly = filtered.groupby("month_start", as_index=False).agg(mean_aqi=("aqi","mean"), median_aqi=("aqi","median"), observations=("aqi","size"))
monthly = monthly.sort_values("month_start")
monthly["rolling_3m"] = monthly.mean_aqi.rolling(3, min_periods=1).mean()
fig = go.Figure()
fig.add_trace(go.Scatter(x=monthly.month_start, y=monthly.mean_aqi, mode="lines+markers", name="Monthly mean", line=dict(color="#38bdf8", width=3), marker=dict(size=6), fill="tozeroy", fillcolor="rgba(56,189,248,.08)"))
fig.add_trace(go.Scatter(x=monthly.month_start, y=monthly.rolling_3m, mode="lines", name="3-month rolling mean", line=dict(color="#a78bfa", width=3, dash="dot")))
fig.update_layout(title="Monthly AQI movement", xaxis_title="Month", yaxis_title="Average AQI", hovermode="x unified")
plot_theme(fig, 360); st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False, "responsive":True})

# City ranking panels
left, right = st.columns([1.05, 1], gap="large")
city_stats = filtered.groupby("city", as_index=False).agg(mean_aqi=("aqi","mean"), max_aqi=("aqi","max"), observations=("aqi","size")).sort_values("mean_aqi", ascending=False)
with left:
    st.markdown('<div class="section-title">Most Polluted Cities</div><div class="section-sub">Ranked by mean AQI in the selected period.</div>', unsafe_allow_html=True)
    worst = city_stats.head(8).sort_values("mean_aqi", ascending=True)
    f = px.bar(worst, x="mean_aqi", y="city", orientation="h", color="mean_aqi", color_continuous_scale=["#34d399", "#fbbf24", "#fb7185"], text_auto=".1f", hover_data={"observations":True,"max_aqi":":.0f"})
    f.update_layout(title="Highest average AQI", xaxis_title="Mean AQI", yaxis_title="", coloraxis_showscale=False)
    plot_theme(f, 330); st.plotly_chart(f, use_container_width=True, config={"displaylogo":False})
with right:
    st.markdown('<div class="section-title">Cleanest Cities</div><div class="section-sub">Lowest mean AQI among the selected cities.</div>', unsafe_allow_html=True)
    clean = city_stats.sort_values("mean_aqi", ascending=True).head(8).sort_values("mean_aqi", ascending=False)
    f = px.bar(clean, x="mean_aqi", y="city", orientation="h", color="mean_aqi", color_continuous_scale=["#34d399", "#38bdf8"], text_auto=".1f", hover_data={"observations":True,"max_aqi":":.0f"})
    f.update_layout(title="Lowest average AQI", xaxis_title="Mean AQI", yaxis_title="", coloraxis_showscale=False)
    plot_theme(f, 330); st.plotly_chart(f, use_container_width=True, config={"displaylogo":False})

# Distribution and category analysis
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown('<div class="section-title">AQI Distribution</div><div class="section-sub">Shows the spread and concentration of individual readings.</div>', unsafe_allow_html=True)
    f = px.histogram(filtered, x="aqi", nbins=22, marginal="box", color_discrete_sequence=["#38bdf8"], title="Reading distribution")
    f.update_layout(xaxis_title="AQI", yaxis_title="Number of observations", showlegend=False)
    plot_theme(f, 330); st.plotly_chart(f, use_container_width=True, config={"displaylogo":False})
with c2:
    st.markdown('<div class="section-title">AQI Category Mix</div><div class="section-sub">Composition of records by the category field in the dataset.</div>', unsafe_allow_html=True)
    cats = filtered.groupby("aqi_category", as_index=False).size().sort_values("size", ascending=False)
    f = px.pie(cats, names="aqi_category", values="size", hole=.62, title="Category share", color_discrete_sequence=["#34d399", "#38bdf8", "#fbbf24", "#fb7185", "#a78bfa", "#f97316"])
    f.update_traces(textposition="inside", textinfo="percent+label")
    plot_theme(f, 330); st.plotly_chart(f, use_container_width=True, config={"displaylogo":False})

# Heatmap and pollutant breakdown
c3, c4 = st.columns(2, gap="large")
with c3:
    st.markdown('<div class="section-title">City × Month Heatmap</div><div class="section-sub">Quickly spots periods when city-level mean AQI was elevated.</div>', unsafe_allow_html=True)
    heat = filtered.pivot_table(index="city", columns="month_name", values="aqi", aggfunc="mean")
    month_order = [pd.Timestamp(2000, m, 1).strftime("%b") for m in range(1,13)]
    heat = heat.reindex(columns=[m for m in month_order if m in heat.columns])
    if not heat.empty:
        f = px.imshow(heat, aspect="auto", color_continuous_scale="RdYlGn_r", labels=dict(x="Month", y="City", color="Mean AQI"), title="Average AQI by city and calendar month")
        plot_theme(f, max(300, min(470, 180 + 26*len(heat))))
        st.plotly_chart(f, use_container_width=True, config={"displaylogo":False})
    else: st.info("Not enough records for a heatmap.")
with c4:
    st.markdown("<div class='section-title'>Dominant Pollutants</div><div class='section-sub'>Counts from the dataset's dominant-pollutant labels, not pollutant concentration measurements.</div>", unsafe_allow_html=True)
    pol = filtered.groupby("dominant_pollutant", as_index=False).size().sort_values("size", ascending=True)
    f = px.bar(pol, x="size", y="dominant_pollutant", orientation="h", text="size", color="size", color_continuous_scale="Blues", title="Records by dominant pollutant")
    f.update_layout(xaxis_title="Observation count", yaxis_title="", coloraxis_showscale=False)
    plot_theme(f, 330); st.plotly_chart(f, use_container_width=True, config={"displaylogo":False})

# Analytics / anomaly flags
st.markdown('<div class="section-title">Advanced Analytics</div><div class="section-sub">Transparent IQR-based anomaly flagging and a simple baseline forecast. Forecasts are exploratory, not official air-quality predictions.</div>', unsafe_allow_html=True)
a1, a2 = st.columns([1,1], gap="large")
q1, q3 = filtered.aqi.quantile([.25,.75]); iqr = q3-q1
lo, hi = q1-1.5*iqr, q3+1.5*iqr
anoms = filtered[(filtered.aqi < lo) | (filtered.aqi > hi)].copy()
with a1:
    st.markdown("**Potential AQI outliers**")
    st.metric("Flagged observations", f"{len(anoms)}", help="IQR rule: values below Q1 − 1.5×IQR or above Q3 + 1.5×IQR. Flags warrant review; they are not proof of erroneous data.")
    if not anoms.empty:
        st.dataframe(anoms[["date","city","state","aqi","aqi_category","dominant_pollutant"]].sort_values("aqi", ascending=False).head(12), use_container_width=True, hide_index=True)
    else: st.success("No AQI values were flagged by the IQR rule for this selection.")
with a2:
    st.markdown("**Next 3 months — baseline estimate**")
    if len(monthly) >= 3:
        # Linear trend fit to monthly means; clip forecast to non-negative AQI.
        x = np.arange(len(monthly), dtype=float); y = monthly.mean_aqi.to_numpy(dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        future_x = np.arange(len(monthly), len(monthly)+3, dtype=float)
        forecast = np.maximum(0, slope*future_x + intercept)
        future_dates = pd.date_range(monthly.month_start.max() + pd.offsets.MonthBegin(1), periods=3, freq="MS")
        forecast_df = pd.DataFrame({"Month": future_dates, "Estimated mean AQI": forecast.round(1)})
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)
        ff = go.Figure()
        ff.add_trace(go.Scatter(x=monthly.month_start, y=monthly.mean_aqi, mode="lines+markers", name="Observed", line=dict(color="#38bdf8", width=2)))
        ff.add_trace(go.Scatter(x=future_dates, y=forecast, mode="lines+markers", name="Linear baseline", line=dict(color="#fbbf24", width=3, dash="dash")))
        ff.update_layout(title="Observed vs. baseline trend extension", xaxis_title="Month", yaxis_title="Mean AQI")
        plot_theme(ff, 270); st.plotly_chart(ff, use_container_width=True, config={"displaylogo":False})
    else:
        st.info("Select a period containing at least three months to show a baseline forecast.")

# Data table and downloads
st.markdown('<div class="section-title">Explore and Export Data</div><div class="section-sub">Inspect filtered observations and download the current analysis for your report.</div>', unsafe_allow_html=True)
with st.expander("Open filtered observation table", expanded=False):
    st.dataframe(filtered.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
summary_csv = city_stats.to_csv(index=False).encode("utf-8")
filtered_csv = filtered.to_csv(index=False).encode("utf-8")
anomaly_csv = anoms.to_csv(index=False).encode("utf-8")
d1,d2,d3 = st.columns(3)
with d1: st.download_button("⬇️ Download filtered data", filtered_csv, "airwatch_filtered_data.csv", "text/csv", use_container_width=True)
with d2: st.download_button("⬇️ Download city summary", summary_csv, "airwatch_city_summary.csv", "text/csv", use_container_width=True)
with d3: st.download_button("⬇️ Download flagged outliers", anomaly_csv, "airwatch_aqi_outliers.csv", "text/csv", use_container_width=True)

with st.expander("About this project / methodology"):
    st.markdown("""
    **Project:** AirWatch — Air Quality Analysis and Monitoring Dashboard.  
    **Stack:** Python, Streamlit, Pandas, NumPy and Plotly.  
    **Data pipeline:** column standardisation → date/numeric parsing → invalid-row removal → duplicate removal → derived time dimensions.  
    **Trend:** monthly mean AQI and 3-month rolling mean.  
    **Outliers:** transparent 1.5×IQR rule.  
    **Forecast:** straight-line least-squares extension of monthly means for three months. It is a baseline demonstration only; it does not model seasonality, meteorology, emissions or uncertainty.  
    **Data limitation:** the included starter dataset is synthetic demo data. Replace it with an authoritative dataset and cite the source before making real-world claims. The pollutant field is a dominant-pollutant label, not concentration data.
    """)

st.markdown('<div class="small-muted">AirWatch · Python-only interactive dashboard · Built for local use in VS Code</div>', unsafe_allow_html=True)
