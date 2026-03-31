import streamlit as st

st.set_page_config(page_title="Insight Modules | BlueMoonBio", layout="wide")
st.markdown("<style>.stApp { background-color: #030407; font-family: 'Inter', sans-serif; color: #fff; }</style>", unsafe_allow_html=True)

st.title("Biological Insight Modules")
st.write("A structured view of potential contributors to mood and anxiety.")

col1, col2 = st.columns([1.4, 1])

with col1:
    modules = {
        "Genetic Contributors": "Variants associated with mood, anxiety, and treatment response.",
        "Inflammation & Immune Signals": "Patterns of immune activation and inflammatory stress.",
        "Hormonal & Metabolic Factors": "Context related to energy, sleep, and mood stability.",
        "Neural Circuit Patterns": "Pathways involved in emotional regulation and stress response.",
        "Treatment Response Indicators": "Clues that may inform medication sensitivity or side‑effect risk.",
        "Context & Lived Experience": "Biology interpreted in human context, not isolation."
    }

    for title, desc in modules.items():
        st.markdown(f"#### {title}")
        st.write(desc)
        st.divider()

with col2:
    try:
        st.image("assets/modules_grid.svg", caption="Insight modules as a layered grid", use_column_width=True)
    except:
        pass
