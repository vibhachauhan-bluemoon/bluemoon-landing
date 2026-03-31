import streamlit as st

st.set_page_config(page_title="BlueMoonBio | Patient Portal", page_icon="🌙", layout="wide")
st.markdown("<style>.stApp { background-color: #030407; font-family: 'Inter', sans-serif; color: #fff; }</style>", unsafe_allow_html=True)

st.title("When someone you love is struggling, you deserve more than guesswork.")

col1, col2 = st.columns([2, 1])

with col1:
    st.write("""
**BlueMoonBio** illuminates the biology behind mood, anxiety, and treatment response—so families and clinicians can move beyond trial‑and‑error toward more informed care decisions.

We translate complex genetic, immune, hormonal, and neural signals into clear, human‑readable insights that respect dignity and context.
""")

    st.subheader("A biological discovery engine for mental health")
    st.write("""
Our platform integrates multi‑omic signals — genetics, inflammation, hormones, neural pathways, and lived experience — into a structured, explainable view of what may be driving symptoms.
""")

with col2:
    try:
        st.image("assets/hero_layers.svg", caption="Layered biological context", use_column_width=True)
    except:
        pass
    st.info("""
**Biological Insight Snapshot**
- Genetic contributors  
- Immune & inflammatory stress  
- Hormonal & metabolic context  
- Neural circuit patterns  
""")
