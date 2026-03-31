import streamlit as st

st.set_page_config(page_title="For Clinicians | BlueMoonBio", layout="wide")
st.markdown("<style>.stApp { background-color: #030407; font-family: 'Inter', sans-serif; color: #fff; }</style>", unsafe_allow_html=True)

st.title("For Clinicians")

col1, col2 = st.columns([1.4, 1])
with col1:
    st.write("""
    You balance limited time with complex cases and incomplete data.

    BlueMoonBio is designed to fit alongside your workflow, offering structured biological context that can inform:
    - assessment  
    - referrals  
    - shared decision‑making  
    """)

    st.info("""
    **What clinicians receive:**
    - Multi‑omic context for difficult cases  
    - Explainable reasoning, not black‑box scores  
    - Pathway‑level insights  
    - Clear communication for families  
    """)

with col2:
    try:
        st.image("assets/clinician_workflow.svg", caption="Workflow Augmentation", use_column_width=True)
    except:
        pass
