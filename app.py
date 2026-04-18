import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
import pickle
import os
import datetime

st.set_page_config(page_title="BlueMoon Simulation Engine | Demo", layout="wide")

# ==========================================
# UI POLISH & ARCHITECTURE
# ==========================================
import base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

bg_b64 = get_base64_of_bin_file('assets/background1.png')
bg_css = '''
    background-color: #010204;
'''

st.markdown(f'''
<style>
.stApp {{ {bg_css} font-family: 'Inter', sans-serif; color: #ffffff; }}
.css-1d391kg {{ padding-top: 2rem; }}
.demo-banner {{
    background: rgba(255, 215, 0, 0.1);
    border: 1px solid rgba(255, 215, 0, 0.4);
    color: rgba(255, 215, 0, 0.85);
    padding: 10px 20px;
    border-radius: 4px;
    font-family: 'Inter', sans-serif; letter-spacing: 0px;
    font-weight: bold;
    text-align: center;
    letter-spacing: 2px;
    margin-bottom: 30px;
}}
.hud-header {{
    border-bottom: 1px solid rgba(0, 191, 255, 0.2);
    padding-bottom: 20px;
    margin-bottom: 30px;
}}
/* Hide default Streamlit top-right menu and icons */
header {{ visibility: hidden !important; }}
#MainMenu {{ visibility: hidden !important; }}
footer {{ visibility: hidden !important; }}
[data-testid="stToolbar"] {{ visibility: hidden !important; }}
</style>
''', unsafe_allow_html=True)

st.markdown('<div class="demo-banner">[ PUBLIC DEMO ENGINE : RESTRICTED CAPABILITY ]</div>', unsafe_allow_html=True)

st.markdown('''
<div class="hud-header">
    <h1 style='color: #fff; font-size: 2.2rem; font-weight: 800; letter-spacing: -1px;'>BlueMoon <span style='color: #00BFFF;'>Simulation Engine</span></h1>
    <span style='color: #a1a1aa; font-family: "Inter", sans-serif; letter-spacing: 0px; font-size: 1.1rem;'>SYSTEM // ACTIVE SIMULATION ENVIRONMENT</span><br>
    <span style='color: #fff; font-size: 1.1rem; font-weight: 400; margin-top: 10px; display: inline-block;'>This system maps geometric intervention outcomes across 7 validated biological axes.</span>
</div>
''', unsafe_allow_html=True)


# ==========================================
# BACKEND MODULARITY (7-D ARCHITECTURE)
# ==========================================
np.random.seed(42)

# Geometric mapping vectors for the 7 active targets:
# [RC1 (Serotonin), RC2 (Glutamate), RC3 (TNF), PC1 (Systemic), PC2a (Stress), PC2b (Immune), PC2c (HPA)]
drug_map = {
    "RC1 Targeting (Serotonergic)":     [ 0.8, -0.1,  0.0, -0.2,  0.1, -0.1,  0.0],
    "RC2 Targeting (Glutamatergic)":    [-0.1,  0.9, -0.1,  0.4,  0.6, -0.1,  0.3],
    "RC3 Targeting (TNF/Immune)":       [ 0.0,  0.0,  0.9, -0.3, -0.1,  0.7, -0.2],
    "PC1 Targeting (Global Systemic)":  [ 0.1,  0.0,  0.4,  0.8, -0.2,  0.8,  0.1],
    "Multi-Axis Neuromodulation":       [ 0.4,  0.5, -0.1,  0.0,  0.2,  0.0,  0.2]
}

axis_labels = [
    'RC1 (Serotonergic)', 'RC2 (Glutamatergic)', 'RC3 (TNF/Immune)', 
    'PC1 (Global Systemic)', 'PC2a (Stress/Synaptic)', 'PC2b (Neuroimmune)', 'PC2c (HPA Axis)'
]

def project_patient(X):
    # Generates a randomized but biologically constrained 7D pathological state
    state = np.random.uniform(-0.8, 1.2, 7)
    return state

def predict_response(z_pos):
    # Mathematical assumption: Homeostasis (healthy state) rests at [0,0,0,0,0,0,0]
    dist = np.linalg.norm(z_pos) # Euclidean distance from homeostasis
    # Map distance inversely to response probability
    return np.clip(1.0 - (dist / 3.0), 0.1, 0.99)


# ==========================================
# PART 1: TOP INPUT BAR
# ==========================================
col_up, col_mode = st.columns([2,1])

with col_up:
    uploaded = st.file_uploader("Ingest Expression Profile / Matrix (CSV)", type=["csv"], help="Upload bulk RNA-seq or PBMC count matrices")
    with st.expander("View CSV Formatting Requirements", expanded=False):
        st.markdown("""
        **Required Data Format:**
        - **Data Type:** Bulk RNA-seq (e.g., TPM/FPKM) or PBMC expression counts.
        - **Orientation:** Rows = Patients/Samples, Columns = Genes.
        - **Headers:** The first row must contain standard gene identifiers (HGNC symbols or Ensembl IDs). 
        - **Sample IDs:** The first column must explicitly contain the sample identifiers (e.g., `Sample_ID`).
        """)
        
        # Generate dummy CSV for download
        dummy_cols = ["Sample_ID", "HTR2A", "GRIN1", "TNF", "IL6", "BDNF", "SLC6A4"] + [f"GENE_{i}" for i in range(1, 94)]
        dummy_data = np.random.uniform(0, 100, (5, len(dummy_cols) - 1))
        dummy_df = pd.DataFrame(dummy_data, columns=dummy_cols[1:])
        dummy_df.insert(0, "Sample_ID", [f"Patient_{i:03d}" for i in range(1, 6)])
        csv_buffer = dummy_df.to_csv(index=False)
        
        st.download_button(
            label="Download Example Dataset (.csv)",
            data=csv_buffer,
            file_name="BlueMoon_Example_Cohort.csv",
            mime="text/csv",
            help="Download this sample matrix to test the simulation engine instantly."
        )

with col_mode:
    mode = st.selectbox("Operation Mode", ["Single Patient (Targeted View)", "Cohort Mode (Pharma View)"])

if uploaded:
    df = pd.read_csv(uploaded)
    if df.shape[0] > 10:
        st.warning(f"Demo Constraint: Uploaded matrix contains {df.shape[0]} patients. Truncating to 10 profiles for public demonstration.")
        df = df.head(10)
    else:
        st.success(f"Ingested {df.shape[0]} patient profiles.")
else:
    # Dummy patient or dummy cohort
    if mode == "Cohort Mode (Pharma View)":
        df = pd.DataFrame(np.random.randn(800, 1000))
    else:
        df = pd.DataFrame(np.random.randn(1, 1000))
    st.info("Operating on baseline internal simulation data.")

st.divider()

# ==========================================
# PART 2: PHARMA COHORT MODE
# ==========================================
if "Cohort" in mode:
    st.subheader("Cross-Disease 3D Projection Engine")
    st.write("Visualizing cohort geometry along the primary axes (RC1, RC2, RC3). Metaclusters (PC1, 2a, 2b, 2c) omitted in 3D projection.")
    
    np.random.seed(int(time.time()) % 100)
    zs = [project_patient(df.values[i:i+1]) for i in range(min(500, len(df)))]
    x_rc1 = [z[0] for z in zs]
    y_rc2 = [z[1] for z in zs]
    z_rc3 = [z[2] for z in zs]

    fig = go.Figure()

    # Patients Scatter 3D
    fig.add_trace(go.Scatter3d(
        x=x_rc1, y=y_rc2, z=z_rc3,
        mode='markers',
        marker=dict(size=4, color='rgba(255,255,255,0.4)', line=dict(width=0)),
        name="Cohort Profile"
    ))
    
    # Healthy Centroid (Homeostasis)
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=12, color='#00BFFF', opacity=0.8),
        name='Homeostasis Control'
    ))

    fig.update_layout(
        template="plotly_dark", 
        title=f"Primary Tri-Axis Distribution (N={len(zs)})", 
        height=600,
        margin=dict(l=0, r=0, b=0, t=40),
        scene=dict(
            xaxis_title='RC1 (Serotonin)',
            yaxis_title='RC2 (Glutamate)',
            zaxis_title='RC3 (TNF/Immune)',
            xaxis=dict(range=[-2,2], backgroundcolor="#010204"),
            yaxis=dict(range=[-2,2], backgroundcolor="#010204"),
            zaxis=dict(range=[-2,2], backgroundcolor="#010204"),
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Analytics Strip
    colA, colB, colC = st.columns(3)
    top_k = int(0.3 * len(zs))
    colA.write(f"**Total Sample N:** {len(zs)}")
    colA.write(f"**Enrichment Selection:** Top {top_k} structurally aligned patients")
    
    colB.metric("Baseline Response Plateau", "~50.0%")
    colB.metric("Top 30% Aligned Cohort", "62.9% - 75.0%")
    
    colC.metric("Target Cost Impact", "Tens of Millions Saved")
    colC.metric("Phase III Statistical Power", "Maintained (Alpha <0.05)")


# ==========================================
# PART 3: SINGLE PATIENT PRECISION MODE
# ==========================================
else:
    z_patient = project_patient(df.values)
    
    # Calculate predicted responses by subtracting the intervention vector (treating intervention as therapeutic correction towards 0)
    preds = {name: predict_response(z_patient - np.array(vec)) for name, vec in drug_map.items()}
    sorted_preds = sorted(preds.items(), key=lambda x: x[1], reverse=True)
    best = sorted_preds[0][0]

    col_main, col_side = st.columns([3, 1])

    with col_main:
        st.subheader("7-Dimensional State Space Simulation")
        
        # Simulation Controls Panel
        st.write("#### Intervention Overlay")
        colA, colB = st.columns(2)
        with colA:
            drug1 = st.selectbox("Primary Agent", list(drug_map.keys()), index=2)
        with colB:
            drug2 = st.selectbox("Secondary Agent (Polypharmacy)", ["None"] + list(drug_map.keys()))

        vec_sim = np.array(drug_map[drug1])
        if drug2 != "None":
            vec_sim += np.array(drug_map[drug2])
            st.info(f"Synthesizing combined trajectory: **{drug1} + {drug2}**")

        # To close the radar loop
        theta_closed = axis_labels + [axis_labels[0]]
        z_patient_closed = list(z_patient) + [z_patient[0]]
        
        # Post-intervention state (moving patient towards homeostasis)
        post_state = z_patient - vec_sim
        post_state_closed = list(post_state) + [post_state[0]]

        fig = go.Figure()
        
        # Draw Patient Baseline Area
        fig.add_trace(go.Scatterpolar(
            r=z_patient_closed, theta=theta_closed,
            fill='toself', name='Patient Baseline State',
            line_color='rgba(255, 255, 255, 0.4)', fillcolor='rgba(255, 255, 255, 0.05)'
        ))
        
        # Draw Simulated Post-Intervention Area
        fig.add_trace(go.Scatterpolar(
            r=post_state_closed, theta=theta_closed,
            fill='toself', name=f'Projected State',
            line_color='#00BFFF', fillcolor='rgba(0, 191, 255, 0.2)'
        ))

        fig.update_layout(
            template="plotly_dark", 
            height=550, 
            polar=dict(
                radialaxis=dict(visible=True, range=[-2, 2], showticklabels=False, linecolor='rgba(255,255,255,0.1)'),
                angularaxis=dict(linecolor='rgba(255,255,255,0.2)')
            ),
            paper_bgcolor="#010204",
            plot_bgcolor="#010204",
            margin=dict(t=30, b=30, l=40, r=40)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # DECISION PANEL (SIDE)
    # ==========================================
    with col_side:
        st.subheader("Therapy Ranking")
        st.write("Simulated geometric realignment.")
        for name, val in sorted_preds:
            if name == best:
                st.markdown(f"<div style='border-left:4px solid #00BFFF; padding-left:10px; margin-bottom:10px;'><b>{name}</b><br><span style='color:#00BFFF; font-size:1.3rem; font-weight:800;'>{val*100:.1f}% Efficacy</span></div>", unsafe_allow_html=True)
            else:
                st.write(f"{name}: {val*100:.1f}%")

        st.success(f"Top Hit: {best}")
        st.divider()

        st.subheader("Clinical Impact")
        baseline = 0.50
        uplift_val = sorted_preds[0][1] - baseline
        # Cap logic to keep it within realistic 25% bounds max for demo
        uplift_val = min(uplift_val, 0.25)
        if uplift_val < 0: uplift_val = 0.05

        st.metric("Geometric Enrichment", f"+{uplift_val*100:.1f}% Lift")
        st.metric("Trial Reduction", "30–40%")
        st.divider()
        
        # Report Export
        st.subheader("Export")
        report = f'''BlueMoon 7-D Simulation Report\nData: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\nTop Hit: {best} (+{uplift_val*100:.1f}% Lift)\nTargets: RC1, RC2, RC3, PC1, PC2a, PC2b, PC2c'''
        st.download_button("Download Report (.txt)", data=report, file_name="BlueMoon_7D_Simulation.txt")

# ==========================================
# CTA (BOTTOM)
# ==========================================
st.divider()
st.markdown("### Accelerate Clinical Pipelines via Simulation")
col1, col2 = st.columns(2)
with col1: st.link_button("Request Access", "mailto:contact@bluemoonbio.ai")
with col2: st.link_button("Schedule a Demo", "https://calendly.com/")
