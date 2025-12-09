import streamlit as st

st.write("Layout forcé - 4 boutons alignés")

with st.container(horizontal=True):

    st.button("test1", use_container_width=True)
    st.button("test2", use_container_width=True)
    st.button("test3", use_container_width=True)
    st.button("test4", use_container_width=True)