import streamlit as st


options = ["Pomme", "Banane", "Cerise", "Orange"]
selection = st.multiselect("Choisis tes fruits préférés :", options)
st.write("Tu as sélectionné :", selection)