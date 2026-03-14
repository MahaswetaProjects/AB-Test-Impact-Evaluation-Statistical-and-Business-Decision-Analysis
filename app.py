"""
A/B Test Impact Evaluation — Interactive Dashboard
Checkout Redesign Experiment
Author: Mahasweta Talik
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import (
    proportions_ztest,
    proportion_confint,
    proportion_effectsize,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="A/B Test Dashboard — Checkout Redesign",
    page_icon="🧪",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #4C72B0;
        padding: 16px 20px;
        border-radius: 6px;
        margin: 4px 0;
    }
    .metric-card.green { border-left-color: #28a745; }
    .metric-card.orange { border-left-color: #fd7e14; }
    .metric-card.red { border-left-color: #dc3545; }

    .kpi-value { font-size: 2rem; font-weight: 700; color: #212529; }
    .kpi-label { font-size: 0.85rem; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-delta { font-size: 0.9rem; font-weight: 600; }
    .delta-pos { color: #28a745; }
    .delta-neg { color: #dc3545; }

    .section-header {
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 8px;
        margin: 24px 0 16px;
    }
    .ship-banner {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 20px 28px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 20px 0;
    }
    .noship-banner {
        background: linear-gradient(135deg, #dc3545, #e83e8c);
        color: white;
        padding: 20px 28px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 20px 0;
    }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar Controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/000000/test-tube.png", width=60)
    st.title("Experiment Config")
    st.markdown("---")

    st.subheader("📐 Statistical Parameters")
    baseline   = st.slider("Baseline Conversion Rate",  0.05, 0.20, 0.10, 0.01, format="%.0f%%")
    mde        = st.slider("Min. Detectable Effect (absolute)", 0.01, 0.05, 0.02, 0.005, format="%.1f%%")
    alpha_val  = st.select_slider("Significance Level (α)", [0.01, 0.05, 0.10], value=0.05)
    power_val  = st.select_slider("Statistical Power",       [0.70, 0.80, 0.90], value=0.80)

    st.markdown("---")
    st.subheader("💰 Business Parameters")
    monthly_users  = st.number_input("Monthly Active Users", 100_000, 10_000_000, 1_000_000, 100_000)
    aov            = st.number_input("Avg Order Value (₹)", 100, 5000, 800, 100)

    st.markdown("---")
    st.subheader("🎲 Simulation Seed")
    seed = st.number_input("Random Seed", 0, 9999, 42, 1)

    run = st.button("▶  Run Experiment", use_container_width=True, type="primary")


# ── Run Simulation ────────────────────────────────────────────────────────────
@st.cache_data
def run_experiment(baseline, mde, alpha_val, power_val, monthly_users, aov, seed):
    np.random.seed(seed)
    expected = baseline + mde

    # Sample size
    es   = proportion_effectsize(baseline, expected)
    pa   = NormalIndPower()
    req_n = int(np.ceil(pa.solve_power(effect_size=es, alpha=alpha_val, power=power_val)))

    total = req_n * 2
    groups   = np.random.choice(["A", "B"], size=total)
    devices  = np.random.choice(["mobile","desktop","tablet"], size=total, p=[0.55,0.35,0.10])
    utypes   = np.random.choice(["new","returning"], size=total, p=[0.60,0.40])

    dev_mult = {"mobile": 0.85, "desktop": 1.20, "tablet": 1.00}
    cp = {"A": baseline, "B": expected}
    converted = [
        np.random.binomial(1, min(cp[g] * dev_mult[d], 1))
        for g, d in zip(groups, devices)
    ]

    data = pd.DataFrame({
        "user_id" : range(1, total + 1),
        "group"   : groups,
        "device"  : devices,
        "user_type": utypes,
        "converted": converted,
    })

    success = data.groupby("group")["converted"].sum()
    counts  = data.groupby("group")["converted"].count()
    rates   = data.groupby("group")["converted"].mean()

    z_stat, p_val = proportions_ztest(count=success, nobs=counts)
    ci_a = proportion_confint(success["A"], counts["A"], alpha=alpha_val, method="wilson")
    ci_b = proportion_confint(success["B"], counts["B"], alpha=alpha_val, method="wilson")

    abs_lift = rates["B"] - rates["A"]
    rel_lift = abs_lift / rates["A"]
    monthly_uplift = abs_lift * monthly_users * aov

    # A/A
    ctrl = data[data["group"] == "A"].copy()
    ctrl["aa_grp"] = np.random.choice(["A1","A2"], size=len(ctrl))
    aa_s = ctrl.groupby("aa_grp")["converted"].sum()
    aa_n = ctrl.groupby("aa_grp")["converted"].count()
    _, aa_p = proportions_ztest(aa_s, aa_n)

    return {
        "data"        : data,
        "req_n"       : req_n,
        "success"     : success,
        "counts"      : counts,
        "rates"       : rates,
        "z_stat"      : z_stat,
        "p_val"       : p_val,
        "ci_a"        : ci_a,
        "ci_b"        : ci_b,
        "abs_lift"    : abs_lift,
        "rel_lift"    : rel_lift,
        "monthly_uplift": monthly_uplift,
        "aa_p"        : aa_p,
        "cohen_h"     : proportion_effectsize(rates["B"], rates["A"]),
    }


res = run_experiment(baseline, mde, alpha_val, power_val, monthly_users, aov, seed)

stat_sig  = res["p_val"] < alpha_val
prac_sig  = res["abs_lift"] >= 0.01
aa_pass   = res["aa_p"] > alpha_val
lift_pos  = (res["ci_b"][0] - res["ci_a"][1]) > 0
ship      = stat_sig and prac_sig and aa_pass

COLORS = {"control": "#4C72B0", "treatment": "#DD8452", "green": "#28a745", "red": "#dc3545"}

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧪 A/B Test Dashboard — Checkout Redesign")
st.markdown("*Statistical & Business Decision Analysis | Mahasweta Talik*")
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="kpi-label">Control Conversion</div>
        <div class="kpi-value">{res['rates']['A']:.2%}</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card green">
        <div class="kpi-label">Treatment Conversion</div>
        <div class="kpi-value">{res['rates']['B']:.2%}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    delta_sign = "+" if res['abs_lift'] > 0 else ""
    color_class = "green" if res['abs_lift'] > 0 else "red"
    st.markdown(f"""
    <div class="metric-card {color_class}">
        <div class="kpi-label">Relative Lift</div>
        <div class="kpi-value">{delta_sign}{res['rel_lift']:.1%}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    pval_color = "green" if stat_sig else "red"
    st.markdown(f"""
    <div class="metric-card {pval_color}">
        <div class="kpi-label">p-value</div>
        <div class="kpi-value">{res['p_val']:.5f}</div>
        <div class="kpi-delta {'delta-pos' if stat_sig else 'delta-neg'}">
            {'✅ Significant' if stat_sig else '❌ Not significant'}
        </div>
    </div>""", unsafe_allow_html=True)

with col5:
    uplift_cr = res['monthly_uplift'] / 1e7
    st.markdown(f"""
    <div class="metric-card orange">
        <div class="kpi-label">Monthly Rev Uplift</div>
        <div class="kpi-value">₹{uplift_cr:.2f}Cr</div>
    </div>""", unsafe_allow_html=True)

# ── Ship Decision Banner ──────────────────────────────────────────────────────
if ship:
    st.markdown('<div class="ship-banner">🚀 RECOMMENDATION: SHIP THE FEATURE</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="noship-banner">⛔ RECOMMENDATION: DO NOT SHIP</div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistical Results", "🔍 Segmentation", "💰 Business Impact", "✅ Decision Checklist"])

# ─── Tab 1: Statistical Results ───────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Conversion Rate Comparison")
        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(
            ["Control (A)", "Treatment (B)"],
            [res["rates"]["A"], res["rates"]["B"]],
            color=[COLORS["control"], COLORS["treatment"]],
            width=0.45, edgecolor="white", linewidth=1.5
        )
        for bar, rate in zip(bars, [res["rates"]["A"], res["rates"]["B"]]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                    f"{rate:.2%}", ha="center", fontweight="bold", fontsize=11)
        ax.axhline(y=baseline, color="grey", linestyle="--", alpha=0.7, label=f"Baseline ({baseline:.0%})")
        ax.set_ylabel("Conversion Rate")
        ax.set_title("Observed Conversion Rate by Group")
        ax.set_ylim(0, max(res["rates"]["B"] * 1.3, baseline * 1.5))
        ax.legend()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_right:
        st.subheader("Confidence Intervals (95%)")
        fig, ax = plt.subplots(figsize=(6, 4))
        ci_data = {
            "Control (A)": (res["rates"]["A"], res["ci_a"]),
            "Treatment (B)": (res["rates"]["B"], res["ci_b"]),
        }
        for i, (label, (mean, ci)) in enumerate(ci_data.items()):
            color = COLORS["control"] if i == 0 else COLORS["treatment"]
            ax.errorbar(i, mean, yerr=[[mean - ci[0]], [ci[1] - mean]],
                        fmt="o", color=color, capsize=8, capthick=2,
                        elinewidth=2, markersize=10)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Control (A)", "Treatment (B)"])
        ax.set_xlim(-0.5, 1.5)
        ax.set_ylabel("Conversion Rate")
        ax.set_title("Point Estimates with 95% CI")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Stats table
    st.subheader("Hypothesis Test Summary")
    stats_data = {
        "Metric": ["Conversions", "Users", "Conversion Rate", "Z-statistic", "p-value", "Cohen's h", "Absolute Lift", "Relative Lift"],
        "Control (A)": [
            f"{int(res['success']['A']):,}", f"{int(res['counts']['A']):,}",
            f"{res['rates']['A']:.4f}", f"{res['z_stat']:.4f}", f"{res['p_val']:.6f}",
            f"{res['cohen_h']:.4f}", "—", "—"
        ],
        "Treatment (B)": [
            f"{int(res['success']['B']):,}", f"{int(res['counts']['B']):,}",
            f"{res['rates']['B']:.4f}", "←", "←",
            "←", f"{res['abs_lift']:.4f} ({res['abs_lift']:.2%})",
            f"{res['rel_lift']:.4f} ({res['rel_lift']:.2%})"
        ],
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

# ─── Tab 2: Segmentation ──────────────────────────────────────────────────────
with tab2:
    st.subheader("Treatment Effect by Segment")
    data = res["data"]

    seg_rows = []
    for seg_col in ["device", "user_type"]:
        for val in sorted(data[seg_col].unique()):
            sd = data[data[seg_col] == val]
            ss = sd.groupby("group")["converted"].sum()
            sn = sd.groupby("group")["converted"].count()
            sr = sd.groupby("group")["converted"].mean()
            if "A" in ss.index and "B" in ss.index:
                _, sp = proportions_ztest([ss["A"], ss["B"]], [sn["A"], sn["B"]])
                lift = sr["B"] - sr["A"]
                seg_rows.append({
                    "Segment Type": seg_col.title(), "Value": val,
                    "n (Control)": int(sn["A"]), "n (Treatment)": int(sn["B"]),
                    "Conv (A)": f"{sr['A']:.3%}", "Conv (B)": f"{sr['B']:.3%}",
                    "Abs Lift": f"{lift:.3%}",
                    "Rel Lift": f"{(lift/sr['A']):.1%}",
                    "p-value": round(sp, 4),
                    "Significant": "✅" if sp < alpha_val else "❌",
                    "_lift_float": lift,
                })

    seg_df = pd.DataFrame(seg_rows)

    col1, col2 = st.columns(2)
    for col, seg_type in zip([col1, col2], ["Device", "User_type"]):
        with col:
            st.markdown(f"**By {seg_type.replace('_',' ').title()}**")
            subset = seg_df[seg_df["Segment Type"] == seg_type.replace("_"," ").title()]
            fig, ax = plt.subplots(figsize=(5, 3.5))
            colors = [COLORS["green"] if v > 0 else COLORS["red"] for v in subset["_lift_float"]]
            ax.barh(subset["Value"], subset["_lift_float"], color=colors, edgecolor="white")
            ax.axvline(0, color="black", linewidth=0.8)
            ax.axvline(res["abs_lift"], color="darkblue", linestyle="--",
                       linewidth=1.5, label=f"Overall ({res['abs_lift']:.2%})")
            for _, row in subset.iterrows():
                ax.text(row["_lift_float"] + 0.0005, list(subset["Value"]).index(row["Value"]),
                        row["Abs Lift"], va="center", fontsize=9)
            ax.set_xlabel("Absolute Lift")
            ax.legend(fontsize=8)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    display_cols = ["Segment Type", "Value", "n (Control)", "n (Treatment)", "Conv (A)", "Conv (B)", "Abs Lift", "Rel Lift", "p-value", "Significant"]
    st.dataframe(seg_df[display_cols], use_container_width=True, hide_index=True)

# ─── Tab 3: Business Impact ───────────────────────────────────────────────────
with tab3:
    st.subheader("💰 Revenue Impact Calculator")

    ci_lift_low  = res["ci_b"][0] - res["ci_a"][1]
    ci_lift_high = res["ci_b"][1] - res["ci_a"][0]

    scen_lifts = {"Conservative (CI lower)": ci_lift_low,
                  "Point Estimate": res["abs_lift"],
                  "Optimistic (CI upper)": ci_lift_high}

    col1, col2, col3 = st.columns(3)
    for col, (name, lift) in zip([col1, col2, col3], scen_lifts.items()):
        monthly = lift * monthly_users * aov
        annual  = monthly * 12
        with col:
            st.metric(name,
                      f"₹{monthly/1e7:.2f} Cr/mo",
                      f"₹{annual/1e7:.2f} Cr/yr")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("**Revenue Uplift Scenarios (Monthly)**")
        fig, ax = plt.subplots(figsize=(6, 4))
        vals   = [v * monthly_users * aov / 1e6 for v in scen_lifts.values()]
        colors_s = [COLORS["control"], COLORS["green"], COLORS["treatment"]]
        bars = ax.bar(list(scen_lifts.keys()), vals, color=colors_s, edgecolor="white")
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                    f"₹{v:.1f}M", ha="center", fontweight="bold")
        ax.set_ylabel("Revenue Uplift (₹ Millions)")
        ax.set_title("Monthly Revenue — 3 Scenarios")
        plt.xticks(rotation=10, ha="right", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_r:
        st.markdown("**Revenue Heatmap: Lift × AOV**")
        aov_range  = np.arange(400, 1601, 200)
        lift_range = np.arange(0.01, 0.06, 0.01)
        mat = np.array([[l * monthly_users * a / 1e6 for a in aov_range] for l in lift_range])
        fig, ax = plt.subplots(figsize=(6, 4))
        im = ax.imshow(mat, cmap="YlGn", aspect="auto")
        ax.set_xticks(range(len(aov_range)))
        ax.set_xticklabels([f"₹{a}" for a in aov_range], fontsize=8)
        ax.set_yticks(range(len(lift_range)))
        ax.set_yticklabels([f"{l:.0%}" for l in lift_range])
        ax.set_xlabel("Avg Order Value (₹)")
        ax.set_ylabel("Absolute Lift")
        ax.set_title("Monthly Uplift (₹M)")
        for i in range(len(lift_range)):
            for j in range(len(aov_range)):
                ax.text(j, i, f"{mat[i,j]:.0f}", ha="center", va="center",
                        fontsize=7, color="black" if mat[i,j] < 40 else "white")
        plt.colorbar(im, ax=ax, label="₹M")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

# ─── Tab 4: Decision Checklist ────────────────────────────────────────────────
with tab4:
    st.subheader("✅ Ship/No-Ship Decision Framework")

    checks = [
        ("Statistical significance (p < α)", stat_sig,
         f"p = {res['p_val']:.5f} {'<' if stat_sig else '≥'} α = {alpha_val}"),
        ("Practical significance (lift ≥ 1%)", prac_sig,
         f"Observed lift = {res['abs_lift']:.2%}"),
        ("A/A test passed", aa_pass,
         f"A/A p-value = {res['aa_p']:.4f} {'> α (no false positive)' if aa_pass else '< α (⚠️ infra issue!)'}"),
        ("Lift CI entirely above zero", lift_pos,
         f"Lift CI = [{res['ci_b'][0]-res['ci_a'][1]:.3%}, {res['ci_b'][1]-res['ci_a'][0]:.3%}]"),
    ]

    for check, passed, detail in checks:
        icon = "✅" if passed else "❌"
        color = "#d4edda" if passed else "#f8d7da"
        border = "#28a745" if passed else "#dc3545"
        st.markdown(f"""
        <div style="background:{color}; border-left:4px solid {border};
                    padding:12px 16px; border-radius:6px; margin:8px 0;">
            <strong>{icon} {check}</strong><br>
            <span style="font-size:0.9rem; color:#555;">{detail}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if ship:
        st.success("**🚀 FINAL RECOMMENDATION: SHIP**\n\nAll criteria met. Deploy the treatment with gradual rollout and monitoring.")
        st.markdown("""
        **Recommended Rollout Plan:**
        1. **Day 1**: Expand to 25% traffic, monitor error rates
        2. **Day 3**: If no regressions → 50% traffic
        3. **Day 7**: Full 100% rollout
        4. **Day 30**: Post-launch review against these metrics
        """)
    else:
        st.error("**⛔ FINAL RECOMMENDATION: DO NOT SHIP**\n\nOne or more decision criteria not met. Investigate and re-run experiment.")

    st.markdown("---")
    st.markdown("### 📌 Experiment Summary")
    st.info(f"""
    | Parameter | Value |
    |---|---|
    | Required sample per group | {res['req_n']:,} |
    | Total users in experiment | {res['req_n']*2:,} |
    | Control conversions | {int(res['success']['A']):,} ({res['rates']['A']:.2%}) |
    | Treatment conversions | {int(res['success']['B']):,} ({res['rates']['B']:.2%}) |
    | Absolute lift | {res['abs_lift']:.4f} ({res['abs_lift']:.2%}) |
    | Relative lift | {res['rel_lift']:.2%} |
    | Z-statistic | {res['z_stat']:.4f} |
    | p-value | {res['p_val']:.6f} |
    | Estimated monthly uplift | ₹{res['monthly_uplift']/1e7:.2f} Cr |
    """)
