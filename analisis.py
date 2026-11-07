# analisis.py
import numpy as np
import pandas as pd
from criterios import RTCA

RANGO_CONTABLE = (25, 250)   # colonias por placa para un conteo confiable
VOL_ML = 0.1                 # mL sembrados por placa
SI = ["si", "sí", "s", "1", "true"]

def preparar_placas(df, morf=None):
    """Separa 'colonias' en número (n) y estado; une la morfología (columna 'tipica')."""
    df = df.copy()
    txt = df["colonias"].astype(str).str.strip()
    df["n"] = pd.to_numeric(txt, errors="coerce")
    df["estado"] = np.select(
        [df.n.notna(), txt.str.upper() == "TNTC", txt.isin(["nan", ""])],
        ["contado", "TNTC", "sin_dato"], default="no_confiable")
    df["dil"] = pd.to_numeric(df["dilucion_exp"], errors="coerce").abs()
    if morf is not None:
        m = morf.copy()
        m["dil"] = pd.to_numeric(m["dilucion_exp"], errors="coerce").abs()
        m = m.drop(columns="dilucion_exp")
        df = df.merge(m, on=["medio", "tratamiento", "replica", "dil"], how="left")
    else:
        df["tipica"] = np.nan
    return df

def validar_controles(df):
    """Un control con colonias o TNTC invalida la corrida (criterio de eliminación)."""
    ctrl = df[df.tratamiento == "CONTROL"]
    malos = ctrl[(ctrl.n.fillna(0) > 0) | (ctrl.estado == "TNTC")]
    return malos.empty, malos

def estimar_conteo(sub):
    """UFC/g a partir de la placa más confiable (rango 25-250; si no hay, la de menor dilución con colonias)."""
    lo, hi = RANGO_CONTABLE
    cont = sub[sub.estado == "contado"]
    ok = cont[(cont.n >= lo) & (cont.n <= hi)].sort_values("dil")
    if not ok.empty:
        f, nota = ok.iloc[0], ""
    else:
        con = cont[cont.n > 0].sort_values("dil")
        if con.empty:
            if (sub.estado == "TNTC").any():
                v = hi / VOL_ML * 10 ** sub.dil.max()
                return {"UFC_g": np.nan, "reporte": f"> {v:.1e}",
                        "nota": "TNTC en todas las placas leídas (valor mínimo)"}
            return {"UFC_g": np.nan, "reporte": "no evaluable", "nota": "sin placas confiables"}
        f = con.iloc[0]
        nota = f"estimado (< {lo} colonias en la placa)" if f.n < lo else f"estimado (> {hi} colonias)"
    v = f.n / VOL_ML * 10 ** f.dil
    return {"UFC_g": v, "reporte": f"{v:.2e}", "nota": nota}

def reportar_ecoli(sub):
    """E. coli presuntivo en EMB: solo cuentan colonias típicas (centro oscuro, brillo verde metálico)."""
    if sub["tipica"].isna().all():
        return {"reporte": "Sin evaluar (falta morfología)", "cumple_limite": None, "nota": ""}
    tipicas = sub["tipica"].astype(str).str.strip().str.lower().isin(SI)
    if not tipicas.any():
        return {"reporte": "< 10^2 UFC/g (sin colonias típicas)", "cumple_limite": True,
                "nota": "presuntivo; el crecimiento abundante pudo enmascarar colonias típicas"}
    return {"reporte": "Hay colonias típicas: recontar solo las típicas y recalcular",
            "cumple_limite": None, "nota": ""}

def reportar_salmonella(sub):
    """Presuntivo: colonias sospechosas en SS. Requiere confirmación bioquímica (TSI, LIA, urea)."""
    if sub["tipica"].isna().all():
        return {"resultado": "Sin evaluar (falta morfología)", "cumple_limite": None}
    hay = sub["tipica"].astype(str).str.strip().str.lower().isin(SI).any()
    if hay:
        return {"resultado": "Presencia presuntiva/25 g (pendiente de confirmación)", "cumple_limite": False}
    return {"resultado": "Ausencia/25 g", "cumple_limite": True}

def delta_masa(p0, pt):
    return (p0 - pt) / p0 * 100
