import streamlit as st
import database.database as db
from core.utiles import formato_moneda
from database.models import Simulacion, Escenario, Abono, Usuario



# Cargar datos iniciales
with db.obtener_sesion() as sesion:
    escenarios = sesion.query(Escenario).all()


with st.expander("Crear abonos", expanded=True):
    if escenarios:
        with st.form("form_abonos"):
            col1, col2 = st.columns(2)

            with col1:
                escenario = st.selectbox("Selecciona la alternativa", options=escenarios)
                if escenario:
                    st.text(f"Plazo: {escenario.plazo} meses")
                    st.text(f"Capital: {formato_moneda(escenario.capital)}")


            with col2:
                periodo = st.number_input("Ingresa el mes del abono", min_value=1, step=12)
                valor = st.number_input("Ingresa el valor del abono", step=500000)

            guardar = st.form_submit_button("Guardar Abono", type="primary", width="stretch")
            

            if guardar:
                if escenario:
                    with db.obtener_sesion() as sesion:
                        escenario = sesion.query(Escenario).filter_by(nombre=escenario).first()
                        abono = Abono(
                            escenario_id=escenario.id,
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
                datos_escenario = sesion.query(Escenario).filter_by(nombre=escenario.nombre).first()
                if datos_escenario:
                    abonos = sesion.query(Abono).filter_by(escenario_id=datos_escenario.id)

            with st.container(horizontal=True, horizontal_alignment="left"):
                st.title("Visualización en el tiempo")

            with st.container(horizontal=True, horizontal_alignment="right"):
                st.table(abonos)