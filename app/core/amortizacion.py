import pandas as pd
import numpy as np

def calcular_tabla_amortizacion(saldo, tasa_ea, plazo_max, cuota_fija, abonos_extra):
    tasa_mensual = (1 + tasa_ea/100)**(1/12) - 1
    datos = []
    saldo_actual = saldo
    total_interes = 0
    
    for mes in range(1, int(plazo_max) + 1):
        if saldo_actual <= 0: break
        
        interes_mes = saldo_actual * tasa_mensual
        abono_capital_cuota = cuota_fija - interes_mes
        extra = abonos_extra.get(mes, 0)
        
        pago_total_capital = abono_capital_cuota + extra
        
        if pago_total_capital >= saldo_actual:
            pago_total_capital = saldo_actual
            saldo_actual = 0
        else:
            saldo_actual -= pago_total_capital
            
        total_interes += interes_mes
        datos.append({
            "Mes": mes,
            "Saldo": saldo_actual,
            "Interés": interes_mes,
            "Capital": pago_total_capital,
            "Cuota": cuota_fija + extra
        })
        
    return pd.DataFrame(datos), total_interes, len(datos)