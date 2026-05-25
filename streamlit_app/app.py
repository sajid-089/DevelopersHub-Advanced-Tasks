from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


# -----------------------------
# Page config + CSS (modern UI)
# -----------------------------
st.set_page_config(page_title="Superstore BI Dashboard", layout="wide")

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1300px; }
      .hero {
        border-radius: 18px;
        padding: 18px 18px;
        background: linear-gradient(120deg, rgba(79,70,229,0.18), rgba(16,185,129,0.12));
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 12px;
      }
      .hero h1 { margin: 0; font-size: 28px; }
      .hero p { margin: 6px 0 0 0; opacity: 0.9; }
      .card {
        border-radius: 16px;
        padding: 14px 14px;
        border: 1px solid rgba(255,255,255,0.10);
        background: rgba(255,255,255,0.03);
      }
      .muted { opacity: 0.8; font-size: 13px; }
      .kpi-title { opacity: 0.85; font-size: 13px; margin-bottom: 6px; }
      .kpi-value { font-size: 26px; font-weight: 800; line-height: 1.1; }
      .kpi-sub { opacity: 0.75; font-size: 12px; margin-top: 4px; }
      hr { opacity: 0.2; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Global Superstore — Business Intelligence Dashboard</h1>
      <p class="muted">Filters • KPIs • Animated trends • 3D exploration (Plotly)</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Helpers: loading + mapping
# -----------------------------
def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(".", " ", regex=False)   # Customer.Name -> Customer Name
        .str.replace("_", " ", regex=False)
        .str.replace("-", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
    )
    return df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standard names used in the app:
    Sales, Profit, Customer, Region, Category, Sub-Category, Order Date
    Optional: Segment, State, City, Country, Quantity, Discount
    """
    df = df.copy()
    cols = {c.lower().strip(): c for c in df.columns}

    def pick(*names: str) -> str | None:
        for n in names:
            if n in cols:
                return cols[n]
        return None

    mapping: dict[str, str] = {}

    sales = pick("sales")
    profit = pick("profit")

    # handles Customer Name / Customer ID (including Customer.Name / Customer.ID after normalize)
    customer = pick("customer name", "customer", "customer id", "customername", "customerid")

    region = pick("region")
    category = pick("category")
    subcat = pick("sub category", "sub-category", "subcategory")
    order_date = pick("order date", "orderdate")

    segment = pick("segment")
    state = pick("state")
    city = pick("city")
    country = pick("country")
    quantity = pick("quantity")
    discount = pick("discount")

    if sales: mapping[sales] = "Sales"
    if profit: mapping[profit] = "Profit"
    if customer: mapping[customer] = "Customer"
    if region: mapping[region] = "Region"
    if category: mapping[category] = "Category"
    if subcat: mapping[subcat] = "Sub-Category"
    if order_date: mapping[order_date] = "Order Date"

    if segment: mapping[segment] = "Segment"
    if state: mapping[state] = "State"
    if city: mapping[city] = "City"
    if country: mapping[country] = "Country"
    if quantity: mapping[quantity] = "Quantity"
    if discount: mapping[discount] = "Discount"

    return df.rename(columns=mapping)


@st.cache_data(show_spinner=False)
def load_data(uploaded_file=None, local_path: Path | None = None) -> pd.DataFrame:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding_errors="ignore")
    else:
        df = pd.read_csv(local_path, encoding_errors="ignore")

    df = normalize_cols(df)
    df = standardize_column_names(df)

    # Parse date if present
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    # Coerce numeric fields
    for c in ["Sales", "Profit", "Quantity", "Discount"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def require_cols(df: pd.DataFrame, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.info(f"Available columns: {df.columns.tolist()}")
        st.stop()


def money(x: float) -> str:
    return f"{x:,.2f}"


# -----------------------------
# Sidebar: data source + theme
# -----------------------------
with st.sidebar:
    st.header("Controls")

    theme = st.selectbox("Chart Theme", ["Dark (recommended)", "Light"], index=0)
    px.defaults.template = "plotly_dark" if "Dark" in theme else "plotly_white"

    st.divider()
    st.subheader("Dataset")

    ROOT = Path(__file__).resolve().parents[1]
    default_path = ROOT / "data" / "Global_Superstore.csv"

    uploaded = st.file_uploader("Upload Global Superstore CSV", type=["csv"])
    st.caption("If uploaded, it overrides local data file.")

if uploaded is not None:
    df = load_data(uploaded_file=uploaded)
    st.success("Loaded dataset from uploaded file.")
else:
    if default_path.exists():
        df = load_data(local_path=default_path)
        st.info(f"Loaded dataset from: {default_path}")
    else:
        st.warning("Local dataset not found at `data/Global_Superstore.csv`.")
        st.info("Upload CSV from the sidebar to continue.")
        st.stop()

# Required by task
require_cols(df, ["Sales", "Profit", "Customer"])


# -----------------------------
# Filters (Required: Region/Category/Sub-Category)
# -----------------------------
df_f = df.copy()

with st.sidebar:
    st.subheader("Filters")

    # Date filter (nice extra)
    if "Order Date" in df_f.columns and df_f["Order Date"].notna().any():
        dmin = df_f["Order Date"].min().date()
        dmax = df_f["Order Date"].max().date()
        date_range = st.date_input("Order Date range", value=(dmin, dmax))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start = pd.to_datetime(date_range[0])
            end = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            df_f = df_f[(df_f["Order Date"] >= start) & (df_f["Order Date"] <= end)]

    if "Region" in df_f.columns:
        regions = sorted(df_f["Region"].dropna().unique().tolist())
        region_sel = st.multiselect("Region", regions, default=regions)
        df_f = df_f[df_f["Region"].isin(region_sel)]

    if "Category" in df_f.columns:
        cats = sorted(df_f["Category"].dropna().unique().tolist())
        cat_sel = st.multiselect("Category", cats, default=cats)
        df_f = df_f[df_f["Category"].isin(cat_sel)]

    if "Sub-Category" in df_f.columns:
        subs = sorted(df_f["Sub-Category"].dropna().unique().tolist())
        sub_sel = st.multiselect("Sub-Category", subs, default=subs)
        df_f = df_f[df_f["Sub-Category"].isin(sub_sel)]

    # optional filter
    if "Segment" in df_f.columns:
        segs = sorted(df_f["Segment"].dropna().unique().tolist())
        seg_sel = st.multiselect("Segment", segs, default=segs)
        df_f = df_f[df_f["Segment"].isin(seg_sel)]

    st.caption(f"Rows: {len(df_f):,} / {len(df):,}")


# -----------------------------
# KPIs (Required + extra)
# -----------------------------
total_sales = float(df_f["Sales"].sum(skipna=True))
total_profit = float(df_f["Profit"].sum(skipna=True))
profit_margin = (total_profit / total_sales) if total_sales else np.nan

k1, k2, k3, k4 = st.columns(4)

def kpi_card(title: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="card">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k1:
    kpi_card("Total Sales", money(total_sales), "All filtered orders")
with k2:
    kpi_card("Total Profit", money(total_profit), "Net profit in selection")
with k3:
    kpi_card("Profit Margin", (f"{profit_margin*100:.2f}%" if np.isfinite(profit_margin) else "N/A"), "Profit / Sales")
with k4:
    kpi_card("Unique Customers", f"{df_f['Customer'].nunique():,}", "Customer count in selection")

st.divider()


# -----------------------------
# Tabs layout (pro)
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Customers (Required)", "Animated Trends", "3D Lab", "Data"]
)

# -----------------------------
# Overview
# -----------------------------
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        if "Category" in df_f.columns:
            grp = (df_f.groupby("Category", as_index=False)["Sales"]
                   .sum()
                   .sort_values("Sales", ascending=False))
            fig = px.bar(grp, x="Category", y="Sales", title="Sales by Category", text_auto=".2s")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category column not found.")

    with c2:
        if "Sub-Category" in df_f.columns:
            grp = (df_f.groupby("Sub-Category", as_index=False)["Profit"]
                   .sum()
                   .sort_values("Profit", ascending=False)
                   .head(15))
            fig = px.bar(grp, x="Sub-Category", y="Profit", title="Top Sub-Categories by Profit (Top 15)", text_auto=".2s")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sub-Category column not found.")

    # Extra: Sales vs Profit bubble
    if "Category" in df_f.columns:
        perf = (df_f.groupby("Category", as_index=False)
                .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")))
        fig = px.scatter(perf, x="Sales", y="Profit", size="Sales", color="Category",
                         title="Category Performance (Sales vs Profit)", hover_data=["Sales", "Profit"])
        fig.update_layout(height=400, legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Customers (Required: Top 5 Customers by Sales)
# -----------------------------
with tab2:
    st.subheader("Top 5 Customers by Sales (Required)")

    top5 = (df_f.groupby("Customer", as_index=False)["Sales"]
            .sum()
            .sort_values("Sales", ascending=False)
            .head(5))

    l, r = st.columns([0.55, 0.45])
    with l:
        st.dataframe(top5, use_container_width=True)
    with r:
        fig = px.bar(top5, x="Customer", y="Sales", title="Top 5 Customers — Sales", text_auto=".2s")
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Animated Trends (Plotly animation frames)
# -----------------------------
with tab3:
    st.subheader("Animated Monthly Sales (if Order Date is available)")

    if "Order Date" not in df_f.columns or not df_f["Order Date"].notna().any():
        st.info("Order Date column not found (or not parseable). Animated charts need Order Date.")
    else:
        tmp = df_f.dropna(subset=["Order Date"]).copy()
        tmp["month"] = tmp["Order Date"].dt.to_period("M").astype(str)

        # aggregate for animation
        if "Category" in tmp.columns:
            anim = (tmp.groupby(["month", "Category"], as_index=False)["Sales"].sum())
            fig = px.bar(
                anim, x="Category", y="Sales",
                animation_frame="month",
                color="Category",
                title="Sales by Category — Animated by Month",
                range_y=[0, anim["Sales"].max() * 1.05]
            )
            fig.update_layout(height=520, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Category column not found. Animation skipped.")


# -----------------------------
# 3D Lab (interactive 3D chart)
# -----------------------------
with tab4:
    st.subheader("3D Exploration (Interactive)")

    st.caption("3D is best used for exploration. We sample points to keep it fast.")
    z_choice = st.selectbox("Z-axis", ["Discount", "Quantity"], index=0)

    if z_choice not in df_f.columns:
        st.info(f"Column '{z_choice}' not found. Available: {df_f.columns.tolist()}")
    else:
        # sample for performance
        sample_n = min(4000, len(df_f))
        df_s = df_f.dropna(subset=["Sales", "Profit", z_choice]).sample(sample_n, random_state=42) if len(df_f) > sample_n else df_f

        # camera rotation slider (feels like animation)
        angle = st.slider("Rotate view", 0, 360, 35)
        rad = math.radians(angle)
        camera = dict(eye=dict(x=1.35 * math.cos(rad), y=1.35 * math.sin(rad), z=0.75))

        color_col = "Category" if "Category" in df_s.columns else None

        fig = px.scatter_3d(
            df_s,
            x="Sales",
            y="Profit",
            z=z_choice,
            color=color_col,
            opacity=0.75,
            title=f"3D Scatter: Sales vs Profit vs {z_choice}",
        )
        fig.update_layout(height=650, scene_camera=camera, legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Data tab
# -----------------------------
with tab5:
    st.subheader("Filtered Data Preview")
    st.dataframe(df_f.head(200), use_container_width=True)

    st.download_button(
        "Download filtered CSV",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="superstore_filtered.csv",
        mime="text/csv"
    )

st.caption("Use sidebar filters to analyze Region/Category/Sub-Category performance.")