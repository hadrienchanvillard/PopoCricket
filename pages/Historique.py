import streamlit as st
from src.game import CricketGame


game = CricketGame(game_id=9)

state_df, points_df = game.get_df_to_print()

st.dataframe(
    state_df,
    column_config={
        name: st.column_config.ImageColumn(name)
        for name in game.player_list
    },
)

st.dataframe(points_df, hide_index=True)