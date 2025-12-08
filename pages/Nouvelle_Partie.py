import streamlit as st
from utils import get_user_list
from src.game import CricketGame

user_list = get_user_list()

if "game" not in st.session_state:
    st.session_state.game_started = False

placeholder = st.empty()

if not st.session_state.game_started:
    with placeholder.container():
        select_players = st.multiselect("Sélectionnez les joueurs:",
                             options=user_list,
                             max_selections=6)
        start_button = st.button("Commencer la partie", type="primary")

    if start_button and len(select_players) >= 2:
        st.session_state.game = CricketGame(select_players)
        st.session_state.game_started = True
        st.rerun()
    elif start_button:
        st.write("Il faut au moins deux joueurs pour commencer la partie.")

else:
    game = st.session_state.game
    state_df, points_df = game.get_df_to_print()

    st.dataframe(
        state_df,
        column_config={
            name: st.column_config.ImageColumn(name)
            for name in user_list
        },
    )

    col20, col19, col18, col17, col16, col15, col25 = st.columns(7)

    with col20:
        st.button("20", type="secondary", width="stretch", on_click=game.throw, args=["20", 1])
    with col19:
        st.button("19", type="secondary", width="stretch", on_click=game.throw, args=["19", 1])
    with col18:
        st.button("18", type="secondary", width="stretch", on_click=game.throw, args=["18", 1])
    with col17:
        st.button("17", type="secondary", width="stretch", on_click=game.throw, args=["17", 1])
    with col16:
        st.button("16", type="secondary", width="stretch", on_click=game.throw, args=["16", 1])
    with col15:
        st.button("15", type="secondary", width="stretch", on_click=game.throw, args=["15", 1])
    with col25:
        st.button("25", type="secondary", width="stretch", on_click=game.throw, args=["25", 1])

    double, triple, ret = st.columns(3)

    with double:
        st.button("Double", type="secondary", width="stretch")
    with triple:
        st.button("Triple", type="secondary", width="stretch")
    with ret:
        st.button("Retour", type="secondary", width="stretch", on_click=game.return_to_last_state)
