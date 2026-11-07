# analisis.py
import numpy as np
import pandas as pd
from criterios import RTCA

RANGO_CONTABLE = (25, 250)   # colonias por placa para considerar un conteo confiable
VOL_ML = 0.1                 # volumen sembrado por placa

def preparar_placas(df):
    """Separa 'colonias' en número (n) y estado (contado / TNTC / no_confiable / sin_dato)."""
    df = df.copy()
    txt = df["colonias"].astype(str).str.strip()
    df["n"] = pd.to_numeric(txt, errors="coerce")
    df["estado"] = np.select(
        [df.n.notna(), txt.str.upper() == "TNTC", txt.isin(["nan", ""])],
        ["contado", "TNTC", "sin_dato"], default="no_confiable")
    df["dil"] = pd.to_numeric(df["dilucion_exp"], errors="coerce").abs()
    return df

def ufc_g(n, dil, vol=VOL_ML):
    return n / vol * 10 ** dil

def validar_controles(df):
    """Un control con colonias o TNTC invalida la corrida (criterio de eliminación)."""
    ctrl = df[df.tratamiento == "CONTROL"]
    malos = ctrl[(ctrl.n.fillna(0) > 0) | (ctrl.estado == "TNTC")]
    return malos.empty, malos

def reportar_ecoli(sub):
    """sub = placas EMB de un tratamiento (ya pasadas por preparar_placas)."""
    LIM = RTCA["ecoli_registro_ufc_g"]
    lo, hi = RANGO_CONTABLE
    cont = sub[sub.estado == "contado"]

    en_rango = cont[(cont.n >= lo) & (cont.n <= hi)].sort_values("dil")
    if not en_rango.empty:
        f, nota = en_rango.iloc[0], ""
    else:
        con_col = cont[cont.n > 0].sort_values("dil")
        if not con_col.empty:
            f = con_col.iloc[0]
            nota = f"estimado (< {lo} colonias en la placa)" if f.n < lo else f"estimado (> {hi} colonias)"
        else:
            tntc = sub[sub.estado == "TNTC"]
            if not tntc.empty:
                d = tntc.dil.max()
                v = hi / VOL_ML * 10 ** d
                return {"UFC_g": np.nan, "log10": np.log10(v), "reporte": f"> {v:.1e}",
                        "cumple_limite": False, "placa_usada": f"dil -{int(d)}",
                        "nota": "TNTC en todas las placas leídas: valor mínimo, no cuantificable"}
            if not cont.empty:
                return {"UFC_g": np.nan, "log10": np.nan, "reporte": "< 10^2",
                        "cumple_limite": True, "placa_usada": "", "nota": ""}
            return {"UFC_g": np.nan, "log10": np.nan, "reporte": "no evaluable",
                    "cumple_limite": None, "placa_usada": "", "nota": "sin placas confiables"}

    v = ufc_g(f.n, f.dil)
    return {"UFC_g": v, "log10": np.log10(v), "reporte": f"{v:.2e}",
            "cumple_limite": bool(v <= LIM), "placa_usada": f"dil -{int(f.dil)}", "nota": nota}

def reportar_salmonella(sub):
    """Presuntivo. Requiere la columna 'sospechosa' (si/no): colonias incoloras, con o sin centro negro."""
    if "sospechosa" not in sub.columns or sub["sospechosa"].isna().all():
        return {"resultado": "Sin evaluar (falta registrar morfología)", "cumple_limite": None}
    s = sub["sospechosa"].astype(str).str.strip().str.lower()
    hay = s.isin(["si", "sí", "s", "1", "true"]).any()
    return {"resultado": "Presencia presuntiva/25 g" if hay else "Ausencia/25 g",
            "cumple_limite": not hay}

def delta_masa(p0, pt):
    return (p0 - pt) / p0 * 100
