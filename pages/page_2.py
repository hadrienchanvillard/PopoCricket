import streamlit as st
from st_supabase_connection import SupabaseConnection


conn = st.connection("supabase", type=SupabaseConnection)
client = conn.client
response = client.table("users").select("*").execute()

if response.data:
    st.dataframe(response.data)
else:
    st.write("Aucun utilisateur trouvé.")