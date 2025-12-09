import streamlit as st
from utils import get_leaderbord
import pandas as pd

leadeboard_data = get_leaderbord()

leaderboard = pd.DataFrame(
    leadeboard_data,
    index=["🥇", "🥈", "🥉"] + [i for i in range(4, len(leadeboard_data)+1)]
)
leaderboard.columns = ["Joueur", "Score"]
st.dataframe(leaderboard)