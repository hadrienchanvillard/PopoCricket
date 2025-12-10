import streamlit as st
from st_supabase_connection import SupabaseConnection


@st.cache_resource
def get_client():
    conn = st.connection("supabase", type=SupabaseConnection)
    client = conn.client
    return client

def get_player_list():
    client = get_client()
    player_list = client.table("players").select("player_name").execute()

    names = [player["player_name"] for player in player_list.data]
    return names

def get_leaderbord():
    client = get_client()
    return client.table("players").select("player_name", "player_elo").order("player_elo", desc=True).execute().data

@st.cache_data
def get_player_id(player_name: str):
    client = get_client()
    result = (
        client
        .table("players")
        .select("id")
        .eq("player_name", player_name)
        .execute()
    )

    if result.data:
        return result.data[0]["id"]
    return None

def get_player_elo(player_name: str):
    client = get_client()
    result = (
        client
        .table("players")
        .select("player_elo")
        .eq("player_name", player_name)
        .execute()
    )
    if result.data:
        return float(result.data[0]["player_elo"])
    return None

@st.cache_data
def get_player_name(player_id):
    client = get_client()
    result = (
        client
        .table("players")
        .select("player_name")
        .eq("id", player_id)
        .execute()
    )

    if result.data:
        return result.data[0]["player_name"]
    return None

@st.cache_data
def get_delta_elo(match_id, player):
    client = get_client()
    result = (
        client
        .table("match_ranking")
        .select("delta_elo")
        .eq("match_id", match_id)
        .eq("player_id", get_player_id(player))
        .execute()
    )

    if result.data:
        return result.data[0]["delta_elo"]
    return None

def get_player_rank(players_ranking, player_name):
    for rank, players in players_ranking.items():
        for player_n in players:
            if player_name == player_n:
                return int(rank)
    return None

def calcul_delta_elo(players_ranking, player_list):
    result = {}

    player_elo_rank = {}
    for player in player_list:
        player_elo_rank[player] = {"elo": get_player_elo(player), "rank": get_player_rank(players_ranking, player)}

    for player in player_list:
        delta = 0
        for other_player in player_list:
            if other_player != player:
                prob = 1 / (1 + 10**((player_elo_rank[other_player]["elo"] - player_elo_rank[player]["elo"]) / 400))
                if player_elo_rank[player]["rank"] < player_elo_rank[other_player]["rank"]:
                    real = 1
                elif player_elo_rank[player]["rank"] == player_elo_rank[other_player]["rank"]:
                    real = 0.5
                else:
                    real = 0
                delta += real - prob
        delta = round((32 * delta) / (len(player_list) - 1), 2)
        result[player] = delta
    return result

