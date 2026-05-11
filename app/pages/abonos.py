import time
import streamlit as st
import database.database as db
from sqlalchemy.orm import joinedload
from core.utiles import formato_moneda, mostrar_proyeccion_escenario
from database.models import Simulacion, Escenario, Abono, Usuario



escenario_elegido = Escenario()
with db.obtener_sesion() as sesion:
    escenarios = (
            sesion.query(Escenario)
            .options(joinedload(Escenario.abonos))
            .all()
        )
    

with st.expander("Crear abonos", expanded=True):
    if escenarios:
        with st.form("form_abonos"):
            col1, col2 = st.columns(2)

            with col1:
                escenario_elegido = st.selectbox("Selecciona la alternativa", options=escenarios)
                if escenario_elegido:
                    st.text(f"Plazo: {escenario_elegido.plazo} meses")
                    st.text(f"Capital: {formato_moneda(escenario_elegido.capital)}")


            with col2:
                periodo = st.number_input("Ingresa el mes del abono", min_value=0, step=6)
                valor = st.number_input("Ingresa el valor del abono", step=500000)

            guardar = st.form_submit_button("Guardar Abono", type="primary", width="stretch")
            

            if guardar:
                if escenario_elegido:
                    with db.obtener_sesion() as sesion:
                        sesion.merge(escenario_elegido)
                        abono = Abono(
                            escenario_id=escenario_elegido.id,
                            mes=periodo,
                            monto=valor
                        )
                        sesion.add(abono)
                        sesion.commit()
                        sesion.refresh(abono)
                    notificacion = st.success("Registrado exitosamente")
                    time.sleep(2)
                    notificacion = st.empty
                    st.rerun()
                else:
                    st.info("Debes seleccionar un escenario existente")


st.divider()
with st.container():
    if escenario_elegido:
        # Recuperar el escenario con los abonos actualizados
        with db.obtener_sesion() as sesion:
            escenario_actualizado = (
                sesion.query(Escenario)
                .options(joinedload(Escenario.abonos))
                .filter_by(id=escenario_elegido.id).first()
            )
        mostrar_proyeccion_escenario(escenario_actualizado)