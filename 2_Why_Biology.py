import streamlit as st

st.set_page_config(page_title="Why Biology Matters | BlueMoonBio", layout="wide")
st.markdown("<style>.stApp { background-color: #030407; font-family: 'Inter', sans-serif; color: #fff; }</style>", unsafe_allow_html=True)

st.title("Why Biology Matters in Mental Health")

st.write("""
Mental health shouldn’t be a maze of trial‑and‑error. Behind every symptom is a biological story:
- genes that shape sensitivity  
- immune signals that amplify stress  
- hormones that shift mood  
- neural circuits that struggle to reset  

BlueMoonBio brings these layers together so the question becomes:
**“What might be driving this, and where could we focus first?”**
""")

st.subheader("From fragments → to patterns → toward action")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("### Scattered data, unclear meaning")
    st.write("Lab results, history, and genetics sit in silos.")

with col2:
    st.write("### Layered biological context")
    st.write("We integrate multi‑omic signals into a coherent picture.")

with col3:
    st.write("### Insights that guide conversations")
    st.write("Supporting care decisions with clarity and dignity.")
