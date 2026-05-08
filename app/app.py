import streamlit as st
import database.database as db



# Cargar o iniciar la base de datos
db.iniciar_db()

# Configuración de páginas
st.set_page_config(page_title="SimuLate", page_icon=":material/money:", layout="wide")


principal = st.Page("pages/dashboard.py", title="Simulación", icon=":material/home:")
alternativas = st.Page("pages/alternativas.py", title="Alternativas", icon=":material/add_circle:")
abonos = st.Page("pages/abonos.py", title="Abonos", icon=":material/add_circle:")
calculadora = st.Page("pages/calculadora.py", title="Caluladora", icon=":material/edit:")

pg = st.navigation({
    "Dashboard": [principal],
    "Crear": [alternativas, abonos],
    "Ayuda": [calculadora]
})

pg.run()