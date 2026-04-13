import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meesho Sales Calculator", layout="wide")

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        color: #F26522;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Meesho Sales Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">State-wise Net Sales Summary — TCS Reconciliation</div>', unsafe_allow_html=True)

# ── Column config ─────────────────────────────────────────────────────────────
STATE_COL   = "end_customer_state_new"
QTY_COL     = "quantity"
GST_COL     = "gst_rate"
TAXABLE_COL = "total_taxable_sale_value"
TAX_COL     = "tax_amount"
INVOICE_COL = "total_invoice_value"

REQUIRED_COLS = [STATE_COL, QTY_COL, GST_COL, TAXABLE_COL, TAX_COL, INVOICE_COL]


def validate_columns(df: pd.DataFrame, label: str) -> bool:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        st.error(f"**{label}** is missing columns: `{'`, `'.join(missing)}`\n\n"
                 f"Found: `{'`, `'.join(df.columns.tolist())}`")
        return False
    return True


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with blank/null state."""
    return df[df[STATE_COL].notna() & (df[STATE_COL].astype(str).str.strip() != "")]


def aggregate_by_state(df: pd.DataFrame) -> pd.DataFrame:
    return (
        clean(df)
        .groupby(STATE_COL, sort=True)
        .agg({QTY_COL: "sum", TAXABLE_COL: "sum", TAX_COL: "sum", INVOICE_COL: "sum"})
        .reset_index()
    )


def fmt(val: float) -> str:
    try:
        return f"{int(val):,}" if val == int(val) else f"{val:,.2f}"
    except Exception:
        return f"{val:,.2f}"


def build_summary(sales_agg: pd.DataFrame, ret_agg: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge(
        sales_agg.rename(columns={
            QTY_COL: "S_Qty", TAXABLE_COL: "S_Taxable",
            TAX_COL: "S_Tax", INVOICE_COL: "S_Invoice"
        }),
        ret_agg.rename(columns={
            QTY_COL: "R_Qty", TAXABLE_COL: "R_Taxable",
            TAX_COL: "R_Tax", INVOICE_COL: "R_Invoice"
        }),
        on=STATE_COL, how="outer"
    ).fillna(0)

    merged["N_Qty"]     = merged["S_Qty"]     - merged["R_Qty"]
    merged["N_Taxable"] = merged["S_Taxable"] - merged["R_Taxable"]
    merged["N_Tax"]     = merged["S_Tax"]     - merged["R_Tax"]
    merged["N_Invoice"] = merged["S_Invoice"] - merged["R_Invoice"]

    return merged.sort_values(STATE_COL).reset_index(drop=True)


def compute_grand_total(df: pd.DataFrame) -> dict:
    num_cols = ["S_Qty","S_Taxable","S_Tax","S_Invoice",
                "R_Qty","R_Taxable","R_Tax","R_Invoice",
                "N_Qty","N_Taxable","N_Tax","N_Invoice"]
    return {c: df[c].sum() for c in num_cols}


ORANGE = "#F26522"
RED    = "#c0392b"
GREEN  = "#1e7e45"
BLUE   = "#1F3864"

def display_summary_table(df: pd.DataFrame, totals: dict):
    ordered_cols = [
        STATE_COL,
        "S_Qty","S_Taxable","S_Tax","S_Invoice",
        "R_Qty","R_Taxable","R_Tax","R_Invoice",
        "N_Qty","N_Taxable","N_Tax","N_Invoice",
    ]

    html = f"""
    <style>
    .smtbl {{ border-collapse: collapse; width: 100%; font-size: 12px; font-family: Arial, sans-serif; }}
    .smtbl th, .smtbl td {{ border: 1px solid #ccc; padding: 5px 9px; text-align: right; white-space: nowrap; }}
    .smtbl th {{ text-align: center; color: #fff; }}
    .smtbl td:first-child {{ text-align: left; font-weight: 500; }}
    .smtbl tbody tr:hover td {{ background: #ffe0c8 !important; }}
    .smtbl .grand td {{ font-weight: 700; background: #1F3864 !important; color: #fff !important; }}
    .smtbl .grand td:first-child {{ color: #fff; }}
    .th-s {{ background: {ORANGE}; }}
    .th-r {{ background: {RED};    }}
    .th-n {{ background: {GREEN};  }}
    .th-l {{ background: {BLUE};   }}
    </style>
    <table class="smtbl">
      <thead>
        <tr>
          <th class="th-l" rowspan="2">STATE</th>
          <th class="th-s" colspan="4">REVISED SALES</th>
          <th class="th-r" colspan="4">SALES RETURN</th>
          <th class="th-n" colspan="4">NET SALES</th>
        </tr>
        <tr>
          <th class="th-s">Quantity</th><th class="th-s">Taxable Value</th>
          <th class="th-s">Tax Amount</th><th class="th-s">Invoice Value</th>
          <th class="th-r">Quantity</th><th class="th-r">Taxable Value</th>
          <th class="th-r">Tax Amount</th><th class="th-r">Invoice Value</th>
          <th class="th-n">Quantity</th><th class="th-n">Taxable Value</th>
          <th class="th-n">Tax Amount</th><th class="th-n">Invoice Value</th>
        </tr>
      </thead>
      <tbody>
    """

    # State rows
    for _, row in df.iterrows():
        html += "<tr>"
        for col in ordered_cols:
            val = row.get(col, "")
            if col == STATE_COL:
                html += f"<td>{val}</td>"
            else:
                try:
                    html += f"<td>{fmt(float(val))}</td>"
                except Exception:
                    html += f"<td>{val}</td>"
        html += "</tr>"

    # Grand total row (pinned at bottom, dark blue)
    html += '<tr class="grand">'
    html += "<td>GRAND TOTAL</td>"
    for col in ordered_cols[1:]:
        html += f"<td>{fmt(totals[col])}</td>"
    html += "</tr>"

    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)


def display_grand_total_cards(totals: dict):
    """Show grand total as metric cards at the top."""
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    pairs = [
        (c1, "Net Qty",          totals["N_Qty"]),
        (c2, "Net Taxable Value",totals["N_Taxable"]),
        (c3, "Net Tax Amount",   totals["N_Tax"]),
        (c4, "Net Invoice Value",totals["N_Invoice"]),
        (c5, "Sales Invoice",    totals["S_Invoice"]),
        (c6, "Return Invoice",   totals["R_Invoice"]),
    ]
    for col, label, val in pairs:
        col.metric(label, fmt(val))


# ── File Upload ───────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("##### TCS Sales File")
    sales_file = st.file_uploader("Upload `tcs_sales.xlsx`", type=["xlsx"], key="sales")
with col2:
    st.markdown("##### TCS Sales Return File")
    ret_file = st.file_uploader("Upload `tcs_sales_return.xlsx`", type=["xlsx"], key="returns")

# ── Process ───────────────────────────────────────────────────────────────────
if sales_file and ret_file:
    with st.spinner("Processing files..."):
        try:
            sales_df = pd.read_excel(sales_file)
            ret_df   = pd.read_excel(ret_file)
        except Exception as e:
            st.error(f"Could not read files: {e}")
            st.stop()

    if not validate_columns(sales_df, "Sales file"):
        st.stop()
    if not validate_columns(ret_df, "Sales Return file"):
        st.stop()

    sales_agg = aggregate_by_state(sales_df)
    ret_agg   = aggregate_by_state(ret_df)
    summary   = build_summary(sales_agg, ret_agg)
    totals    = compute_grand_total(summary)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["State Summary", "Raw Data"])

    with tab1:
        st.markdown("#### Grand Total")
        display_grand_total_cards(totals)
        st.markdown("---")
        st.markdown("#### State-wise Net Sales Summary")
        display_summary_table(summary, totals)
        st.markdown("")

        # Download
        export = summary.copy()
        export["GRAND_TOTAL_MARKER"] = ""
        export_cols = {
            STATE_COL: "State",
            "S_Qty": "Sales Qty", "S_Taxable": "Sales Taxable Value",
            "S_Tax": "Sales Tax Amount", "S_Invoice": "Sales Invoice Value",
            "R_Qty": "Return Qty", "R_Taxable": "Return Taxable Value",
            "R_Tax": "Return Tax Amount", "R_Invoice": "Return Invoice Value",
            "N_Qty": "Net Qty", "N_Taxable": "Net Taxable Value",
            "N_Tax": "Net Tax Amount", "N_Invoice": "Net Invoice Value",
        }
        export_df = summary[list(export_cols.keys())].copy()
        export_df.columns = list(export_cols.values())
        # append grand total row
        gt_row = {"State": "GRAND TOTAL"}
        gt_row.update({
            "Sales Qty": totals["S_Qty"], "Sales Taxable Value": totals["S_Taxable"],
            "Sales Tax Amount": totals["S_Tax"], "Sales Invoice Value": totals["S_Invoice"],
            "Return Qty": totals["R_Qty"], "Return Taxable Value": totals["R_Taxable"],
            "Return Tax Amount": totals["R_Tax"], "Return Invoice Value": totals["R_Invoice"],
            "Net Qty": totals["N_Qty"], "Net Taxable Value": totals["N_Taxable"],
            "Net Tax Amount": totals["N_Tax"], "Net Invoice Value": totals["N_Invoice"],
        })
        export_df = pd.concat([export_df, pd.DataFrame([gt_row])], ignore_index=True)

        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="meesho_net_sales_summary.csv",
            mime="text/csv",
        )

    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Sales Data** (raw)")
            st.dataframe(clean(sales_df)[REQUIRED_COLS], use_container_width=True, hide_index=True)
        with col_b:
            st.markdown("**Sales Return Data** (raw)")
            st.dataframe(clean(ret_df)[REQUIRED_COLS], use_container_width=True, hide_index=True)

else:
    st.info("Please upload both Excel files above to generate the report.")
    st.markdown("""
    **Expected columns in both files:**
    | Column | Description |
    |--------|-------------|
    | `end_customer_state_new` | State name |
    | `quantity` | Number of units |
    | `gst_rate` | GST rate (e.g. 5, 12, 18) |
    | `total_taxable_sale_value` | Taxable value |
    | `tax_amount` | Tax amount |
    | `total_invoice_value` | Invoice value |
    """)
