import streamlit as st
import database.database as db
from database.models import Simulacion, Escenario, Usuario



# Cargar datos básicos
with db.obtener_sesion() as sesion:
    simulaciones = sesion.query(Simulacion.id).all()


st.title("Constructor de Alternativas")

with st.expander("Crear Alternativa", expanded=True):
    with st.form("form_escenario", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre del escenario")
            tipo = st.selectbox("Tipo", options=["Préstamo", "Inversión"])
            tasa = st.number_input("Tasa de Interés", min_value=0.0, step=0.1)
            simulacion = st.selectbox("Simulación", options=[simulaciones   ])
        
        with col2:
            capital = st.number_input("Capital Inicial", min_value=0, step=500000)
            plazo = st.number_input("Plazo en meses", min_value=0, step=12)
            cuota = st.number_input("Valor de la cuota", step=500000)
            autor = st.text_input("Creador")

        guardar = st.form_submit_button("Guardar Alternativa", type="primary", width="stretch")
        

        if guardar:
            if nombre:
                with db.obtener_sesion() as sesion:
                    admin_id = sesion.query(Usuario.id).filter_by(nombre=autor)
                    escenario = Escenario(
                        nombre=nombre,
                        capital=capital,
                        tasa=tasa,
                        plazo=plazo,
                        cuota=cuota,
                        simulacion=simulacion,
                        creado_por=admin_id
                    )
                    sesion.add(escenario)
                    sesion.commit()
                    sesion.refresh(escenario)
                st.success("Guardado exitosamente")
            else:
                st.error("Debes ingresar un nombre válido")

st.divider()
with db.obtener_sesion() as sesion:
    escenarios = sesion.query(Escenario).all()

if escenarios:
    columnas = st.columns([3, 3, 1, 1, 2, 2, 2])
    campos = ["Nombre", "Capital", "Tipo", "Tasa", "Plazo", "Cuota", "Acción"]

    # Construir tabla
    for col, campo in zip(columnas, campos):
        st.write(f"**{campo}**")
    
    st.table(escenarios)

else:
    st.info("Crea primero una Alternativa")

st.divider()

if st.button("Crear un abono"):
    st.switch_page("pages/abonos.py")