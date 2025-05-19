
import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Shiny Embedded", layout="wide")

st.title("Anatomeshr Shiny App")

# Change this URL to your actual Shiny server URL
shiny_url = "https://anatomeshr.serve.scilifelab.se/app/anatomeshr"

html(f"""
<iframe src="{shiny_url}" width="100%" height="800" style="border:none;"></iframe>
""", height=800)


