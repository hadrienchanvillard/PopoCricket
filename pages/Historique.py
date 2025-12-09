import streamlit as st
from src.game import CricketGame
from utils import get_client
from datetime import datetime

st.set_page_config(
    page_title="Historique",
    page_icon="🎮",
)

client = get_client()
games = (
    client
    .table("games")
    .select("id", "created_at")
    .eq("is_finished", True)
    .order("created_at", desc=True)
    .limit(10)
    .execute()
)

for game_info in games.data:

    game_id = game_info["id"]
    date = datetime.fromisoformat(game_info['created_at'])

    st.write(f"Date: {date.strftime('%d/%m/%Y %H:%M')}")

    game = CricketGame(game_id=game_id)
    state_df, points_df = game.get_df_to_print()
    st.dataframe(
        state_df,
        column_config={
            name: st.column_config.ImageColumn(name)
            for name in game.player_list
        },
    )
    st.dataframe(points_df, hide_index=True)