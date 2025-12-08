import streamlit as st
from utils import get_client, get_user_list

st.set_page_config(
    page_title="Ajouter un utilisateur",
    page_icon="⛹️",
)

client = get_client()
user_list = get_user_list()

new_user_name = st.text_input("Nom de l'utilisateur", placeholder="Neuil")

if new_user_name:
    if new_user_name not in user_list:
        try:
            response = client.table("users").insert(
                [{"user_name": new_user_name}], count="None"
            ).execute()
            st.success("Joueur ajouté avec succès.")
        except Exception as e:
            if "Failing row contains" in str(e):
                st.error("Le nom d'utilisateur ne peut pas être plus long que 25 caractères.")
            else:
                st.error(e)

    else:
        st.error("Ce joueur existe déjà.")
