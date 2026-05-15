import streamlit as st
import pandas as pd

from database.models import Escenario

def mostrar_tabla_escenarios(escenarios):
    st.subheader("📋 Escenarios Disponibles")

    # Cabecera de la tabla
    # Ajustamos los anchos de columna: Nombre, Tipo, Capital, Tasa, Plazo, Cuota, Acción
    cols = st.columns([2, 1.5, 1.5, 1, 1, 1.5, 1.5])
    fields = ["Nombre", "Tipo", "Capital", "Tasa", "Plazo", "Cuota", "Acción"]
    
    for col, field in zip(cols, fields):
        col.markdown(f"**{field}**")
    
    st.divider()

    # Filas de datos
    for escenario in escenarios:
        with st.container():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 1.5, 1.5, 1, 1, 1.5, 1.5])
            
            c1.text(escenario.nombre)
            c2.caption(escenario.tipo)
            c3.text(f"${escenario.capital:,.2f}")
            c4.text(f"{escenario.tasa}%")
            c5.text(f"{escenario.plazo} m")
            c6.text(f"${escenario.cuota:,.2f}")
            
            # Botón de acción con una clave única por escenario
            if c7.button(":material/add_circle: Abono", key=f"abono_{escenario.id}"):
                st.switch_page("pages/abonos.py")


def crear_tabla_amortizacion(escenario: Escenario):
    """
    Crea una tabla de amortización dado un escenario y sus abonos.
    ["Mes", "Saldo Inicial", "Cuota Fija", "Interés", "Abono Extra", "Amortización Total", "Saldo Final"]
    Args:
        - escenario: El objeto tipo Escenario

    Return:
        - proyeccion: Lista de listas, 7 cols, n meses filas
    """
    # Preparar datos base
    saldo = escenario.capital
    # TEA convertir a TEM = (1 + TEA) (1/12) - 1
    tasa_mensual = -1 + ((escenario.tasa / 100) + 1)**(1/12)
    cuota_fija = escenario.cuota
    dict_abonos = {a.mes: a.monto for a in escenario.abonos}
    
    proyeccion = []
    proyeccion.append([
            "Mes",
            "Saldo Inicial",
            "Cuota Fija",
            "Interés",
            "Abono Extra",
            "Amortización Total",
            "Saldo Final"
        ])
    
    for mes in range(1, escenario.plazo + 1):
        if saldo <= 0: break

        interes = saldo * tasa_mensual
        abono_extra = dict_abonos.get(mes, 0)
        
        # Aporte a capital normal es Cuota - Interés
        amortizacion_base = cuota_fija - interes
        
        # La amortización total incluye el abono extra
        amortizacion_total = amortizacion_base + abono_extra
        
        # Evitar que el saldo sea negativo
        if amortizacion_total > saldo:
            amortizacion_total = saldo
            abono_extra = max(0, saldo - amortizacion_base)
            
        saldo_final = saldo - amortizacion_total
        
        proyeccion.append([
            mes,
            saldo,
            cuota_fija,
            interes,
            abono_extra,
            amortizacion_total,
            max(0, saldo_final)
        ])

        saldo = saldo_final

    return proyeccion

def mostrar_proyeccion_escenario(escenario: Escenario):
    proyeccion = crear_tabla_amortizacion(escenario)
    if proyeccion is None:
        return st.error("La proyección está vacía")
    df = pd.DataFrame(proyeccion)
    df.columns = df.iloc[0]
    df = df[1:]

    mostrar_datos_escenario(escenario, df)

    # Tabla
    def resaltar_abonos(row):
        return ['background-color: #185c13' if row['Abono Extra'] > 0 else '' for _ in row]

    st.dataframe(
        df.style.format({
            "Saldo Inicial": "${:,.0f}",
            "Cuota Fija": "${:,.0f}",
            "Interés": "${:,.0f}",
            "Abono Extra": "${:,.0f}",
            "Amortización Total": "${:,.0f}",
            "Saldo Final": "${:,.0f}"
        }).apply(resaltar_abonos, axis=1),
        width="stretch",
        hide_index=True
    )


def formato_moneda(valor):
    """Convierte un número a formato $1.000.000"""
    return f"${valor:,.0f}".replace(",", ".")


def mostrar_datos_escenario(escenario: Escenario, df: pd.DataFrame):
    """Muestra algunos indicadores importantes de un escenario"""
    tasa_mensual = -1 + ((escenario.tasa / 100) + 1)**(1/12)

    # Renderizado en Streamlit
    st.subheader(f":chart_with_upwards_trend: Proyección: {escenario.nombre}")
    print(df)
    # Titulos
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Capital Inicial", formato_moneda(escenario.capital))
    total_pagado = df["Cuota Fija"].sum() + df["Abono Extra"].sum()
    diferencia_pagado = total_pagado - escenario.capital
    c1.metric("Total pagado", formato_moneda(total_pagado), delta=formato_moneda(diferencia_pagado))

    c2.metric("Total Abonos Extra", formato_moneda(df["Abono Extra"].sum()))
    comparacion_intereses = (df["Interés"].sum() * 100) / escenario.capital
    c2.metric("Total Intereses", formato_moneda(df["Interés"].sum()), delta=f"{comparacion_intereses:,.2f}%")

    c3.metric("Plazo inicial", escenario.plazo)
    diferencia_plazo = escenario.plazo - len(df)
    c3.metric("Meses Reales", len(df), delta=diferencia_plazo)

    c4.metric("Tasa efectiva mensual", f"{tasa_mensual*100:,.2f}%")
    c4.metric("Tasa efectiva anual", f"{escenario.tasa:,.2f}%")
