import streamlit as st
from utils import get_client, get_player_list

st.set_page_config(
    page_title="Ajouter un joueur",
    page_icon="⛹️",
)

client = get_client()
player_list = get_player_list()

new_player_name = st.text_input("Nom de l'joueur", placeholder="Neuil")

if new_player_name:
    if new_player_name not in player_list:
        try:
            response = client.table("players").insert(
                [{"player_name": new_player_name}], count="None"
            ).execute()
            st.success("Joueur ajouté avec succès.")
        except Exception as e:
            if "Failing row contains" in str(e):
                st.error("Le nom d'utilisateur ne peut pas être plus long que 25 caractères.")
            else:
                st.error(e)

    else:
        st.error("Ce joueur existe déjà.")
