import streamlit as st
from utils import get_leaderbord
import pandas as pd

st.set_page_config(
    page_title="Classement",
    page_icon="🏅",
)

leadeboard_data = get_leaderbord()

leaderboard = pd.DataFrame(
    leadeboard_data,
    index=["🥇", "🥈", "🥉"] + [str(i) for i in range(4, len(leadeboard_data)+1)]
)
leaderboard.columns = ["Joueur", "Score"]
st.dataframe(leaderboard)