import streamlit as st
from st_supabase_connection import SupabaseConnection


@st.cache_resource
def get_client():
    conn = st.connection("supabase", type=SupabaseConnection)
    client = conn.client
    return client

def get_user_list():
    client = get_client()
    user_list = client.table("users").select("user_name").execute()

    names = [user["user_name"] for user in user_list.data]
    return names

def get_leaderbord():
    client = get_client()
    return client.table("users").select("user_name", "user_points").order("user_points", desc=True).execute().data

def get_user_id(username: str):
    client = get_client()
    result = (
        client
        .table("users")
        .select("id")
        .eq("user_name", username)
        .execute()
    )

    if result.data:
        return result.data[0]["id"]
    return None
