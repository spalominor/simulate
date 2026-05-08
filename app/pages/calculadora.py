import streamlit as st
import numpy_financial as npf

st.title("🧮 Calculadora Financiera")

tab1, tab2, tab3 = st.tabs(["Calcular Tasa", "Calcular Cuota", "Inferir de Extracto"])

with tab1:
    s = st.number_input("Saldo Actual", value=100000000)
    c = st.number_input("Cuota Mensual", value=2000000)
    p = st.number_input("Meses Restantes", value=72)
    if st.button("Calcular Tasa Real"):
        rate = npf.rate(p, -c, s, 0)
        ea = ((1 + rate)**12 - 1) * 100
        st.metric("Tasa E.A. Inferida", f"{ea:.2f}%")

with tab3:
    st.info("Usa los datos de tu último extracto para saber tu tasa real.")
    s_ant = st.number_input("Saldo mes anterior", value=50000000)
    int_pagado = st.number_input("Intereses pagados este mes", value=500000)
    if st.button("Analizar Extracto"):
        t_mensual = (int_pagado / s_ant)
        ea = ((1 + t_mensual)**12 - 1) * 100
        st.success(f"Tu tasa real actual es {ea:.2f}% E.A.")