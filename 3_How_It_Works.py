import streamlit as st

st.set_page_config(page_title="How It Works | BlueMoonBio", layout="wide")
st.markdown("<style>.stApp { background-color: #030407; font-family: 'Inter', sans-serif; color: #fff; }</style>", unsafe_allow_html=True)

st.title("How BlueMoonBio Works")
st.write("A three‑step framework designed for clarity, not hype.")

col1, col2 = st.columns([1.6, 1])

with col1:
    st.markdown("### 1. Illuminate")
    st.write("Identify biological contributors relevant to mood, anxiety, and treatment response.")

    st.markdown("### 2. Understand")
    st.write("Reveal how genetic, immune, hormonal, and neural signals interact.")

    st.markdown("### 3. Guide")
    st.write("Translate findings into clear, human‑readable narratives that support care decisions.")

with col2:
    try:
        st.image("assets/pathway_diagram.svg", caption="Example of converging biological pathways", use_column_width=True)
    except:
        pass
