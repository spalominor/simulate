import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.orm import joinedload
import database.database as db
from database.models import Simulacion, Escenario, Abono, Usuario
from core.utiles import crear_tabla_amortizacion, mostrar_datos_escenario


# Dashboard
st.title("📊 SimuLate")

# Cargar datos iniciales
with db.obtener_sesion() as sesion:
    simulaciones = (
        sesion.query(Simulacion)
        .options(joinedload(Simulacion.escenarios))
        .all()
    )
    escenarios = (
            sesion.query(Escenario)
            .options(joinedload(Escenario.abonos))
            .all()
        )


if simulaciones:
    resultados = []
    resumenes = []

    for esc in escenarios:
        proyeccion = crear_tabla_amortizacion(esc)
        df_proyeccion = pd.DataFrame(proyeccion)
        df_proyeccion.columns = df_proyeccion.iloc[0]
        df_proyeccion = df_proyeccion[1:]

        df_proyeccion["ID Escenario"] = esc.id
        df_proyeccion["Escenario"] = esc.nombre

        resultados.append(df_proyeccion)
        resumenes.append({
                    "ID": esc.id,
                    "Escenario": esc.nombre,
                    "Meses": len(df_proyeccion),
                    "Capital": esc.capital,
                    "Tasa": esc.tasa,
                    "Intereses": df_proyeccion["Interés"].sum(),
                    "Proporción Intereses": (df_proyeccion["Interés"].sum() * 100) / esc.capital,
                    "Abonos Extra": df_proyeccion["Abono Extra"].sum(),
                    "Total Pagado": df_proyeccion["Cuota Fija"].sum() + df_proyeccion["Abono Extra"].sum()
            })

    # Dataframes globales
    df_grafica = pd.concat(resultados, ignore_index=True)
    df_resumen = pd.DataFrame(resumenes)

    # Barra de selección de escenarios
    escenarios_seleccionados = st.multiselect(
        "Escenarios a comparar",
        options=df_resumen["Escenario"].tolist(),
        default=df_resumen["Escenario"].tolist()
    )
    df_filtrado = df_grafica[df_grafica["Escenario"].isin(escenarios_seleccionados)]
    df_resumen_filtrado = df_resumen[df_resumen["Escenario"].isin(escenarios_seleccionados)]

    # Obtener el id del mejor escenario para buscarlo
    mejor = df_resumen_filtrado.sort_values("Proporción Intereses").iloc[0]
    mejor_id = int(mejor["ID"])

    # Buscar el escenario
    with db.obtener_sesion() as sesion:
        escenario_mejor = (
                sesion.query(Escenario)
                .options(joinedload(Escenario.abonos))
                .filter_by(id=mejor_id).first()
            )
    
    # Mostrar el dashboard con los indicadores del escenario
    proyeccion_mejor = df_filtrado[df_filtrado["ID Escenario"] == mejor_id]
    mostrar_datos_escenario(escenario_mejor, proyeccion_mejor)


    # Graficar
    st.subheader("Curva de capital pendiente")

    fig = px.line(
        df_filtrado,
        x="Mes",
        y="Saldo Final",
        color="Escenario",
        markers=True
    )
    fig.update_layout(xaxis_title="Mes", yaxis_title="Capital pendiente")
    st.plotly_chart(fig, width="stretch")
    st.subheader("Resumen comparativo")

    # Tabla
    st.dataframe(
        df_resumen_filtrado.sort_values("Proporción Intereses").style.format({
            "Capital": "${:,.0f}",
            "Tasa": "{:,.2f}%",
            "Intereses": "${:,.0f}",
            "Proporción Intereses": "{:,.2f}%",
            "Abonos Extra": "${:,.0f}",
            "Total Pagado": "${:,.0f}"
        }), width="stretch", hide_index=True, row_height=50)


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
    