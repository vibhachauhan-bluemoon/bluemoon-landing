import streamlit as st

st.set_page_config(page_title="For Families | BlueMoonBio", layout="wide")
st.markdown("<style>.stApp { background-color: #030407; font-family: 'Inter', sans-serif; color: #fff; }</style>", unsafe_allow_html=True)

st.title("For Families")
col1, col2 = st.columns([1.4, 1])

with col1:
    st.write("""
    You’ve tried to do everything right, but the path still feels uncertain.

    BlueMoonBio focuses on explanations that are:
    - understandable  
    - non‑stigmatizing  
    - grounded in biology  

    So you can ask more precise questions and advocate with confidence.
    """)

    st.info("""
    **What families receive:**
    - A clear biological context for symptoms  
    - Insight modules that highlight potential contributors  
    - Language designed to reduce stigma  
    - A map of where to focus next  
    """)
with col2:
    try:
        st.image("assets/family_story.svg", use_column_width=True)
    except:
        pass
