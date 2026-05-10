import streamlit as st

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
            c4.text(f"{escenario.tasa * 100}%")
            c5.text(f"{escenario.plazo} m")
            c6.text(f"${escenario.cuota:,.2f}")
            
            # Botón de acción con una clave única por escenario
            if c7.button("➕ Abono", key=f"abono_{escenario.id}"):
                st.switch_page("pages/abonos.py")


def formato_moneda(valor):
    """Convierte un número a formato $1.000.000"""
    return f"{valor:,.0f} $".replace(",", ".")