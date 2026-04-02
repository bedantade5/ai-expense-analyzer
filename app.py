import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Finely · Expense Analyzer",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

dark = st.session_state.dark_mode

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap');

:root {{
  --bg:          {'#0b0d11' if dark else '#f5f4ef'};
  --bg2:         {'#111318' if dark else '#eeece5'};
  --surface:     {'#181c24' if dark else '#ffffff'};
  --surface2:    {'#1f2430' if dark else '#f9f8f4'};
  --border:      {'rgba(255,255,255,0.07)' if dark else 'rgba(0,0,0,0.08)'};
  --ink:         {'#eceef2' if dark else '#111218'};
  --ink2:        {'#8b92a5' if dark else '#5a5e6e'};
  --ink3:        {'#4a5168' if dark else '#9ea3b2'};
  --accent:      #c8f23a;
  --accent-dim:  {'rgba(200,242,58,0.12)' if dark else 'rgba(200,242,58,0.18)'};
  --accent-text: {'#b4da2a' if dark else '#6b8500'};
  --red:         #ff5f6b;
  --red-dim:     {'rgba(255,95,107,0.12)' if dark else 'rgba(255,95,107,0.1)'};
  --amber:       #f7b955;
  --amber-dim:   {'rgba(247,185,85,0.12)' if dark else 'rgba(247,185,85,0.1)'};
  --blue:        #5b9cf6;
  --blue-dim:    {'rgba(91,156,246,0.12)' if dark else 'rgba(91,156,246,0.1)'};
  --r:           12px;
  --mono:        'DM Mono', monospace;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [class*="css"], .stApp {{
  font-family: 'Syne', sans-serif !important;
  background: var(--bg) !important;
  color: var(--ink) !important;
}}

#MainMenu, footer, header {{ visibility: hidden; }}

.block-container {{
  padding: 2.5rem 3rem 5rem 3rem !important;
  max-width: 1380px;
}}

/* ── Header ── */
.finely-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}}
.finely-wordmark {{
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 2rem;
  letter-spacing: -0.02em;
  color: var(--ink);
  line-height: 1;
}}
.finely-wordmark em {{
  color: var(--accent);
  font-style: normal;
}}
.finely-tagline {{
  font-size: 0.72rem;
  color: var(--ink3);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-top: 0.25rem;
  font-family: var(--mono);
}}
.header-right {{
  display: flex;
  align-items: center;
  gap: 1.25rem;
}}
.api-pill {{
  font-family: var(--mono);
  font-size: 0.7rem;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  color: var(--ink2);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--surface2);
}}
.dot {{
  width: 6px; height: 6px; border-radius: 50%; display: inline-block;
}}
.dot-on  {{ background: var(--accent); box-shadow: 0 0 6px var(--accent); }}
.dot-off {{ background: var(--red); }}

/* ── Cards ── */
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1.5rem 1.75rem;
  height: 100%;
  transition: border-color 0.2s;
}}
.card:hover {{ border-color: {'rgba(255,255,255,0.14)' if dark else 'rgba(0,0,0,0.14)'}; }}

/* ── KPI ── */
.kpi-label {{
  font-family: var(--mono);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--ink3);
  margin-bottom: 0.6rem;
}}
.kpi-value {{
  font-size: 2rem;
  font-weight: 800;
  color: var(--ink);
  line-height: 1;
  letter-spacing: -0.03em;
}}
.kpi-value-sm {{
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--ink);
  line-height: 1;
  letter-spacing: -0.02em;
}}
.kpi-sub {{
  font-size: 0.75rem;
  color: var(--ink2);
  margin-top: 0.45rem;
  font-family: var(--mono);
}}
.kpi-badge {{
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  margin-top: 0.75rem;
  padding: 0.22rem 0.6rem;
  border-radius: 6px;
  font-size: 0.67rem;
  font-family: var(--mono);
  font-weight: 500;
  letter-spacing: 0.04em;
}}
.badge-green {{ background: var(--accent-dim); color: var(--accent-text); }}
.badge-red   {{ background: var(--red-dim);    color: var(--red); }}
.badge-amber {{ background: var(--amber-dim);  color: var(--amber); }}
.badge-blue  {{ background: var(--blue-dim);   color: var(--blue); }}

.kpi-accent-line {{
  height: 2px;
  border-radius: 2px;
  margin-bottom: 1.1rem;
}}
.line-green {{ background: var(--accent); }}
.line-red   {{ background: var(--red); }}
.line-amber {{ background: var(--amber); }}
.line-blue  {{ background: var(--blue); }}

/* ── Section labels ── */
.section-label {{
  font-family: var(--mono);
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--ink3);
  margin-bottom: 0.35rem;
}}
.section-title {{
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 0.2rem;
  letter-spacing: -0.01em;
}}
.section-sub {{
  font-size: 0.75rem;
  color: var(--ink2);
  margin-bottom: 1.25rem;
  font-family: var(--mono);
}}

/* ── Anomaly rows ── */
.anomaly-row {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 0;
  border-bottom: 1px solid var(--border);
  gap: 1rem;
}}
.anomaly-row:last-child {{ border-bottom: none; }}
.anomaly-merchant {{ font-weight: 700; font-size: 0.88rem; color: var(--ink); }}
.anomaly-date {{ font-size: 0.7rem; color: var(--ink3); margin-top: 0.15rem; font-family: var(--mono); }}
.anomaly-cat {{
  font-size: 0.65rem;
  color: var(--ink2);
  background: var(--surface2);
  border: 1px solid var(--border);
  padding: 0.15rem 0.45rem;
  border-radius: 5px;
  margin-left: 0.5rem;
  font-family: var(--mono);
}}
.anomaly-amount {{
  font-weight: 700;
  font-size: 0.88rem;
  color: var(--red);
  background: var(--red-dim);
  padding: 0.28rem 0.75rem;
  border-radius: 8px;
  white-space: nowrap;
  font-family: var(--mono);
  flex-shrink: 0;
}}

/* ── Insight cards ── */
.insight-card {{
  background: var(--surface2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 8px;
  padding: 1rem 1.15rem;
  margin-bottom: 0.65rem;
}}
.insight-icon {{
  font-size: 1rem;
  margin-bottom: 0.3rem;
  display: block;
}}
.insight-title {{
  font-family: var(--mono);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--accent-text);
  margin-bottom: 0.3rem;
}}
.insight-text {{
  font-size: 0.83rem;
  color: var(--ink2);
  line-height: 1.6;
}}
.insight-text b {{ color: var(--ink); font-weight: 700; }}

/* ── Empty / guard states ── */
.guard-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  text-align: center;
  padding: 4.5rem 2rem;
  margin-top: 1rem;
}}
.guard-icon {{ font-size: 2.5rem; margin-bottom: 1rem; }}
.guard-title {{ font-size: 1.1rem; font-weight: 700; color: var(--ink); margin-bottom: 0.45rem; }}
.guard-sub   {{ font-size: 0.83rem; color: var(--ink2); margin-bottom: 1.25rem; }}
.code-pill {{
  display: inline-block;
  font-family: var(--mono);
  font-size: 0.82rem;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--accent);
  padding: 0.4rem 1.1rem;
  border-radius: 8px;
}}

/* ── Ledger count ── */
.ledger-count {{
  font-family: var(--mono);
  font-size: 0.68rem;
  color: var(--ink3);
  text-align: right;
  margin-top: 0.6rem;
  letter-spacing: 0.04em;
}}

/* ── Buttons ── */
.stButton > button {{
  background: var(--accent) !important;
  color: #111 !important;
  border: none !important;
  border-radius: 9px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.82rem !important;
  padding: 0.55rem 1.25rem !important;
  transition: opacity 0.15s, transform 0.1s !important;
  width: 100%;
  letter-spacing: 0.01em;
}}
.stButton > button:hover {{
  opacity: 0.88 !important;
  transform: translateY(-1px) !important;
}}

/* secondary buttons */
.stButton > button[kind="secondary"] {{
  background: var(--surface2) !important;
  color: var(--ink) !important;
  border: 1px solid var(--border) !important;
}}

/* ── Inputs & selects ── */
.stSelectbox > div > div,
.stFileUploader > div {{
  background: var(--surface2) !important;
  border-color: var(--border) !important;
  color: var(--ink) !important;
  border-radius: 8px !important;
}}
.stSelectbox label, .stFileUploader label {{
  color: var(--ink3) !important;
  font-family: var(--mono) !important;
  font-size: 0.68rem !important;
  text-transform: uppercase;
  letter-spacing: 0.09em;
}}

/* ── Expander ── */
[data-testid="stExpander"] {{
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
}}
[data-testid="stExpander"] summary {{
  color: var(--ink) !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
}}

/* ── Dataframe ── */
[data-testid="stDataFrame"] > div {{
  border-radius: 10px !important;
  border: 1px solid var(--border) !important;
  overflow: hidden;
}}

/* ── Footer ── */
.page-footer {{
  text-align: center;
  margin-top: 3.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  font-family: var(--mono);
  font-size: 0.67rem;
  color: var(--ink3);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}

div[data-testid="metric-container"] {{ display: none; }}

@media (max-width: 768px) {{
  .block-container {{ padding: 1.25rem 1rem 3rem 1rem !important; }}
  .finely-wordmark {{ font-size: 1.5rem; }}
  .kpi-value {{ font-size: 1.55rem; }}
  .card {{ padding: 1.1rem 1.2rem; }}
  .anomaly-row {{ flex-wrap: wrap; gap: 0.4rem; }}
}}
</style>
""", unsafe_allow_html=True)

CATEGORY_COLORS = {
    "Food":          "#c8f23a",
    "Travel":        "#5b9cf6",
    "Shopping":      "#f7b955",
    "Bills":         "#c084fc",
    "Healthcare":    "#34d399",
    "Entertainment": "#ff5f6b",
    "Education":     "#38bdf8",
    "Uncategorized": "#4a5168",
}

PLOT_BG    = "rgba(0,0,0,0)"
GRID_CLR   = "rgba(255,255,255,0.06)" if dark else "rgba(0,0,0,0.07)"
TICK_CLR   = "rgba(139,146,165,1)"
FONT_FAMILY = "Syne, sans-serif"

def check_api():
    try:
        return requests.get(f"{API_BASE}/", timeout=3).status_code == 200
    except Exception:
        return False

def fetch_summary():
    try:
        r = requests.get(f"{API_BASE}/summary", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def fetch_transactions():
    try:
        r = requests.get(f"{API_BASE}/data", timeout=10)
        if r.status_code == 200:
            return pd.DataFrame(r.json().get("transactions", []))
    except Exception:
        pass
    return pd.DataFrame()

def upload_csv(file_bytes, filename):
    try:
        r = requests.post(
            f"{API_BASE}/upload",
            files={"file": (filename, file_bytes, "text/csv")},
            params={"replace": "true"},
            timeout=30,
        )
        return r.status_code, r.json()
    except Exception as e:
        return 500, {"detail": str(e)}

def clear_data():
    try:
        return requests.delete(f"{API_BASE}/data", timeout=10).status_code == 200
    except Exception:
        return False

def make_donut(cat_data: dict) -> go.Figure:
    labels = list(cat_data.keys())
    values = list(cat_data.values())
    colors = [CATEGORY_COLORS.get(l, "#4a5168") for l in labels]
    total  = sum(values)

    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(color=PLOT_BG, width=3)),
        textinfo="none", sort=True, direction="clockwise",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} · %{percent}<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>₹{total:,.0f}</b>", x=0.5, y=0.56, showarrow=False,
        font=dict(size=16, family=FONT_FAMILY, color="#eceef2" if dark else "#111218"),
    )
    fig.add_annotation(
        text="total spend", x=0.5, y=0.43, showarrow=False,
        font=dict(size=10, color=TICK_CLR, family="DM Mono, monospace"),
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v", x=1.02, y=0.5,
            font=dict(size=10, family=FONT_FAMILY, color=TICK_CLR),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        margin=dict(t=10, b=10, l=10, r=10), height=290,
        font=dict(family=FONT_FAMILY),
    )
    return fig

def make_trend(monthly_data: dict) -> go.Figure:
    if not monthly_data:
        return go.Figure()
    mon_df = pd.DataFrame(list(monthly_data.items()), columns=["Month", "Amount"])
    mon_df = mon_df.sort_values("Month")
    mon_df["Label"] = pd.to_datetime(mon_df["Month"]).dt.strftime("%b %Y")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mon_df["Label"], y=mon_df["Amount"],
        mode="lines+markers",
        line=dict(color="#c8f23a", width=2, shape="spline"),
        marker=dict(color="#111318" if dark else "#f5f4ef", size=8,
                    line=dict(color="#c8f23a", width=2)),
        fill="tozeroy", fillcolor="rgba(200,242,58,0.06)",
        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        height=290, margin=dict(t=10, b=10, l=10, r=10),
        font=dict(family=FONT_FAMILY),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=10, color=TICK_CLR, family="DM Mono, monospace"),
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID_CLR, zeroline=False,
            tickprefix="₹", tickformat=",.0f",
            tickfont=dict(size=10, color=TICK_CLR, family="DM Mono, monospace"),
        ),
        hovermode="x unified",
    )
    return fig

def make_bar(cat_data: dict) -> go.Figure:
    cat_df = pd.DataFrame(list(cat_data.items()), columns=["Category", "Amount"])
    cat_df = cat_df.sort_values("Amount", ascending=True)
    colors = [CATEGORY_COLORS.get(c, "#4a5168") for c in cat_df["Category"]]

    fig = go.Figure(go.Bar(
        x=cat_df["Amount"], y=cat_df["Category"], orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)"),
                    opacity=0.9),
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
        text=[f"₹{v:,.0f}" for v in cat_df["Amount"]],
        textposition="outside",
        textfont=dict(size=10, color=TICK_CLR, family="DM Mono, monospace"),
    ))
    fig.update_layout(
        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
        height=max(220, len(cat_df) * 46),
        margin=dict(t=5, b=5, l=5, r=100),
        font=dict(family=FONT_FAMILY),
        xaxis=dict(
            showgrid=True, gridcolor=GRID_CLR, zeroline=False,
            tickprefix="₹", tickformat=",.0f",
            tickfont=dict(size=10, color=TICK_CLR, family="DM Mono, monospace"),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color=TICK_CLR),
        ),
        bargap=0.42,
    )
    return fig

def generate_insights(df: pd.DataFrame, summary: dict) -> list[dict]:
    insights = []
    if df.empty:
        return insights

    cat_data = summary.get("category_breakdown", {})
    if cat_data:
        top_cat = max(cat_data, key=cat_data.get)
        top_pct = round(cat_data[top_cat] / summary["total_spend"] * 100, 1)
        insights.append({
            "icon": "🔍", "title": "Top Spending Category",
            "text": f"Your biggest spend is on <b>{top_cat}</b>, accounting for "
                    f"<b>{top_pct}%</b> of total expenses (₹{cat_data[top_cat]:,.0f}). "
                    f"Consider reviewing this category for potential savings.",
        })

    monthly = summary.get("monthly_trend", {})
    if len(monthly) >= 2:
        sorted_months = sorted(monthly.keys())
        last, prev = monthly[sorted_months[-1]], monthly[sorted_months[-2]]
        delta = round((last - prev) / prev * 100, 1) if prev else 0
        direction = "increased" if delta > 0 else "decreased"
        emoji = "📈" if delta > 0 else "📉"
        insights.append({
            "icon": emoji, "title": "Month-over-Month Trend",
            "text": f"Spending <b>{direction} by {abs(delta)}%</b> vs last month "
                    f"(₹{prev:,.0f} → ₹{last:,.0f}).",
        })

    anom = summary.get("anomaly_count", 0)
    if anom > 0:
        insights.append({
            "icon": "⚠️", "title": "Anomaly Alert",
            "text": f"AI flagged <b>{anom} unusual transaction{'s' if anom > 1 else ''}</b> "
                    f"that deviate significantly from your normal spending. Review them on the right.",
        })
    else:
        insights.append({
            "icon": "✅", "title": "Spending Looks Normal",
            "text": "No anomalies detected. Your spending patterns are consistent.",
        })

    avg_spend = summary["total_spend"] / summary["transaction_count"]
    insights.append({
        "icon": "💡", "title": "Average Transaction Size",
        "text": f"Your average transaction is <b>₹{avg_spend:,.0f}</b> across "
                f"{summary['transaction_count']} transactions. "
                f"Reviewing small recurring charges can reveal hidden costs.",
    })
    return insights

api_ok  = check_api()
dot_cls = "dot-on" if api_ok else "dot-off"
api_lbl = "API Live" if api_ok else "API Offline"
theme_icon = "☀️" if dark else "🌙"

h_left, h_right = st.columns([3, 1])
with h_left:
    st.markdown(f"""
    <div class="finely-header">
        <div>
            <div class="finely-wordmark">fin<em>·</em>ely</div>
            <div class="finely-tagline">AI-Powered Expense Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with h_right:
    col_api, col_toggle = st.columns([2, 1])
    with col_api:
        st.markdown(f"""
        <div style="margin-top:0.9rem;">
            <div class="api-pill">
                <span class="dot {dot_cls}"></span>{api_lbl}
            </div>
        </div>""", unsafe_allow_html=True)
    with col_toggle:
        st.markdown("<div style='margin-top:0.7rem;'></div>", unsafe_allow_html=True)
        st.button(theme_icon, on_click=toggle_theme, help="Toggle light/dark mode")

with st.expander("📂  Upload Bank Statement CSV", expanded=False):
    uc1, uc2, uc3 = st.columns([3, 1, 1])
    with uc1:
        uploaded_file = st.file_uploader(
            "CSV with columns: Date, Merchant, Amount",
            type=["csv"], label_visibility="collapsed",
        )
    with uc2:
        if uploaded_file and api_ok:
            if st.button("Analyze →", use_container_width=True):
                with st.spinner("Running AI categorization + anomaly detection…"):
                    status, result = upload_csv(uploaded_file.getvalue(), uploaded_file.name)
                if status == 200:
                    st.success(result.get("message", "Done!"))
                    st.rerun()
                else:
                    st.error(result.get("detail", "Upload failed."))
    with uc3:
        if st.button("Clear All", use_container_width=True):
            if clear_data():
                st.rerun()

if not api_ok:
    st.markdown("""
    <div class="guard-card">
        <div class="guard-icon">🔌</div>
        <div class="guard-title">Backend Not Running</div>
        <div class="guard-sub">Start the FastAPI server in your terminal:</div>
        <span class="code-pill">uvicorn api:app --reload</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

summary = fetch_summary()
df      = fetch_transactions()

if summary is None or df.empty:
    st.markdown("""
    <div class="guard-card">
        <div class="guard-icon">📊</div>
        <div class="guard-title">No Transaction Data Yet</div>
        <div class="guard-sub">
            Upload your <code>transactions.csv</code> using the panel above to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

cat_data     = summary.get("category_breakdown", {})
monthly_data = summary.get("monthly_trend", {})
top_cat      = max(cat_data, key=cat_data.get) if cat_data else "—"
top_cat_amt  = cat_data.get(top_cat, 0)
anom_count   = summary.get("anomaly_count", 0)
total_spend  = summary.get("total_spend", 0)
txn_count    = summary.get("transaction_count", 0)
avg_txn      = round(total_spend / txn_count, 0) if txn_count else 0

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    st.markdown(f"""
    <div class="card">
        <div class="kpi-accent-line line-green"></div>
        <div class="kpi-label">Total Spend</div>
        <div class="kpi-value">₹{total_spend:,.0f}</div>
        <div class="kpi-sub">{txn_count} transactions</div>
        <span class="kpi-badge badge-green">All Time</span>
    </div>""", unsafe_allow_html=True)

with k2:
    top_pct = round(top_cat_amt / total_spend * 100, 1) if total_spend else 0
    st.markdown(f"""
    <div class="card">
        <div class="kpi-accent-line line-amber"></div>
        <div class="kpi-label">Top Category</div>
        <div class="kpi-value-sm">{top_cat}</div>
        <div class="kpi-sub">₹{top_cat_amt:,.0f} spent</div>
        <span class="kpi-badge badge-amber">{top_pct}% of total</span>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
        <div class="kpi-accent-line line-blue"></div>
        <div class="kpi-label">Avg Transaction</div>
        <div class="kpi-value">₹{avg_txn:,.0f}</div>
        <div class="kpi-sub">per transaction</div>
        <span class="kpi-badge badge-blue">{len(cat_data)} categories</span>
    </div>""", unsafe_allow_html=True)

with k4:
    a_badge = "badge-red" if anom_count > 0 else "badge-green"
    a_text  = f"{anom_count} flagged" if anom_count > 0 else "All clear"
    st.markdown(f"""
    <div class="card">
        <div class="kpi-accent-line line-red"></div>
        <div class="kpi-label">Anomalies</div>
        <div class="kpi-value">{anom_count}</div>
        <div class="kpi-sub">unusual transactions</div>
        <span class="kpi-badge {a_badge}">{a_text}</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

cl, cr = st.columns(2, gap="large")

with cl:
    st.markdown("""
    <div class="card">
        <div class="section-label">Breakdown</div>
        <div class="section-title">Expenses by Category</div>
        <div class="section-sub">Distribution of your spending</div>
    """, unsafe_allow_html=True)
    if cat_data:
        st.plotly_chart(make_donut(cat_data), use_container_width=True,
                        config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with cr:
    st.markdown("""
    <div class="card">
        <div class="section-label">Trajectory</div>
        <div class="section-title">Monthly Spending Trend</div>
        <div class="section-sub">Your expense trajectory over time</div>
    """, unsafe_allow_html=True)
    if monthly_data:
        st.plotly_chart(make_trend(monthly_data), use_container_width=True,
                        config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

il, ir = st.columns(2, gap="large")

with il:
    st.markdown("""
    <div class="card">
        <div class="section-label">Intelligence</div>
        <div class="section-title">AI Insights</div>
        <div class="section-sub">Patterns detected in your spending behaviour</div>
    """, unsafe_allow_html=True)
    for ins in generate_insights(df, summary):
        st.markdown(f"""
        <div class="insight-card">
            <span class="insight-icon">{ins['icon']}</span>
            <div class="insight-title">{ins['title']}</div>
            <div class="insight-text">{ins['text']}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with ir:
    anomaly_df = (
        df[df["is_anomaly"] == True].sort_values("amount", ascending=False)
        if not df.empty else pd.DataFrame()
    )
    st.markdown(f"""
    <div class="card">
        <div class="section-label">Flagged</div>
        <div class="section-title">Anomalous Transactions</div>
        <div class="section-sub">{len(anomaly_df)} transaction{'s' if len(anomaly_df) != 1 else ''}
        flagged by Isolation Forest</div>
    """, unsafe_allow_html=True)

    if anomaly_df.empty:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 0;">
            <div style="font-size:1.75rem;margin-bottom:0.5rem;">✅</div>
            <div style="font-size:0.83rem;color:var(--ink2);font-family:var(--mono);">
                No anomalies detected.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for _, row in anomaly_df.iterrows():
            st.markdown(f"""
            <div class="anomaly-row">
                <div>
                    <div class="anomaly-merchant">{row['merchant']}</div>
                    <div class="anomaly-date">{row['date']}
                        <span class="anomaly-cat">{row['category']}</span>
                    </div>
                </div>
                <div class="anomaly-amount">₹{row['amount']:,.0f}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="section-label">Ranked</div>
    <div class="section-title">Category Breakdown</div>
    <div class="section-sub">Total spend per category, highest to lowest</div>
""", unsafe_allow_html=True)
if cat_data:
    st.plotly_chart(make_bar(cat_data), use_container_width=True,
                    config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div class="section-label">Ledger</div>
    <div class="section-title">All Transactions</div>
    <div class="section-sub">Full record — filterable & sortable</div>
""", unsafe_allow_html=True)

f1, f2, f3 = st.columns([2, 2, 1], gap="medium")
with f1:
    cats    = ["All"] + sorted(df["category"].unique().tolist())
    sel_cat = st.selectbox("Category", cats)
with f2:
    sel_anom = st.selectbox("Filter", ["All", "Anomalies Only", "Normal Only"])
with f3:
    sel_sort = st.selectbox("Sort", ["Date ↓", "Amount ↓", "Amount ↑"])

display_df = df.copy()
if sel_cat  != "All":
    display_df = display_df[display_df["category"] == sel_cat]
if sel_anom == "Anomalies Only":
    display_df = display_df[display_df["is_anomaly"] == True]
elif sel_anom == "Normal Only":
    display_df = display_df[display_df["is_anomaly"] == False]

sort_map = {"Date ↓": ("date", False), "Amount ↓": ("amount", False), "Amount ↑": ("amount", True)}
sc, sa = sort_map[sel_sort]
display_df = display_df.sort_values(sc, ascending=sa)

display_df["Amount"]  = display_df["amount"].apply(lambda x: f"₹{x:,.2f}")
display_df["Anomaly"] = display_df["is_anomaly"].apply(lambda x: "🚨 Yes" if x else "✅ No")

final_df = display_df[["date", "merchant", "Amount", "category", "Anomaly"]].rename(columns={
    "date": "Date", "merchant": "Merchant", "category": "Category",
})

st.dataframe(final_df, use_container_width=True, hide_index=True, height=420)

st.markdown(f"""
<div class="ledger-count">Showing {len(final_df)} of {len(df)} transactions</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-footer">
    finely &nbsp;·&nbsp; AI Expense Analyzer &nbsp;·&nbsp;
    FastAPI &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; Scikit-learn
    <div style="font-size: 12px; opacity: 0.8; margin-top: 4px;">
        Made by Bedanta De and Shreya Thakre
    </div>
</div>
""", unsafe_allow_html=True)