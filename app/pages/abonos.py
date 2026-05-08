import streamlit as st
import database.database as db
from database.models import Simulacion, Escenario, Abono, Usuario



# Cargar datos iniciales
with db.obtener_sesion() as sesion:
    escenarios = sesion.query(Escenario.nombre).all()


with st.expander("Crear abonos", expanded=True):
    if escenarios:
        with st.form("form_abonos", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                escenario = st.selectbox("Selecciona la alternativa", options=escenarios)


            with col2:
                periodo = st.number_input("Ingresa el mes del abono", min_value=1, step=12)
                valor = st.number_input("Ingresa el valor del abono", step=500000)


            col1, col2 = st.columns([1, 4])
            with col1:
                guardar = st.form_submit_button("Guardar Abono", type="primary")
            
            with col2:
                if st.button("Ir a Simulación", type="secondary"):
                    st.switch_page("app.py")

            if guardar:
                if escenario:
                    with db.obtener_sesion() as sesion:
                        escenario_id = sesion.query(Escenario.id).filter_by(name=escenario)
                        abono = Abono(
                            escenario_id=escenario_id,
                            mes=periodo,
                            monto=valor
                        )
                        sesion.add(abono)
                        sesion.commit()
                        sesion.refresh(abono)
                    st.success("Registrado exitosamente")
                else:
                    st.info("Debes seleccionar un escenario existente")

        
        if escenario:
            with db.obtener_sesion() as sesion:
                datos_escenario = sesion.query(Escenario).filter_by(name=escenario)
                abonos = sesion.query(Abono).filter_by(escenario_id=datos_escenario.id)

            with st.container(horizontal=True, horizontal_alignment="left"):
                st.title("Visualización en el tiempo")

            with st.container(horizontal=True, horizontal_alignment="right"):
                st.table(abonos)