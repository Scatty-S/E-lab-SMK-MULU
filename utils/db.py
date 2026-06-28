import streamlit as st
from supabase import create_client, Client

# Masukkan URL dan API Key Supabase yang kamu salin tadi di sini
SUPABASE_URL = "https://bxguthzqmpizqfwiczww.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ4Z3V0aHpxbXBpenFmd2ljend3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0MTE1NzgsImV4cCI6MjA5Nzk4NzU3OH0.Eao7akBVGbsg0-gP4EO-PXlqe_ouHvXxRyuQknAPr5U"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Buat instansinya untuk dipanggil di file lain
supabase = init_connection()