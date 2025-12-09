import streamlit as st
from utils import get_user_list
from src.game import CricketGame


if "game" not in st.session_state:
    st.session_state.game_started  = False
    st.session_state.game_ended    = False

user_list = get_user_list()
start_game_placeholder = st.empty()
dart_url = "./assets/dart.png"

if not st.session_state.game_started:

    with start_game_placeholder.container():
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
    st.write(f"Tour: {game.get_tour_number()}/20")
    with st.container(horizontal=True):
        for i in range(game.get_num_remaining_darts()):
            st.image(dart_url, width=30)

    state_df, points_df = game.get_df_to_print()

    st.dataframe(
        state_df,
        column_config={
            name: st.column_config.ImageColumn(name)
            for name in user_list
        },
    )

    st.dataframe(points_df, hide_index=True)

    container_points_1 = st.container(horizontal=True)
    with container_points_1:
        targets = ["20", "19", "18", "17"]
        for target in targets:
            st.button(target, use_container_width=True, type="secondary", on_click=game.throw, args=[target])

    container_points_2 = st.container(horizontal=True)
    with container_points_2:
        targets = ["16", "15", "Bulle"]
        for target in targets:
            target_num = "25" if target == "Bulle" else target
            st.button(target, use_container_width=True, type="secondary", on_click=game.throw, args=[target_num])

    container_multi = st.container(horizontal=True)
    with container_multi:
        st.button("x2", type="secondary", use_container_width=True, on_click=lambda: game.set_multi(2))
        st.button("x3", type="secondary", use_container_width=True, on_click=lambda: game.set_multi(3))
        st.button("⬅️", type="secondary", use_container_width=True, on_click=game.return_to_last_state)

    st.session_state.game_ended = game.game_ended

    if st.session_state.game_ended:
        st.button("Enregistrer la partie", type="primary")