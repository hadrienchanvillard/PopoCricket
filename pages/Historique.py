import streamlit as st
from src.game import CricketGame
from utils import get_client
from datetime import datetime

st.set_page_config(
    page_title="Historique",
    page_icon="🎮",
)

client = get_client()
matches = (
    client
    .table("matches")
    .select("id", "created_at")
    .eq("is_finished", True)
    .order("created_at", desc=True)
    .limit(10)
    .execute()
)

for match_info in matches.data:

    match = match_info["id"]
    date = datetime.fromisoformat(match_info['created_at'])

    st.write(f"Date: {date.strftime('%d/%m/%Y %H:%M')}")

    match = CricketGame(match_id=match)
    state_df, points_df = match.get_df_to_print()
    st.dataframe(
        state_df,
        column_config={
            player: st.column_config.ImageColumn(player)
            for player in match.player_list
        },
    )
    st.dataframe(points_df, hide_index=True)

    st.markdown(match.get_ranking_to_print(for_history=True), unsafe_allow_html=True)