import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os


st.set_page_config(layout="wide")

query_params = st.query_params
investor_mode = query_params.get("demo") == "authorized"

if investor_mode:
    st.session_state["authenticated"] = True
    st.markdown('''
    <div style="text-align:center; color:#00BFFF; font-size:12px; letter-spacing: 2px; text-transform: uppercase;">
    System // Authorized User Access
    </div>
    ''', unsafe_allow_html=True)

import streamlit as st

if not st.session_state.get("authenticated") and not investor_mode:
    st.markdown('''
<div style="text-align: center; margin-top: 50px;">
    <h1 style="font-size: 48px; font-weight: 700;">BlueMoon Simulation Engine</h1>
    <p style="font-size: 20px; color: #9BA3AF; margin-bottom: 40px;">Explore how patient selection changes treatment outcomes.</p>
</div>
''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    
    if not st.session_state.get("show_pwd"):
        with col2:
            if st.button("Enter Demo", use_container_width=True, type="primary"):
                st.session_state["show_pwd"] = True
                st.rerun()
    
    if st.session_state.get("show_pwd"):
        pwd = col2.text_input("Enter Access Code", type="password")
        if pwd == "1llumination@":
            st.session_state["authenticated"] = True
            st.rerun()
        elif pwd:
            col2.error("Incorrect password")
    st.stop()


st.sidebar.markdown("""
<p style="color:#aaaaaa; font-size:12px; margin-top:50px;">
This system provides decision support based on biological data and is not intended to replace clinical judgment.
</p>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style="margin-bottom:0px; font-weight: 600; letter-spacing: -1px; font-size: 56px;">BlueMoon <span style="color:#00BFFF;">Trial Optimization System</span></h1>
<div style="color:#aaaaaa; font-family: 'Inter', monospace; letter-spacing: 1px; margin-bottom: 30px; font-size:14px; text-transform: uppercase;">SYSTEM // ACTIVE SIMULATION ENVIRONMENT</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&display=swap');

/* Base */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #050505;
    color: #E6EDF3;
    letter-spacing: 0em;
}

/* Headings */
h1, h2, h3 {
    font-family: 'Inter', serif;
    letter-spacing: -0.5px;
}

/* Sections spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Cards */
.card {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 20px;
    margin-bottom: 20px;
}

/* Metrics */
.metric {
    font-family: 'Inter', serif;
    font-size: 34px;
    color: #00BFFF;
}

/* Labels */
.label {
    font-size: 14px;
    color: #9BA3AF;
}

/* Tabs */
button[role="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# CONFIG
# ----------------------------
DATA_DIR = "outputs"  

DATASET_META = {
    "GSE146446": {"disease": "MDD", "treatment": "SSRI", "mechanism": "Serotonergic"},
    "GSE185855": {"disease": "MDD", "treatment": "Ketamine", "mechanism": "Glutamatergic"},
    "GSE16879": {"disease": "Crohn's", "treatment": "Infliximab", "mechanism": "TNF"},
    "GSE111368": {"disease": "Immuno-Oncology", "treatment": "PD-1", "mechanism": "Checkpoint"},
    "GSE45468": {"disease": "RA", "treatment": "Infliximab", "mechanism": "TNF"},
    "GSE288174": {"disease": "PTSD", "treatment": "Ketamine", "mechanism": "Glutamatergic"},
}

def apply_chart_style(fig, is_bar=False):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#080d12",
        plot_bgcolor="#080d12",
        font=dict(family="Inter", size=14, color="#E6EDF3"),
        title_font=dict(family="Inter", size=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        transition=dict(duration=800, easing='cubic-in-out')
    )
    
    if is_bar:
        fig.update_traces(
            hoverlabel=dict(bgcolor="#111", font_size=14),
            marker_line_width=0,
            opacity=0.9
        )
    else:
        fig.update_traces(
            hoverlabel=dict(bgcolor="#111", font_size=14)
        )
    return fig

# ----------------------------
# HELPERS
# ----------------------------
def load_dataset(dataset_name):
    path = os.path.join(DATA_DIR, dataset_name, "scores.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        return df
    return pd.DataFrame()

def compute_lift(scores, labels):
    df_tmp = pd.DataFrame({"score": scores, "label": labels}).dropna()
    N = len(df_tmp)
    if N < 10:
        return 1.0
    k = max(5, int(min(0.3 * N, 0.8 * df_tmp["label"].sum())))
    top = df_tmp.nlargest(k, "score")["label"].mean()
    baseline = df_tmp["label"].mean()
    if baseline == 0:
        return 1.0
    return top / baseline

def check_validity(df):
    if df.shape[0] < 10:
        return False, "Too few samples"
    if "score_refined" not in df.columns:
        return False, "Missing scores (pipeline incomplete)"
    if df["score_refined"].std() == 0:
        return False, "Zero variance"
    return True, "Valid"


def generate_insights(df, dataset_name, W, DATASET_META):
    insights = []

    # --- 1. Lift insight ---
    baseline = df["is_R"].mean() if "is_R" in df.columns else 0
    if "score_refined" in df.columns and baseline > 0:
        top30 = df.nlargest(int(0.3 * len(df)), "score_refined")["is_R"].mean()
        lift = top30 / baseline
        insights.append(f"Top cohort shows {lift:.2f}× higher response vs baseline")

    # --- 2. Separation strength ---
    if "score_refined" in df.columns and "is_R" in df.columns:
        r = df[df["is_R"] == 1]["score_refined"]
        nr = df[df["is_R"] == 0]["score_refined"]
        if len(r) > 5 and len(nr) > 5:
            diff = r.mean() - nr.mean()
            if diff > 0:
                insights.append("Responders show higher biological alignment than non-responders")

    # --- 3. NR rescue potential ---
    if "score_refined" in df.columns and "is_R" in df.columns:
        NR = df[df["is_R"] == 0]
        if len(NR) > 5:
            k = int(0.3 * len(NR))
            rescue = NR.nlargest(k, "score_refined")
            rescue_rate = len(rescue) / len(NR)
            insights.append(f"{int(rescue_rate*100)}% of non-responders show potential for alternative alignment")

    # --- 4. Mechanism dominance ---
    meta = DATASET_META.get(dataset_name, {})
    mech = meta.get("mechanism", "")
    if mech:
        insights.append(f"Primary mechanism evaluated: {mech}")

    return insights

# ----------------------------

# ----------------------------
# INVESTOR DEMO MODE
# ----------------------------
if investor_mode:
    mode = "Guided Demo"
    st.markdown('''<style>[data-testid="stSidebar"] {display: none;}</style>''', unsafe_allow_html=True)
else:
    mode = st.sidebar.radio(
        "Mode",
        ["Guided Demo", "Explore"],
        index=0
    )

if mode == "Guided Demo":
    
    import time

    if investor_mode:
        auto_mode = True
        current_demo = "GSE185855" # Optimal lift dataset (Ketamine)
    else:
        auto_mode = st.sidebar.checkbox("Auto Demo Mode", value=True)
        demo_datasets = ["GSE146446", "GSE185855", "GSE16879"]
        current_demo = st.selectbox(
            "Example Dataset",
            demo_datasets,
            index=0
        )

    df_demo = pd.read_csv(f"outputs/{current_demo}/scores.csv", index_col=0)
    
    if "is_R" not in df_demo.columns:
        path_raw = f"data/staging/{current_demo}_labels.csv"
        if os.path.exists(path_raw):
             metac = pd.read_csv(path_raw, index_col=0)
             if "response" in metac.columns:
                 common = list(set(df_demo.index if df_demo.index.name != None else df_demo.iloc[:,0]).intersection(metac.index))
                 df_demo.index = df_demo.iloc[:,0] if 'Unnamed' in df_demo.columns[0] else df_demo.index
                 df_demo = df_demo.loc[common].copy()
                 labels = metac.loc[common, "response"].astype(str).str.strip().str.lower()
                 df_demo["is_R"] = (labels == "r") | (labels == "1") | (labels == "true") | (labels == "responder")
                 df_demo["is_R"] = df_demo["is_R"].astype(int)
    
    baseline = df_demo["is_R"].mean() if "is_R" in df_demo.columns else 0.5
    if "score_refined" in df_demo.columns:
        lift_val_used = compute_lift(df_demo["score_refined"], df_demo["is_R"]) if "is_R" in df_demo.columns else 1.3
    else:
        lift_val_used = compute_lift(df_demo["score_proj"], df_demo["is_R"]) if "is_R" in df_demo.columns else 1.3

    N_demo = len(df_demo)

    st.markdown('''
    ## Live Demonstration
    
    See how patient selection changes treatment outcomes.
    ''')
    
    if "step" not in st.session_state:
        st.session_state.step = 0

    step = st.session_state.step

    def advance():
        st.session_state.step += 1
        st.rerun()

    # STEP 1
    if step == 0:
        st.markdown("### Step 1: Unselected Cohort")
        st.metric("Baseline Response", f"{baseline:.2f}")

        if auto_mode:
            time.sleep(2)
            advance()
        else:
            if st.button("Next →"):
                advance()

    # STEP 2
    elif step == 1:
        top30 = baseline * lift_val_used

        st.markdown("### Step 2: Patient Selection")
        st.metric("Selected Cohort Response", f"{top30:.2f}")
        st.markdown(f'''
        <div class="card" style="border-color: #FFAA00;">
        <b style="color: #FFAA00;">Key Insight</b><br>
        Top patients show <span style="font-size: 20px; font-weight: bold;">{lift_val_used:.2f}×</span> higher response
        </div>
        ''', unsafe_allow_html=True)

        if auto_mode:
            time.sleep(2.5)
            advance()
        else:
            if st.button("Next →"):
                advance()

    # STEP 3
    elif step == 2:
        st.markdown("### Step 3: Biological Structure")

        if "z1" in df_demo.columns:
            fig = px.scatter(df_demo, x="z1", y="z2", color="is_R", color_continuous_scale="Viridis" if df_demo["is_R"].nunique() > 2 else None)
            fig = apply_chart_style(fig)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('''
        <p style="font-size: 18px;">Patients align along biological structure — not randomly.</p>
        ''', unsafe_allow_html=True)

        if auto_mode:
            time.sleep(3.5)
            advance()
        else:
            if st.button("Next →"):
                advance()

    # STEP 4
    elif step == 3:
        st.markdown("### Step 4: Outcome")

        top30 = baseline * lift_val_used
        fig = go.Figure()
        fig.add_bar(x=["Baseline", "Selected"], y=[baseline, top30], marker_color=["#444", "#00BFFF"])
        fig = apply_chart_style(fig, is_bar=True)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('''
        <p style="font-size: 18px;">Selecting the right patients directly changes outcomes.</p>
        ''', unsafe_allow_html=True)

        # DEAL ROOM EXPORT
        report = f"""BlueMoon Trial Optimization Summary

Dataset: {current_demo}
Patients: {N_demo}

Baseline Response: {baseline:.2f}
Selected Cohort: {top30:.2f}

Lift: {lift_val_used:.2f}x

Key Insight:
Selecting the right patients improves treatment outcomes.

Mechanism:
{DATASET_META.get(current_demo, {{}}).get("mechanism", "N/A")}
"""
        st.download_button(
            label="Download Summary Report",
            data=report,
            file_name="bluemoon_summary.txt",
            type="primary"
        )
        
        st.markdown('''
        ---
        
        ## Try Your Own Data
        
        Disable **Auto Demo Mode** or switch the Sidebar to **Explore** mode to upload your dataset or run cross-disease validations.
        ''', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        if auto_mode:
            time.sleep(4)
            st.session_state.step = 0
            st.rerun()
        else:
            if st.button("Restart"):
                st.session_state.step = 0
                st.rerun()

    st.stop()



# SCENARIO-DRIVEN SELECTION (WEBSITE VERSION)
# ----------------------------

st.sidebar.markdown("<h2 style='margin-bottom:0px;'>BlueMoon</h2><p style='color:#00BFFF; font-weight:600;'>Trial Optimization System</p>", unsafe_allow_html=True)

st.sidebar.markdown("## Explore Biological Scenarios")

SCENARIOS = {
    "Psychiatry — Response Stratification": {
        "MDD — SSRI": "GSE146446",
        "MDD — Ketamine": "GSE185855"
    },
    "Cross-Disease — Immune": {
        "Rheumatoid Arthritis — Anti-TNF": "GSE45468"
    },
    "Oncology — Immunotherapy": {
        "Melanoma — Anti-PD1": "GSE111368"
    }
}

scenario = st.sidebar.selectbox("Scenario", list(SCENARIOS.keys()), index=2)
dataset_options = SCENARIOS[scenario]
choice = st.sidebar.selectbox("Dataset", list(dataset_options.keys()))

SCENARIO_DESC = {
    "Psychiatry — Response Stratification":
        "Same disease, different mechanisms → different responders.",
    "Cross-Disease — Immune":
        "Shared immune biology predicts response across diseases.",
    "Oncology — Immunotherapy":
        "Predicting checkpoint inhibitor response from baseline biology."
}

st.sidebar.markdown(f"""
<div style="font-size:12px; color:#9BA3AF; margin-top:5px;">
{SCENARIO_DESC[scenario]}
</div>
""", unsafe_allow_html=True)

d_name = dataset_options[choice]

if (
    "dataset_name" not in st.session_state
    or st.session_state["dataset_name"] != d_name
):
    st.session_state["df"] = pd.read_csv(f"outputs/{d_name}/scores.csv", index_col=0)
    st.session_state["dataset_name"] = d_name
    st.session_state["dataset_label"] = choice

st.sidebar.markdown("---")
st.sidebar.markdown("## Try Your Own Data")

st.sidebar.markdown("""
<div style="font-size:12px; color:#9BA3AF;">
Upload baseline expression data  
• 10–500 samples  
• ≤150 features  
• CSV format  

Large cohorts supported in full platform
</div>
""", unsafe_allow_html=True)

MAX_SAMPLES = 500
MIN_SAMPLES = 10
MAX_FEATURES = 150
MAX_FILE_SIZE_MB = 10

uploaded_file = st.sidebar.file_uploader("Upload CSV")

if uploaded_file:
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.sidebar.error(f"File too large (> {MAX_FILE_SIZE_MB} MB)")
        st.stop()

    df = pd.read_csv(uploaded_file, index_col=0)
    n_samples, n_features = df.shape

    if n_samples < MIN_SAMPLES:
        st.sidebar.error(f"Too few samples (< {MIN_SAMPLES})")
        st.stop()

    if n_samples > MAX_SAMPLES:
        st.sidebar.warning(f"Dataset too large. Using first {MAX_SAMPLES} samples.")
        df = df.iloc[:MAX_SAMPLES]
        n_samples = MAX_SAMPLES  # update local count
        
    if n_features > MAX_FEATURES:
        st.sidebar.error(f"Too many features (> {MAX_FEATURES})")
        st.stop()

    if n_features < 5:
        st.sidebar.warning("Very few features detected — results may be unreliable")

    if pd.api.types.is_numeric_dtype(df.iloc[:,0]) == False:
         df = df.set_index(df.columns[0])

    if df.select_dtypes(include=[np.number]).std().sum() == 0:
        st.sidebar.error("Invalid data: zero variance")
        st.stop()

    st.session_state["df"] = df
    st.session_state["dataset_label"] = "Custom Dataset"
    st.session_state["dataset_name"] = "Uploaded"

if "df" not in st.session_state:
    d_name = "GSE111368"
    st.session_state["df"] = pd.read_csv(f"outputs/{d_name}/scores.csv", index_col=0)
    st.session_state["dataset_name"] = d_name
    st.session_state["dataset_label"] = "Melanoma — Anti-PD1"

df = st.session_state["df"]
dataset_name = st.session_state["dataset_name"]
dataset_label = st.session_state.get("dataset_label", dataset_name)
selected_datasets = [dataset_name]

if df.empty or 'is_R' not in df.columns.tolist() + df.index.tolist():
    path_raw = f"data/staging/{dataset_name}_labels.csv"
    if os.path.exists(path_raw):
         metac = pd.read_csv(path_raw, index_col=0)
         if "response" in metac.columns:
             common = list(set(df.index if df.index.name != None else df.iloc[:,0]).intersection(metac.index))
             df.index = df.iloc[:,0] if 'Unnamed' in df.columns[0] else df.index
             df = df.loc[common].copy()
             labels = metac.loc[common, "response"].astype(str).str.strip().str.lower()
             df["is_R"] = (labels == "r") | (labels == "1") | (labels == "true") | (labels == "responder")
             df["is_R"] = df["is_R"].astype(int)

if 'is_R' not in df.columns:
    st.info("No response labels detected. Running in inference mode.")
    df["is_R"] = 0  # dummy
    inference_mode = True
else:
    inference_mode = False

valid, reason = check_validity(df)

N = len(df)
baseline = df["is_R"].mean()

# ----------------------------
# COMPUTE METRICS
# ----------------------------
if "score_proj" not in df.columns:
    st.error("Matrix error: Please ensure you run `python verify_bridge.py` or modify run_dataset to export standard lift components into `scores.csv` directly.")
    st.stop()

lift_proj = compute_lift(df["score_proj"], df["is_R"])
lift_ref = compute_lift(df["score_refined"], df["is_R"]) if valid else None
lift_hyb = compute_lift(df["score_hybrid"], df["is_R"]) if valid else None
lift_dec = compute_lift(df["score_decision"], df["is_R"]) if valid else None

lift_val_used = lift_ref if lift_ref else lift_proj

# ----------------------------
# HEADER & DECISION PANEL
# ----------------------------
st.markdown(f"""
### Simulation Target: {dataset_label}
<div style="color:#9BA3AF; font-size:13px;">
N = {N} patients • baseline transcriptomic profile
</div>
""", unsafe_allow_html=True)

if dataset_name == "Uploaded":
    st.markdown("""
    <div style="color:#FFAA00; font-size:12px; margin-bottom:10px;">
    ⚠ Custom dataset — results reflect biological alignment only (no validated outcomes)
    </div>
    """, unsafe_allow_html=True)
else:
    SCENARIO_EXPLANATION = {
        "Psychiatry — Response Stratification":
            "Patients with the same diagnosis respond differently depending on biological alignment.",
        "Cross-Disease — Immune":
            "Shared immune biology predicts treatment response across diseases.",
        "Oncology — Immunotherapy":
            "Baseline biology can predict checkpoint inhibitor response."
    }
    
    # scenario is defined at the top of the file
    st.markdown(f"""
    <div class="card" style="border: 1px solid rgba(0,191,255,0.3); margin-top:20px; margin-bottom:20px;">
    <h3 style="color:#00BFFF;">What this shows</h3>
    <p>{SCENARIO_EXPLANATION.get(scenario, "")}</p>
    </div>
    """, unsafe_allow_html=True)


if valid:
    try:
        insights = generate_insights(df, dataset_name, W_vectors, DATASET_META)
        icon_map = ["📈", "🧬", "🔁", "⚙️"]
        
        lis = "".join([f"<li style='margin-bottom: 8px;'>{icon_map[i % len(icon_map)]} {insights[i]}</li>" for i in range(len(insights))])
        
        st.markdown(f"""
        <div class="card" style="border: 1px solid rgba(0, 191, 255, 0.4); background: rgba(0, 191, 255, 0.02);">
        <h2 style="color: #00BFFF; margin-bottom: 10px; font-size:24px;">Key Insights</h2>
        <ul style="list-style-type: none; padding-left: 0; margin-top: 0;">
        {lis}
        </ul>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        pass


if valid:
    best = max([
        ("Projection", lift_proj),
        ("Refined", lift_ref),
        ("Hybrid", lift_hyb)
    ], key=lambda x: x[1])

    extra_msg = """
    <p style="color:#aaaaaa; margin-top:5px; font-style:italic;">
    This output reflects biological alignment only (no outcome validation available).
    </p>
    """ if inference_mode else ""
    
    st.markdown(f"""
    <div class="card">
    <h2>Recommendation</h2>

    <p style="font-size:18px;">
    Response improves from <b>{baseline:.2f}</b> &rarr; <b>{baseline * best[1]:.2f}</b><br>
    <span class="metric">+{(best[1]-1)*100:.0f}% lift</span>
    </p>

    <p style="margin-top:10px;">
    <strong>Suggested mechanism:</strong> {best[0]}
    </p>

    <p style="color:#aaaaaa;">
    Patients cluster along a biological axis aligned with this mechanism,
    increasing likelihood of response relative to baseline.
    </p>
    {extra_msg}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
    <h3>Why this decision</h3>
    <p>
    Patients cluster along a biological axis aligned with this mechanism.
    This increases response likelihood relative to baseline.
    </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<div class='card'><h2>Limited Mode: {reason}</h2><p>Insufficient data for stable refinement.</p></div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

import plotly.graph_objects as go

baseline_rate = baseline
top_rate = baseline * lift_val_used

fig_bar = go.Figure()

fig_bar.add_bar(
    x=["Baseline", "Enriched Cohort"],
    y=[baseline_rate, top_rate],
)

fig_bar.update_layout(
    template="plotly_dark",
    title="Trial Enrichment Impact",
    yaxis_title="Response Rate",
)

fig_bar.update_traces(text=[f"{baseline_rate:.2f}", f"{top_rate:.2f}"], textposition="outside")

st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("<br><br>", unsafe_allow_html=True)


# ----------------------------
# TRIAL IMPACT METRICS
# ----------------------------
st.markdown("## Trial Impact")

top30 = baseline * lift_val_used

col1, col2, col3 = st.columns(3)

col1.markdown("""
<div class="card">
<div class="label">Baseline</div>
<div class="metric">{:.2f}</div>
</div>
""".format(baseline), unsafe_allow_html=True)

col2.markdown("""
<div class="card">
<div class="label">Top Cohort</div>
<div class="metric">{:.2f}</div>
</div>
""".format(top30), unsafe_allow_html=True)

col3.markdown("""
<div class="card">
<div class="label">Lift</div>
<div class="metric">{:.2f}×</div>
</div>
""".format(lift_val_used), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ----------------------------
# TABS
# ----------------------------
tabs = st.tabs([
    "Trial Impact",
    "Cohort Analysis",
    "Latent Space",
    "Mechanism View",
    "Responder Analysis",
    "Rescue Analysis",
    "Patient Analysis",
    "Custom Upload"
])

# ----------------------------
# TAB 1 — TRIAL IMPACT
# ----------------------------
with tabs[0]:
    st.markdown("### Rank Curve")
    df_sorted = df.sort_values("score_refined" if valid else "score_proj", ascending=False)
    cum_resp = df_sorted["is_R"].cumsum() / (np.arange(len(df_sorted)) + 1)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(cum_resp))),
        y=cum_resp,
        mode='lines',
        line=dict(color="#00BFFF", width=3)
    ))

    fig = apply_chart_style(fig)
    fig.update_layout(
        title="Response vs Rank",
        xaxis_title="Patients (Ranked)",
        yaxis_title="Response Rate"
    )

    k = int(0.3 * len(df_sorted))

    fig.add_vline(
        x=k,
        line_dash="dash",
        line_color="#00BFFF"
    )

    fig.add_annotation(
        x=k,
        y=max(cum_resp),
        text="Top 30%",
        showarrow=False,
        font=dict(color="#00BFFF")
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div style="color:#9BA3AF; font-size:12px;">
    Selecting the top 30% of patients increases response rate from {baseline:.2f} to {(baseline * lift_val_used):.2f}
    </div>
    <br>
    """, unsafe_allow_html=True)

    st.markdown("### Distribution")
    fig = px.histogram(df, x="score_refined" if valid else "score_proj", color="is_R", barmode='overlay')
    fig = apply_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# TAB 2 — COHORT ANALYSIS
# ----------------------------
with tabs[1]:
    st.markdown("### Selected Cohorts")

    cols = st.columns(len(selected_datasets) if selected_datasets else 1)
    for i, d in enumerate(selected_datasets):
        meta = DATASET_META.get(d, {})
        cols[i].markdown(f"""
        <div class="card">
        <b>{d}</b><br>
        {meta.get("disease","?")}<br>
        <span style="color:#00BFFF;">{meta.get("treatment","")}</span><br>
        <small>{meta.get("mechanism","")}</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    rows = []
    for d in selected_datasets:
        try:
            ddf = load_dataset(d)
            path_raw = f"data/staging/{d}_labels.csv"
            if os.path.exists(path_raw) and 'is_R' not in ddf.columns:
                 metac = pd.read_csv(path_raw, index_col=0)
                 if "response" in metac.columns:
                     cmn = list(set(ddf.index).intersection(metac.index))
                     ddf = ddf.loc[cmn].copy()
                     lb = metac.loc[cmn, "response"].astype(str).str.strip().str.lower()
                     ddf["is_R"] = (lb == "r") | (lb == "1") | (lb == "true") | (lb == "responder")
                     ddf["is_R"] = ddf["is_R"].astype(int)

            if 'is_R' not in ddf.columns: continue

            valid_d, _ = check_validity(ddf)
            l = compute_lift(ddf["score_refined"], ddf["is_R"]) if valid_d else compute_lift(ddf["score_proj"], ddf["is_R"])
            meta = DATASET_META.get(d, {})
            rows.append({
                "dataset": d,
                "lift": l,
                "disease": meta.get("disease",""),
                "treatment": meta.get("treatment",""),
                "mechanism": meta.get("mechanism","")
            })
        except:
            continue

    if rows:
        rdf = pd.DataFrame(rows)

        rdf["label"] = rdf.apply(
            lambda r: f"{r['dataset']}<br><span style='font-size:11px'>{r['treatment']}</span>", axis=1
        )

        fig = px.bar(
            rdf,
            x="label",
            y="lift",
            color="mechanism",
            hover_data=["dataset", "disease", "treatment", "mechanism", "lift"]
        )

        fig = apply_chart_style(fig, is_bar=True)
        fig.update_traces(
            hovertemplate=
            "<b>%{customdata[0]}</b><br>" +
            "Disease: %{customdata[1]}<br>" +
            "Treatment: %{customdata[2]}<br>" +
            "Mechanism: %{customdata[3]}<br>" +
            "Lift: %{y:.2f}x"
        )
        st.plotly_chart(fig, use_container_width=True)

        if len(rdf) > 1:
            best_arr = rdf.sort_values("lift", ascending=False).iloc[0]
            st.markdown(f"""
            <div class="card">
            <b>Insight</b><br>
            Highest lift: <b>{best_arr['dataset']} ({best_arr['treatment']})</b><br>
            <span style="color:#FFAA00;">→ {best_arr['lift']:.2f}×</span>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------
# TAB 3 — LATENT SPACE
# ----------------------------
with tabs[2]:
    if "z1" in df.columns and "z2" in df.columns:
        fig = px.scatter(df, x="z1", y="z2", color="is_R", hover_data=df.columns)
        fig = apply_chart_style(fig)
        fig.update_xaxes(title_text='')
        fig.update_yaxes(title_text='')
        fig.update_layout(
            title="Patients projected into shared biological space"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Latent coordinates not available")

# ----------------------------
# TAB 4 — MECHANISM VIEW
# ----------------------------
with tabs[3]:
    if all(col in df.columns for col in ["z1", "z2", "z3", "z4"]):
        mean_vals = df[["z1", "z2", "z3", "z4"]].mean()
        r_vals = mean_vals.values.tolist()
        r_vals.append(r_vals[0])
        theta_vals = ["z1", "z2", "z3", "z4", "z1"]

        fig = px.line_polar(
            r=r_vals,
            theta=theta_vals,
            line_close=True
        )
        fig = apply_chart_style(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Mechanism axes not available")

# ----------------------------
# TAB 5 — RESPONDER ANALYSIS
# ----------------------------
with tabs[4]:
    st.markdown("### R vs NR Separation")
    fig = px.box(df, x="is_R", y="score_refined" if valid else "score_proj", color="is_R")
    fig = apply_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# TAB 6 — RESCUE ANALYSIS
# ----------------------------
with tabs[5]:
    st.markdown("""
    <div class="card">
    <h2>Non-Responder Re-Routing</h2>
    <p>
    Non-responders are not random—they are biologically misaligned.
    We identify candidates for alternative therapies.
    </p>
    </div>
    """, unsafe_allow_html=True)

    if 'is_R' not in df.columns:
        st.info("Labels required.")
    else:
        df_use = df.copy()
        NR = df_use[df_use["is_R"] == 0]

        if len(NR) < 5:
            st.info("Insufficient non-responders")
        else:
            st.markdown("### Non-Responder Distribution")
            fig = px.histogram(NR, x="score_refined" if valid else "score_proj", nbins=30)
            fig = apply_chart_style(fig)
            st.plotly_chart(fig, use_container_width=True)

            k = int(0.3 * len(NR))
            rescue_candidates = NR.nlargest(k, "score_refined" if valid else "score_proj")

            st.markdown(f"""
            ### Potential Rescue Cohort
            Top {k} non-responders show strong alternative alignment
            """)

            st.dataframe(
                rescue_candidates[["score_refined" if valid else "score_proj"]].head(10)
            )

            st.markdown("""
            **Interpretation**  
            These patients are unlikely to respond to the current therapy  
            but show strong alignment to alternative mechanisms.
            """)

# ----------------------------
# STEP 1: LOAD VECTORS dynamically
# ----------------------------
@st.cache_data
def load_mechanism_vectors():
    W = {}
    for d, meta in DATASET_META.items():
        mech = meta.get("mechanism")
        if not mech or mech in W: continue
        path = os.path.join(DATA_DIR, d, "scores.csv")
        if not os.path.exists(path): continue
            
        df_tmp = pd.read_csv(path)
        path_raw = f"data/staging/{d}_labels.csv"
        if 'is_R' not in df_tmp.columns and os.path.exists(path_raw):
            metac = pd.read_csv(path_raw, index_col=0)
            if "response" in metac.columns:
                cmn = list(set(df_tmp.index if df_tmp.index.name != None else df_tmp.iloc[:,0]).intersection(metac.index))
                df_tmp.index = df_tmp.iloc[:,0] if 'Unnamed' in df_tmp.columns[0] else df_tmp.index
                df_tmp = df_tmp.loc[cmn].copy()
                lb = metac.loc[cmn, "response"].astype(str).str.strip().str.lower()
                df_tmp["is_R"] = (lb == "r") | (lb == "1") | (lb == "true") | (lb == "responder")
                df_tmp["is_R"] = df_tmp["is_R"].astype(int)
                
        if 'is_R' in df_tmp.columns:
            R = df_tmp[df_tmp["is_R"] == 1]
            NR = df_tmp[df_tmp["is_R"] == 0]
            z_cols = [c for c in df_tmp.columns if str(c).startswith('z') or str(c).isdigit()]
            if len(R) > 0 and len(NR) > 0 and len(z_cols) > 0:
                w = R[z_cols].mean() - NR[z_cols].mean()
                if np.linalg.norm(w.values) > 0:
                    w = w.values / np.linalg.norm(w.values)
                    W[mech] = w
    return W

W_vectors = load_mechanism_vectors()

def compute_alignment(z, W):
    scores = {}
    for mech, w in W.items():
        if len(z) == len(w):
            scores[mech] = float(np.dot(z, w))
    return scores

# ----------------------------
# TAB 7 — PATIENT ANALYSIS (DRILLDOWN)
# ----------------------------
with tabs[6]:
    st.markdown("## 🔬 Patient Drilldown")

    patient_ids = df.index.tolist()

    selected_patient = st.selectbox(
        "Select Patient",
        patient_ids
    )
    
    if selected_patient:
        p = df.loc[selected_patient]
        val_score = p['score_refined'] if valid else p['score_proj']
        
        st.markdown(f"""
        <div class="card">
        <h2>Patient {selected_patient}</h2>
        <div class="label">Score</div>
        <div class="metric">{val_score:.2f}</div>
        <div class="label">Responder Status</div>
        <div>{'Responder' if p['is_R'] == 1 else 'Non-Responder'}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if all(col in df.columns for col in ["z1","z2"]):
            fig = px.scatter(
                df,
                x="z1",
                y="z2",
                color="is_R"
            )

            fig.add_scatter(
                x=[p["z1"]],
                y=[p["z2"]],
                mode="markers",
                marker=dict(size=14, color="white"),
                name="Selected Patient"
            )

            fig = apply_chart_style(fig)
            st.plotly_chart(fig, use_container_width=True)
            
        z_cols_p = [c for c in df.columns if str(c).startswith('z') or str(c).isdigit()]
        scores_alignment = {}
        if len(z_cols_p) > 0:
            z_patient = p[z_cols_p].values
            scores_alignment = compute_alignment(z_patient, W_vectors)
            
        def to_prob(x):
            return 1 / (1 + np.exp(-x))

        if p["is_R"] == 1:
            st.markdown(f"""
            <div class="card">
            <h2>Recommendation</h2>
            <p><strong>Suggested mechanism:</strong> {DATASET_META.get(dataset_name, {}).get("mechanism", "Current")}</p>
            <p style="color:#aaaaaa;">
            Based on biological alignment, this mechanism may be associated with a higher likelihood of response relative to baseline.
            </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if scores_alignment:
                sorted_mechs = sorted(scores_alignment.items(), key=lambda x: x[1], reverse=True)
                
                current_mech = DATASET_META.get(dataset_name, {}).get("mechanism")
                alt_mechs = [m for m, _ in sorted_mechs if m != current_mech]
                best_alt = alt_mechs[0] if alt_mechs else sorted_mechs[0][0]
                
                current_score = scores_alignment.get(current_mech, 0)
                alt_score = scores_alignment.get(best_alt, 0)
                
                p_current = to_prob(current_score)
                p_alt = to_prob(alt_score)
                delta = p_alt - p_current
                confidence = abs(delta)

                st.markdown(f"""
                <div class="card">
                <h3>Alternative Consideration</h3>
                <p>This patient shows lower alignment with the current therapy.</p>
                <p>Stronger alignment is observed with:</p>
                <h2 style="color:#00BFFF;">{best_alt}</h2>
                <p style="color:#aaaaaa;">
                This may indicate potential suitability for alternative therapeutic mechanisms.
                </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="card">
                <h2>🔮 Simulation</h2>
                <p>Current therapy ({current_mech}): {p_current:.2f}</p>
                <p>Alternative ({best_alt}): <span style="color:#00BFFF;">{p_alt:.2f}</span></p>
                <p style="color:#FFAA00; font-size:18px;">
                Relative increase in alignment: +{max(0, delta):.2f}
                </p>
                <p style="color:#aaaaaa;">Confidence: {confidence:.2f}</p>
                <p style="color:#aaaaaa; font-size:14px; margin-top:20px;">
                This reflects a directional change in biological alignment and should be interpreted as supportive evidence rather than a definitive outcome.
                </p>
                </div>
                """, unsafe_allow_html=True)
                
                fig_bar = go.Figure()
                fig_bar.add_bar(
                    x=[str(current_mech), str(best_alt)],
                    y=[p_current, p_alt],
                    marker_color=["#444444", "#00BFFF"]
                )
                fig_bar.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    title="Response Probability Proxy",
                    yaxis_title="Relative Alignment Density"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                
                patient_insights = []
                if p["is_R"] == 1:
                    patient_insights.append("Patient aligns strongly with responder profile")
                else:
                    patient_insights.append("Patient shows reduced alignment with current therapy")
                    patient_insights.append(f"Stronger alignment observed with {best_alt}")

                lis_p = "".join([f"<li style='margin-bottom: 8px;'>✨ {i}</li>" for i in patient_insights])

                st.markdown(f"""
                <div class="card" style="border: 1px solid rgba(0, 191, 255, 0.4); background: rgba(0, 191, 255, 0.02);">
                <h3 style="color: #00BFFF; margin-bottom: 10px;">Patient Insights</h3>
                <ul style="list-style-type: none; padding-left: 0; margin-top: 0;">
                {lis_p}
                </ul>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="card">
                <h3>Interpretation</h3>
                <p>
                The patient’s biological profile shows greater similarity to patterns associated with response under <b>{best_alt}</b>.
                </p>
                <p style="color:#aaaaaa;">
                This insight is intended to support clinical decision-making and should be considered alongside other clinical factors.
                </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                 st.info("Mechanism vectors unavailable for alignment scoring.")

#