"""
app.py — Streamlit UI for Inventory Optimization using QAOA
============================================================
Clean white minimal interface.

Architecture:
  app.py (UI) → quantum_solver.py (QAOA) → utils.py (QUBO)
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import sys
import os

# Make imports from same directory work
sys.path.insert(0, os.path.dirname(__file__))

from utils import (
    build_qubo_matrix, decode_binary_solution, compute_profit,
    check_constraints, classical_solve
)

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG — white minimal theme
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Inventory Optimization · QAOA",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
  /* Import clean sans-serif */
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  /* ====== FORCE WHITE MODE (override dark mode) ====== */
  html, body, [class*="css"],
  .stApp, .main, .block-container,
  [data-testid="stAppViewContainer"],
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  section[data-testid="stSidebar"],
  section[data-testid="stSidebar"] > div,
  [data-testid="stAppViewBlockContainer"],
  [data-testid="stVerticalBlock"],
  [data-testid="stHorizontalBlock"],
  [data-testid="column"],
  [data-testid="stExpander"],
  [data-testid="stExpanderDetails"],
  [data-testid="stMarkdownContainer"],
  [data-testid="stDataFrame"],
  [data-testid="stTable"],
  .stTabs, .stTabs [role="tabpanel"],
  .stSelectbox, .stNumberInput, .stTextInput, .stSlider,
  [data-baseweb="select"], [data-baseweb="input"],
  [data-baseweb="popover"], [data-baseweb="menu"],
  .stAlert, .stSpinner {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    font-family: 'DM Sans', sans-serif;
  }

  /* Force all text to dark */
  .stApp p, .stApp span, .stApp label, .stApp div,
  .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
  .stApp li, .stApp td, .stApp th, .stApp code,
  [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] span,
  [data-testid="stWidgetLabel"] p,
  [data-testid="stWidgetLabel"] label {
    color: #1a1a1a !important;
  }

  /* Fix input fields */
  input, textarea, select,
  [data-baseweb="input"] input,
  [data-baseweb="select"] div,
  .stSelectbox div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border-color: #e0e0e0 !important;
  }

  /* Fix dropdown menus */
  [data-baseweb="popover"] > div,
  [data-baseweb="menu"],
  [role="listbox"],
  [role="option"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
  }
  [role="option"]:hover {
    background-color: #f0f0f0 !important;
  }

  /* Fix dataframes */
  .stDataFrame, .stDataFrame iframe,
  [data-testid="stDataFrame"] > div {
    background-color: #ffffff !important;
  }

  /* Fix expanders */
  [data-testid="stExpander"] summary,
  [data-testid="stExpander"] details {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border-color: #e8e8e8 !important;
  }

  /* Remove Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }

  /* Sidebar */
  [data-testid="stSidebar"],
  [data-testid="stSidebar"] > div:first-child {
    background: #ffffff !important;
    border-right: 1px solid #e8e8e8 !important;
  }

  /* Horizontal rules / dividers */
  hr, [data-testid="stSidebar"] hr {
    border-color: #e8e8e8 !important;
    background-color: #e8e8e8 !important;
  }

  /* Cards */
  .card {
    background: #ffffff !important;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 16px;
  }
  .card-accent {
    background: #ffffff !important;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 16px;
  }

  /* Section headers */
  .section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #888 !important;
    margin-bottom: 12px;
  }

  /* Metric chips */
  .metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
  .metric-chip {
    background: #ffffff !important;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    padding: 10px 16px;
    text-align: center;
    min-width: 90px;
  }
  .metric-chip .val {
    font-size: 22px;
    font-weight: 600;
    color: #1a1a1a !important;
    font-family: 'DM Mono', monospace;
  }
  .metric-chip .lbl {
    font-size: 11px;
    color: #888 !important;
    margin-top: 2px;
  }

  /* Bitstring display */
  .bitstring {
    font-family: 'DM Mono', monospace;
    font-size: 15px;
    letter-spacing: 0.15em;
    background: #ffffff !important;
    border: 1px solid #e8e8e8;
    padding: 8px 14px;
    border-radius: 5px;
    display: inline-block;
    color: #333 !important;
  }

  /* Violation badge */
  .violation {
    background: #ffffff !important;
    border: 1px solid #ffd0d0;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    color: #c00 !important;
    margin: 3px 0;
    display: block;
  }
  .ok-badge {
    background: #ffffff !important;
    border: 1px solid #b8e8c8;
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    color: #1a7a40 !important;
    display: inline-block;
  }

  /* Formula block */
  .formula {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    background: #ffffff !important;
    border-left: 3px solid #d0d0d0;
    padding: 10px 14px;
    border-radius: 0 5px 5px 0;
    color: #444 !important;
    white-space: pre;
    line-height: 1.7;
  }

  /* Tabs */
  .stTabs [role="tablist"] {
    border-bottom: 1px solid #e8e8e8 !important;
    gap: 0;
  }
  .stTabs [role="tab"] {
    font-size: 13px;
    font-weight: 500;
    color: #888 !important;
    padding: 8px 18px;
    border-bottom: 2px solid transparent;
    background-color: #ffffff !important;
  }
  .stTabs [aria-selected="true"] {
    color: #1a1a1a !important;
    border-bottom: 2px solid #1a1a1a !important;
  }

  /* Button */
  .stButton > button {
    background: #1a1a1a !important;
    color: #fff !important;
    border: none;
    border-radius: 6px;
    padding: 10px 28px;
    font-size: 14px;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.02em;
    cursor: pointer;
    width: 100%;
    transition: background 0.15s;
  }
  .stButton > button:hover { background: #333 !important; }

  /* Number inputs */
  .stNumberInput input, .stTextInput input {
    border: 1px solid #e0e0e0 !important;
    border-radius: 5px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    background-color: #ffffff !important;
    color: #1a1a1a !important;
  }

  /* Number input buttons */
  .stNumberInput button {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
    border-color: #e0e0e0 !important;
  }

  /* Streamlit slider */
  .stSlider { padding-top: 4px; }

  /* Tooltip / popover */
  [data-baseweb="tooltip"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
  }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<div style="padding: 32px 0 20px 0; border-bottom: 1px solid #ebebeb; margin-bottom: 28px;">
  <div style="font-size:11px; letter-spacing:0.14em; text-transform:uppercase;
              color:#999; font-weight:600; margin-bottom:6px;">
    ⚛ Quantum Optimization
  </div>
  <h1 style="font-size:28px; font-weight:600; margin:0; color:#1a1a1a; letter-spacing:-0.02em;">
    Inventory Optimization using QAOA
  </h1>
  <p style="margin:8px 0 0 0; color:#666; font-size:14px; line-height:1.5;">
    MILP → QUBO → Ising Hamiltonian → QAOA (Qiskit + Aer Simulator)
  </p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR — Inputs
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<p class="section-title">Problem Setup</p>', unsafe_allow_html=True)

    num_products = st.selectbox("Number of Products (N)", [2, 3], index=0,
                                help="Keep small for simulator efficiency")
    num_materials = st.selectbox("Number of Raw Materials (M)", [1, 2], index=0)
    num_bits = st.selectbox("Bits per variable (K)", [2, 3], index=0,
                             help="xi = Σ 2^k·bik, max xi = 2^K - 1")

    st.markdown("---")
    st.markdown('<p class="section-title">Product Parameters</p>', unsafe_allow_html=True)

    demands, prices, inventories = [], [], []
    for i in range(num_products):
        st.markdown(f"**Product {i+1}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            d = st.number_input(f"d{i+1}", min_value=1, max_value=2**(num_bits)-1,
                                value=min(3, 2**num_bits-1), key=f"d{i}")
        with c2:
            p = st.number_input(f"p{i+1}", min_value=1, max_value=50,
                                value=[10, 15, 12][i % 3], key=f"p{i}")
        with c3:
            s = st.number_input(f"s{i+1}", min_value=0, max_value=5,
                                value=[1, 0, 1][i % 3], key=f"s{i}")
        demands.append(int(d)); prices.append(int(p)); inventories.append(int(s))

    st.markdown("---")
    st.markdown('<p class="section-title">Raw Material Parameters</p>', unsafe_allow_html=True)

    raw_avail, raw_costs = [], []
    for j in range(num_materials):
        st.markdown(f"**Material {j+1}**")
        c1, c2 = st.columns(2)
        with c1:
            y = st.number_input(f"y{j+1} (avail)", min_value=1, max_value=30,
                                value=[10, 8][j % 2], key=f"y{j}")
        with c2:
            c = st.number_input(f"c{j+1} (cost)", min_value=1, max_value=20,
                                value=[3, 2][j % 2], key=f"c{j}")
        raw_avail.append(int(y)); raw_costs.append(int(c))

    st.markdown("---")
    st.markdown('<p class="section-title">A matrix (raw mat. per unit)</p>', unsafe_allow_html=True)
    A_matrix = []
    for i in range(num_products):
        row = []
        cols = st.columns(num_materials)
        for j in range(num_materials):
            with cols[j]:
                default_A = [[2, 1], [1, 3], [2, 1]]
                val = st.number_input(f"A[{i+1},{j+1}]", min_value=0, max_value=10,
                                      value=default_A[i % 3][j % 2], key=f"A{i}{j}")
                row.append(int(val))
        A_matrix.append(row)

    st.markdown("---")
    st.markdown('<p class="section-title">Penalty Weights (λ)</p>', unsafe_allow_html=True)
    lambda1 = st.slider("λ₁ Raw Material", 1.0, 20.0, 5.0, 0.5,
                        help="H_RM penalty weight")
    lambda2 = st.slider("λ₂ Demand", 1.0, 20.0, 5.0, 0.5,
                        help="H_D penalty weight")
    lambda3 = st.slider("λ₃ Inventory", 1.0, 20.0, 3.0, 0.5,
                        help="H_inv penalty weight")

    st.markdown("---")
    st.markdown('<p class="section-title">QAOA Settings</p>', unsafe_allow_html=True)
    qaoa_reps = st.selectbox("QAOA Layers (p)", [1, 2], index=0,
                              help="More layers = better but slower")

    st.markdown("---")
    run_btn = st.button("⚛  Run Optimization")


# ═══════════════════════════════════════════════════════════════════
# FORMULA DISPLAY (always visible)
# ═══════════════════════════════════════════════════════════════════
with st.expander("📐 Mathematical Formulation (from your notes)", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Binary Encoding** (Page 2)")
        st.markdown('<div class="formula">xi = Σ(k=0..K) 2^k · b_ik\nb_ik ∈ {0, 1}</div>',
                    unsafe_allow_html=True)
        st.markdown("**Objective** (Page 2)")
        st.markdown('<div class="formula">Z = Σ_i pi·xi  (Revenue)\nCost = Σ_j cj·(Σ_i Aij·xi)</div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown("**Penalty Hamiltonians** (Page 3)")
        st.markdown('''<div class="formula">H_RM  = Σ_j(Σ_i Aij·xi - yj)²
H_D   = Σ_i(xi - di)²
H_inv = Σ_i(xi + si - di)²

H = -Z + λ₁·H_RM + λ₂·H_D + λ₃·H_inv</div>''',
                    unsafe_allow_html=True)

st.markdown("")


# ═══════════════════════════════════════════════════════════════════
# PROBLEM SUMMARY (always visible)
# ═══════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">Current Problem Instance</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a:
    df_products = pd.DataFrame({
        "Product": [f"P{i+1}" for i in range(num_products)],
        "Demand d": demands,
        "Price p": prices,
        "Inventory s": inventories,
    })
    st.dataframe(df_products, hide_index=True, use_container_width=True)

with col_b:
    df_rm = pd.DataFrame({
        "Material": [f"M{j+1}" for j in range(num_materials)],
        "Available y": raw_avail,
        "Cost c": raw_costs,
    })
    st.dataframe(df_rm, hide_index=True, use_container_width=True)

with col_c:
    df_A = pd.DataFrame(
        A_matrix,
        index=[f"P{i+1}" for i in range(num_products)],
        columns=[f"M{j+1}" for j in range(num_materials)]
    )
    st.markdown("**A matrix** (Aij = units of M_j per P_i)")
    st.dataframe(df_A, use_container_width=True)

qubits_needed = num_products * num_bits
st.markdown(f"""
<div class="card" style="margin-top:8px;">
  <span style="font-size:13px; color:#555;">
  ⚛ <b>{qubits_needed} qubits</b> required &nbsp;|&nbsp;
  {num_products} products × {num_bits} bits/var &nbsp;|&nbsp;
  Max producible per product: <b>{2**num_bits - 1}</b> units
  </span>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# RUN OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════
if run_btn:
    # ── Build QUBO ────────────────────────────────────────────────
    with st.spinner("Building QUBO matrix..."):
        Q_dict, var_names = build_qubo_matrix(
            num_products, num_bits, demands, prices, inventories,
            raw_avail, A_matrix, raw_costs,
            lambda1, lambda2, lambda3
        )

    st.markdown(f"""
    <div class="card-accent" style="margin-top:8px; margin-bottom:16px;">
      ✓ QUBO built — <b>{len(Q_dict)}</b> non-zero terms across
      <b>{qubits_needed}</b> binary variables
    </div>
    """, unsafe_allow_html=True)

    # ── Classical Brute Force ──────────────────────────────────────
    with st.spinner("Running classical brute-force solver..."):
        x_classical, profit_classical, n_feasible = classical_solve(
            demands, prices, inventories, raw_avail, A_matrix, raw_costs
        )
        if x_classical:
            rev_c, cost_c, _ = compute_profit(
                x_classical, demands, prices, inventories, raw_avail, A_matrix, raw_costs
            )
            viol_c = check_constraints(x_classical, demands, inventories, raw_avail, A_matrix)
        else:
            rev_c = cost_c = profit_classical = 0
            viol_c = {"No feasible solution": "—"}

    # ── Quantum QAOA ──────────────────────────────────────────────
    st.markdown("---")

    qaoa_available = True
    try:
        import qiskit_optimization
        import qiskit_algorithms
        import qiskit_aer
    except ImportError:
        qaoa_available = False

    if qaoa_available:
        with st.spinner(f"Running QAOA (p={qaoa_reps}, {qubits_needed} qubits) on Aer simulator..."):
            from quantum_solver import solve_with_qaoa
            result = solve_with_qaoa(
                Q_dict, var_names, num_products, num_bits,
                demands, prices, inventories, raw_avail, A_matrix, raw_costs,
                reps=qaoa_reps
            )
    else:
        result = {"success": False, "error": "Qiskit packages not installed. Showing classical results only."}
        st.warning("⚠ Qiskit not found. Install with: `pip install qiskit qiskit-optimization qiskit-aer qiskit-algorithms`")

    # ═══════════════════════════════════════════════════════════════
    # RESULTS TABS
    # ═══════════════════════════════════════════════════════════════
    tab1, tab2, tab3, tab4 = st.tabs([
        "  Results  ", "  Visualizations  ", "  QAOA Circuit  ", "  QUBO Details  "
    ])

    # ── TAB 1: Results ────────────────────────────────────────────
    with tab1:
        col_q, col_c2 = st.columns(2)

        # ── QAOA Result ──
        with col_q:
            st.markdown('<p class="section-title">⚛ Quantum (QAOA)</p>', unsafe_allow_html=True)
            if result.get("success"):
                qr = result["qaoa"]
                st.markdown(f"""
                <div class="card">
                  <div class="metric-row">
                    {"".join(f'<div class="metric-chip"><div class="val">{xi}</div><div class="lbl">x{i+1} (P{i+1})</div></div>' for i, xi in enumerate(qr["x_values"]))}
                  </div>
                  <div style="margin-top:16px; font-size:13px; color:#555;">
                    <b>Revenue:</b> {qr['revenue']:.1f} &nbsp;|&nbsp;
                    <b>Cost:</b> {qr['cost']:.1f} &nbsp;|&nbsp;
                    <b>Profit:</b> <span style="color:{'#1a7a40' if qr['profit']>=0 else '#c00'};
                    font-weight:600;">{qr['profit']:.1f}</span>
                  </div>
                  <div style="margin-top:12px; font-size:12px; color:#888;">
                    Bitstring: <span class="bitstring">{qr['bitstring_str']}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Constraints**")
                if not qr["violations"]:
                    st.markdown('<span class="ok-badge">✓ All satisfied</span>',
                                unsafe_allow_html=True)
                else:
                    for k, v in qr["violations"].items():
                        st.markdown(f'<span class="violation">✗ {k}: {v}</span>',
                                    unsafe_allow_html=True)

                # Exact quantum (NumPy) result
                st.markdown('<p class="section-title" style="margin-top:20px;">Exact Quantum (NumPy eigensolver)</p>',
                            unsafe_allow_html=True)
                nr = result["classical_quantum"]
                st.markdown(f"""
                <div class="card">
                  <div class="metric-row">
                    {"".join(f'<div class="metric-chip"><div class="val">{xi}</div><div class="lbl">x{i+1}</div></div>' for i, xi in enumerate(nr["x_values"]))}
                  </div>
                  <div style="margin-top:12px; font-size:13px; color:#555;">
                    Profit: <b>{nr['profit']:.1f}</b>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(result.get("error", "QAOA failed"))

        # ── Classical Result ──
        with col_c2:
            st.markdown('<p class="section-title">🖥 Classical (Brute Force)</p>', unsafe_allow_html=True)
            if x_classical:
                st.markdown(f"""
                <div class="card">
                  <div class="metric-row">
                    {"".join(f'<div class="metric-chip"><div class="val">{xi}</div><div class="lbl">x{i+1} (P{i+1})</div></div>' for i, xi in enumerate(x_classical))}
                  </div>
                  <div style="margin-top:16px; font-size:13px; color:#555;">
                    <b>Revenue:</b> {rev_c:.1f} &nbsp;|&nbsp;
                    <b>Cost:</b> {cost_c:.1f} &nbsp;|&nbsp;
                    <b>Profit:</b> <span style="color:{'#1a7a40' if profit_classical>=0 else '#c00'};
                    font-weight:600;">{profit_classical:.1f}</span>
                  </div>
                  <div style="margin-top:8px; font-size:12px; color:#888;">
                    Feasible solutions explored: {n_feasible}
                  </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("**Constraints**")
                if not viol_c:
                    st.markdown('<span class="ok-badge">✓ All satisfied</span>', unsafe_allow_html=True)
                else:
                    for k, v in viol_c.items():
                        st.markdown(f'<span class="violation">✗ {k}: {v}</span>', unsafe_allow_html=True)
            else:
                st.warning("No feasible solution found.")

        # ── Comparison ──
        if result.get("success") and x_classical:
            st.markdown("---")
            st.markdown('<p class="section-title">Classical vs Quantum Comparison</p>', unsafe_allow_html=True)
            qr = result["qaoa"]
            nr = result["classical_quantum"]

            df_compare = pd.DataFrame({
                "Method": ["Classical (Brute Force)", "Exact Quantum (NumPy)", "QAOA"],
                "Production Plan": [
                    str(x_classical), str(nr["x_values"]), str(qr["x_values"])
                ],
                "Revenue": [rev_c, nr["revenue"], qr["revenue"]],
                "Cost": [cost_c, nr["cost"], qr["cost"]],
                "Profit": [profit_classical, nr["profit"], qr["profit"]],
                "Violations": [
                    len(viol_c), len(nr["violations"]), len(qr["violations"])
                ]
            })
            st.dataframe(df_compare, hide_index=True, use_container_width=True)

    # ── TAB 2: Visualizations ─────────────────────────────────────
    with tab2:
        if result.get("success") and x_classical:
            qr = result["qaoa"]
            nr = result["classical_quantum"]

            fig = plt.figure(figsize=(14, 8))
            fig.patch.set_facecolor('white')
            gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)

            product_labels = [f"P{i+1}" for i in range(num_products)]
            x_pos = np.arange(num_products)
            bar_w = 0.22

            GREY1 = "#d0d0d0"
            GREY2 = "#a0a0a0"
            DARK  = "#2a2a2a"
            BLUE  = "#3a6bdf"
            LIGHT = "#e8eefc"

            # ── Plot 1: Demand vs Production ──
            ax1 = fig.add_subplot(gs[0, :2])
            ax1.bar(x_pos - bar_w, demands,      bar_w, label="Demand d",    color=GREY1, zorder=3)
            ax1.bar(x_pos,         x_classical,  bar_w, label="Classical",   color=GREY2, zorder=3)
            ax1.bar(x_pos + bar_w, qr["x_values"], bar_w, label="QAOA",      color=DARK,  zorder=3)
            ax1.set_xticks(x_pos); ax1.set_xticklabels(product_labels)
            ax1.set_title("Demand vs Production", fontsize=12, fontweight='500', pad=10)
            ax1.set_ylabel("Units")
            ax1.legend(fontsize=9, framealpha=0.5)
            ax1.set_facecolor('white')
            ax1.grid(axis='y', color='#f0f0f0', linewidth=1, zorder=0)
            ax1.spines[['top','right']].set_visible(False)

            # ── Plot 2: Profit Comparison ──
            ax2 = fig.add_subplot(gs[0, 2])
            methods = ["Classical", "Exact\nQuantum", "QAOA"]
            profits = [profit_classical, nr["profit"], qr["profit"]]
            colors  = [GREY2, GREY1, DARK]
            bars = ax2.bar(methods, profits, color=colors, zorder=3)
            for bar, val in zip(bars, profits):
                ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                         f"{val:.0f}", ha='center', va='bottom', fontsize=9)
            ax2.set_title("Profit Comparison", fontsize=12, fontweight='500', pad=10)
            ax2.set_ylabel("Profit")
            ax2.set_facecolor('white')
            ax2.grid(axis='y', color='#f0f0f0', linewidth=1, zorder=0)
            ax2.spines[['top','right']].set_visible(False)

            # ── Plot 3: Revenue / Cost breakdown ──
            ax3 = fig.add_subplot(gs[1, :2])
            cat_labels = ["Revenue", "Raw Mat. Cost", "Profit"]
            for idx, (x_vals, label, color) in enumerate([
                (x_classical,    "Classical", GREY2),
                (qr["x_values"], "QAOA",      DARK)
            ]):
                rev, cost, prof = compute_profit(
                    x_vals, demands, prices, inventories, raw_avail, A_matrix, raw_costs
                )
                vals = [rev, cost, prof]
                ax3.bar(np.arange(3) + idx * 0.35, vals, 0.33,
                        label=label, color=color, zorder=3)
            ax3.set_xticks(np.arange(3) + 0.17)
            ax3.set_xticklabels(cat_labels)
            ax3.set_title("Cost Breakdown", fontsize=12, fontweight='500', pad=10)
            ax3.legend(fontsize=9, framealpha=0.5)
            ax3.set_facecolor('white')
            ax3.grid(axis='y', color='#f0f0f0', linewidth=1, zorder=0)
            ax3.spines[['top','right']].set_visible(False)

            # ── Plot 4: Inventory status ──
            ax4 = fig.add_subplot(gs[1, 2])
            avail = [inventories[i] + qr["x_values"][i] for i in range(num_products)]
            ax4.bar(x_pos - 0.18, demands, 0.35, label="Demand", color=GREY1, zorder=3)
            ax4.bar(x_pos + 0.18, avail,   0.35, label="Supply (x+s)", color=DARK, zorder=3)
            ax4.set_xticks(x_pos); ax4.set_xticklabels(product_labels)
            ax4.set_title("Supply vs Demand (QAOA)", fontsize=12, fontweight='500', pad=10)
            ax4.legend(fontsize=9, framealpha=0.5)
            ax4.set_facecolor('white')
            ax4.grid(axis='y', color='#f0f0f0', linewidth=1, zorder=0)
            ax4.spines[['top','right']].set_visible(False)

            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        else:
            st.info("Run the optimization to see visualizations.")

    # ── TAB 3: QAOA Circuit ───────────────────────────────────────
    with tab3:
        st.markdown('<p class="section-title">QAOA Circuit Architecture</p>',
                    unsafe_allow_html=True)

        # Circuit diagram (text-based, always works)
        n_q = qubits_needed
        p   = qaoa_reps

        st.markdown(f"""
        <div class="card">
          <div style="font-size:13px; color:#444; margin-bottom:12px;">
            <b>{n_q} qubits</b> · <b>p={p}</b> QAOA layers ·
            <b>{2*p}</b> variational parameters (γ₁..γₚ, β₁..βₚ)
          </div>
          <div class="formula">Step 0 — Initial State
  |+⟩^⊗{n_q}  :  H gates on all {n_q} qubits

{"".join(f"""
Step {r+1} — QAOA Layer {r+1}
  Problem Unitary U(C, γ_{r+1}):
    ZZ(γ_{r+1}) rotations for each QUBO term (i,j)
    Rz(2·Q_ii·γ_{r+1}) single-qubit rotations (diagonal)
  Mixer Unitary U(B, β_{r+1}):
    Rx(2·β_{r+1}) on all {n_q} qubits
""" for r in range(p))}
Step Final — Measurement
  Measure all {n_q} qubits → bitstring b₀b₁...b_{n_q-1}
  Decode: xi = Σ_k 2^k · b_ik</div>
        </div>
        """, unsafe_allow_html=True)

        # Try to draw Qiskit circuit
        if result.get("success"):
            try:
                circuit = result.get("circuit")
                if circuit is not None:
                    fig_circ, ax_circ = plt.subplots(figsize=(max(8, n_q*1.2), max(4, n_q*0.8)))
                    fig_circ.patch.set_facecolor('white')
                    circuit.draw(output="mpl", ax=ax_circ, style={"backgroundcolor": "#ffffff"})
                    st.pyplot(fig_circ, use_container_width=True)
                    plt.close(fig_circ)
            except Exception as e:
                st.info(f"Circuit diagram: use qiskit's circuit.draw() locally. ({e})")

        # Parameter explanation
        st.markdown("""
        <div class="card-accent" style="margin-top:12px;">
          <div style="font-size:13px; color:#444; line-height:1.8;">
            <b>Variational Parameters:</b><br>
            &nbsp;&nbsp;γ (gamma) — controls time evolution under problem Hamiltonian C<br>
            &nbsp;&nbsp;β (beta)  — controls time evolution under mixer Hamiltonian B = Σ Xᵢ<br><br>
            <b>Optimizer:</b> COBYLA (gradient-free, good for noisy circuits)<br>
            <b>Backend:</b> Qiskit Aer Sampler (noiseless simulation)
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 4: QUBO Details ───────────────────────────────────────
    with tab4:
        st.markdown('<p class="section-title">QUBO Matrix Details</p>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
          <div style="font-size:13px; color:#555; line-height:2;">
            <b>Variables:</b> {len(var_names)}<br>
            <b>Non-zero QUBO terms:</b> {len(Q_dict)}<br>
            <b>Variable names:</b>
            <span class="bitstring">{', '.join(var_names)}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Show top terms
        st.markdown("**Largest magnitude QUBO terms:**")
        sorted_Q = sorted(Q_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:20]
        df_qubo = pd.DataFrame([
            {"Variable i": k[0], "Variable j": k[1], "Coefficient": round(v, 4)}
            for (k, v) in sorted_Q
        ])
        st.dataframe(df_qubo, hide_index=True, use_container_width=True)

        st.markdown("""
        <div class="card-accent" style="margin-top:12px;">
          <div style="font-size:12px; color:#555; line-height:1.8;">
            <b>Diagonal terms</b> (i=j): linear contributions (revenue + penalty linear parts)<br>
            <b>Off-diagonal terms</b> (i≠j): quadratic couplings from penalty expansions<br><br>
            QUBO objective: <code>min x^T Q x</code> where x is the binary vector<br>
            This maps directly to Ising: <code>H = Σ Jᵢⱼ·ZᵢZⱼ + Σ hᵢ·Zᵢ</code>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# DEFAULT STATE (before button click)
# ═══════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div class="card" style="text-align:center; padding:48px 24px; color:#888;">
      <div style="font-size:40px; margin-bottom:12px;">⚛</div>
      <div style="font-size:15px; font-weight:500; color:#555; margin-bottom:6px;">
        Configure parameters in the sidebar
      </div>
      <div style="font-size:13px;">
        Then click <b>Run Optimization</b> to solve with QAOA + Classical comparison
      </div>
    </div>
    """, unsafe_allow_html=True)