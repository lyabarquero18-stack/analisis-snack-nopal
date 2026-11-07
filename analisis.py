# analisis.py
import numpy as np, pandas as pd
from criterios import RTCA

def ufc_g(colonias, dilucion_exp, vol_ml=0.1):
    return colonias / vol_ml * 10**dilucion_exp

def validar_controles(placas):
    """Si un control tiene crecimiento, la corrida se elimina (criterio de eliminación)."""
    ctrl = placas[placas.tratamiento == "CONTROL"]
    malos = ctrl[ctrl.colonias.fillna(0) > 0]
    return malos.empty, malos

def reportar_ecoli(sub):
    """Usa la dilución más baja con colonias típicas; marca si el recuento es estimado."""
    con = sub[sub.colonias > 0].sort_values("dilucion_exp")
    if con.empty:
        return {"UFC_g": "< 10^2", "log10": np.nan, "cumple_limite": True, "nota": ""}
    f = con.iloc[0]
    v = ufc_g(f.colonias, f.dilucion_exp)
    nota = "estimado (<30 colonias)" if f.colonias < 30 else ""
    return {"UFC_g": v, "log10": np.log10(v),
            "cumple_limite": v <= RTCA["ecoli_registro_ufc_g"], "nota": nota}

def reportar_salmonella(sub):
    """Presuntivo: si alguna réplica tiene colonias sospechosas, se reporta presencia presuntiva."""
    hay = (sub.colonias.fillna(0) > 0).any()
    return {"resultado": "Presencia presuntiva/25 g" if hay else "Ausencia/25 g",
            "cumple_limite": not hay}

def delta_masa(p0, pt):
    return (p0 - pt) / p0 * 100
