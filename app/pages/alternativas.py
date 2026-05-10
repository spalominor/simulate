import streamlit as st
import database.database as db
from core import utiles
from database.models import Simulacion, Escenario, Usuario



# Cargar datos básicos
with db.obtener_sesion() as sesion:
    simulaciones = sesion.query(Simulacion).all()
    usuarios = sesion.query(Usuario).all()
    print(f"lista usuarios{usuarios}")


st.title("Constructor de Alternativas")

with st.expander("Crear Alternativa", expanded=True):
    with st.form("form_escenario", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre del escenario", help="Nombre personalizado")
            tipo = st.selectbox("Tipo", options=["Préstamo", "Inversión"])
            tasa = st.number_input("Tasa de Interés", min_value=0.0, step=0.1)
            simulacion = st.selectbox("Simulación", options=simulaciones)
        
        with col2:
            capital = st.number_input("Capital Inicial", min_value=0, step=500000)
            plazo = st.number_input("Plazo en meses", min_value=0, step=12)
            cuota = st.number_input("Valor de la cuota", step=500000)
            autor = st.selectbox("Creador", options=usuarios)

        guardar = st.form_submit_button("Guardar Alternativa", type="primary", width="stretch")

        if guardar:
            if nombre:
                with db.obtener_sesion() as sesion:
                    admin = sesion.merge(autor)
                    simulacion = sesion.merge(simulacion)
                    escenario = Escenario(
                        nombre=nombre,
                        tipo=tipo,
                        capital=capital,
                        tasa=tasa,
                        plazo=plazo,
                        cuota=cuota,
                        creado_por=admin.id
                    )
                    sesion.add(escenario)
                    simulacion.escenarios.append(escenario)
                    sesion.commit()
                    sesion.refresh(escenario)
                st.success("Guardado exitosamente")
            else:
                st.error("Debes ingresar un nombre válido")

st.divider()
with db.obtener_sesion() as sesion:
    escenarios = sesion.query(Escenario).all()

    if escenarios:
        utiles.mostrar_tabla_escenarios(escenarios)

    else:
        st.info("Crea primero una Alternativa")

st.divider()

if st.button("Crear un abono"):
    st.switch_page("pages/abonos.py")