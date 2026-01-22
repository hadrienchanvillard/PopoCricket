import streamlit as st
from utils import get_leaderbord
import pandas as pd

st.set_page_config(
    page_title="Classement",
    page_icon="🏅",
)

leaderboard_data = get_leaderbord()
index_leaderboard = (["🥇", "🥈", "🥉"] + [str(i) for i in range(4, len(leaderboard_data)+1)])[:len(leaderboard_data)]

leaderboard = pd.DataFrame(
    leaderboard_data,
    index=index_leaderboard,
    columns=["Joueur","Score"]
)

st.dataframe(leaderboard)