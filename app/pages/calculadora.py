import numpy_financial as npf
import streamlit as st
from database.models import Escenario
from core.utiles import formato_moneda, mostrar_proyeccion_escenario


st.title("🧮 Calculadora Financiera")

tab1, tab2, tab3, tab4 = st.tabs(["Calcular Tasa", "Calcular Cuota", "Conversión de Tasas", "Inferir de Extracto"])

with tab1:
    s = st.number_input("Saldo Actual", value=100000000, step=10000000, help="Pasa de 10M")
    st.write(f"Selección actual: {formato_moneda(s)}")
    c = st.number_input("Cuota Mensual", value=2000000, step=500000, help="Paso de 500m")
    st.write(f"Selección actual: {formato_moneda(c)}")
    p = st.number_input("Meses Restantes", value=72)

    if st.button("Calcular Tasa Real"):
        st.divider()
        rate = npf.rate(p, -c, s, 0)
        ea = ((1 + rate)**12 - 1) * 100

        escenario = Escenario(
            nombre="Cálculo de Tasa",
            capital=s,
            cuota=c,
            tasa=ea,
            plazo=p
        )
        mostrar_proyeccion_escenario(escenario)


with tab2:
    st.subheader("Cálculo de Cuota")
    st.text("Definir Préstamo")
    capital = st.number_input("Monto del Crédito", value=50000000, step=5000000)
    st.write(f"Selección actual: {formato_moneda(capital)}")
    plazo_meses = st.number_input("Plazo (meses)", value=72, step=12)
    st.write(f"{plazo_meses // 12} años")
    tasa = st.number_input("Tasa de Interés E.A.", value=12.0, min_value=0.0, step=0.5)

    if st.button("Calcular Cuota"):
        tem = ((1 + tasa/100)**(1/12) - 1) * 100
        # npf.pmt pide (tasa_decimal, nper, pv)
        cuota = npf.pmt(tem / 100, plazo_meses, -capital)
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Cuota Mensual Estímada", formato_moneda(cuota), width="stretch")
            with col2:
                st.caption("💡 **Tip de Salud Financiera**")
                ingreso_req = cuota / 0.35
                st.write("Basado en la regla del límite del 35% del endeudamiendo")
                st.write(f"Para pagar esta cuota cómodamente, tus ingresos mensuales deberían ser al menos de **{formato_moneda(ingreso_req)}**.")

    # Opción para ver la proyección completa con el botón
    if 'cuota' in locals():
        escenario_cuota = Escenario(
            nombre="Cálculo de Cuota",
            capital=capital,
            cuota=cuota,
            tasa=tasa,
            plazo=plazo_meses
        )
        mostrar_proyeccion_escenario(escenario_cuota)


with tab3:
    st.subheader("Conversión de Tasas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("Conversor de Tasas")
        tipo_conversion = st.radio(
            "Selecciona el sentido de la conversión:",
            ["Mensual (TEM) a Anual (TEA)", "Anual (TEA) a Mensual (TEM)"]
        )
        
        tasa_input = st.number_input("Tasa (%)", value=2.00 if "Mensual" in tipo_conversion else 25.0, step=1.00)
        
        if "Anual (TEA) a Mensual (TEM)" in tipo_conversion:
            # E.A. a TEM: ((1 + i)^(1/12)) - 1
            tasa_convertida = ((1 + tasa_input/100)**(1/12) - 1) * 100
            st.info(f"Tasa Mensual equivalente: **{tasa_convertida:.4f}%**")
        else:
            # TEM a E.A.: ((1 + i)^12) - 1
            tasa_convertida = ((1 + tasa_input/100)**12 - 1) * 100
            st.info(f"Tasa E.A. equivalente: **{tasa_convertida:.2f}%**")


with tab4:
    st.info("Usa los datos de tu último extracto para saber tu tasa real.")
    s_ant = st.number_input("Saldo mes anterior", value=50000000, step=10000000)
    st.write(f"Selección actual: {formato_moneda(s_ant)}")
    int_pagado = st.number_input("Intereses pagados este mes", value=500000, step=500000)
    st.write(f"Selección actual: {formato_moneda(int_pagado)}")
    if st.button("Analizar Extracto"):
        t_mensual = (int_pagado / s_ant)
        ea = ((1 + t_mensual)**12 - 1) * 100
        st.success(f"Tu tasa real actual es {ea:.2f}% E.A.")