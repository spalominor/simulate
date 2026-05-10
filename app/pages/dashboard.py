import streamlit as st
import pandas as pd
import plotly.express as px
import database.database as db
from database.models import Simulacion, Escenario, Abono, Usuario
from core.amortizacion import calcular_tabla_amortizacion


# Dashboard
st.title("📊 SimuLate")

# Cargar datos iniciales
with db.obtener_sesion() as sesion:
    simulaciones = sesion.query(Simulacion).all()
    escenarios = sesion.query(Escenario).all()

    if not sesion.query(Usuario).filter_by(nombre="sam"):
        admin = Usuario(
            name="sam",
            email="sam@spalominor.com"
        )
        sesion.add(admin)
        sesion.commit()
        sesion.refresh(admin)


if simulaciones:
    try:
        resultados = []
        df_grafica = pd.DataFrame()

        for nombre, d in escenarios:
            df_res, int_tot, meses = calcular_tabla_amortizacion(d['saldo'], d['tasa'], d['plazo'], d['cuota'], d['abonos'])
            resultados.append({"Alt": nombre, "Meses": meses, "Interés": int_tot, "Total": int_tot + d['saldo']})
            
            temp_df = df_res[['Mes', 'Saldo']].copy()
            temp_df['Escenario'] = nombre
            df_grafica = pd.concat([df_grafica, temp_df])

        mejor = min(resultados, key=lambda x: x['Interés'])
        base = resultados[0] # Asumiendo el primero como base
        ahorro = base['Interés'] - mejor['Interés']

        c1, c2, c3 = st.columns(3)
        c1.metric("Escenarios Activos", len(resultados))
        c2.metric("Mejor Alternativa", mejor['Alt'])
        c3.metric("Ahorro Proyectado", f"${ahorro:,.0f}", delta=f"{base['Meses'] - mejor['Meses']} meses menos")

        # --- BLOQUE 2: CURVA DE CAPITAL ---
        st.subheader("Evolución del Saldo")
        fig = px.line(df_grafica, x="Mes", y="Saldo", color="Escenario", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # --- BLOQUE 3: TABLA Y RANKING ---
        st.subheader("Tabla Comparativa")
        res_df = pd.DataFrame(resultados)
        st.dataframe(res_df.style.highlight_min(subset=['Interés', 'Meses'], color='#1e4d2b'), use_container_width=True)
    
    except Exception as e:
        print(f"{e} - Dashboard")
    finally:
        st.info("La simulación aún está vacía")
        st.divider()
        if st.button("Crear Escenario",
                    width="stretch",
                    help="Debes llenar la información de tu préstamo"):
            st.switch_page("pages/alternativas.py")

else:
    st.info("👋 ¡Bienvenido! No tienes simulaciones para mostrar aún")
    
    with st.expander("Crear simulación", expanded=True):
        with st.form("form_simulacion", clear_on_submit=True):
            col1, col2 = st.columns([1, 4])

            with col1:
                nombre = st.text_input("Nombre de la simulación")
                autor = st.text_input("Creador")
                guardar = st.form_submit_button("Crear simulación")

            with col2:
                st.caption("Selecciona los escenarios ya creados")

                # Crear una variable en la caché
                if "escenarios_seleccionados" not in st.session_state:
                    st.session_state.escenarios_seleccionados = []

                for esc in escenarios:
                    seleccionado = st.checkbox(f"{esc.id} - {esc.nombre}", key=esc.id)

                    if seleccionado:
                        if esc.id not in st.session_state.escenarios_seleccionados:
                            st.session_state.escenarios_seleccionados.append(esc.id)

            if guardar:
                if nombre:
                    with db.obtener_sesion() as sesion:
                        creador = sesion.query(Usuario).filter_by(nombre=autor).first()
                        if not creador:
                            creador = Usuario(nombre=autor)

                        simulacion = Simulacion(
                            nombre=nombre,
                            creado_por=creador.id
                        )
                        sesion.add(simulacion)
                        sesion.add(creador)
                        sesion.commit()
                        sesion.refresh(simulacion)
                        sesion.refresh(creador)
                        print(st.session_state.escenarios_seleccionados)

        

        st.divider()
        if st.button("Crear Escenario",
                    width="stretch",
                    help="Debes llenar la información de tu préstamo"):
            st.switch_page("pages/alternativas.py")
    