import streamlit as st
from utils import get_client, get_player_list

st.set_page_config(
    page_title="Ajouter un joueur",
    page_icon="⛹️",
)

client = get_client()
player_list = get_player_list()

new_player_name = st.text_input("Nom du joueur", placeholder="Neuil")

if new_player_name:
    if len(new_player_name) > 25:
        st.error("Le nom ne peut pas dépasser 25 caractères.")
    elif len(new_player_name.strip()) == 0:
        st.error("Le nom ne peut pas être vide.")
    elif new_player_name in player_list:
        st.error("Ce joueur existe déjà.")
    else:
        try:
            response = client.table("players").insert(
                [{"player_name": new_player_name.strip()}], count="None"
            ).execute()
            st.success("Joueur ajouté avec succès.")
        except Exception as e:
            st.error(f"Erreur lors de l'ajout : {e}")
