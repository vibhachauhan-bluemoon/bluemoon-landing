import streamlit as st

st.set_page_config(page_title="About | BlueMoonBio", layout="wide")
st.markdown("<style>.stApp { background-color: #030407; font-family: 'Inter', sans-serif; color: #fff; }</style>", unsafe_allow_html=True)

st.title("About BlueMoonBio")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("""
    BlueMoonBio is founded by scientists and clinicians who have spent their careers in biologics, psychiatry, and AI.

    We are guided by three commitments:
    - **Scientific rigor**  
    - **Transparent communication**  
    - **Dignity‑first design**  
    """)

    st.subheader("Our Principles")
    st.write("""
    - Multi‑omic architecture  
    - Explainable reasoning  
    - Pathway‑level interpretation  
    - Human‑centered language  
    """)

with col2:
    try:
        st.image("assets/bluemoonbio_logo.svg", use_column_width=True)
    except:
        pass
