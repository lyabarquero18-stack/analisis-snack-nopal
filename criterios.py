# criterios.py
RTCA = {
    "subgrupo": "4.2.2 Frutas y vegetales desecados o deshidratados (tipo B)",
    "ecoli_registro_ufc_g": 100,          # 10^2
    "ecoli_vigilancia": {"n": 5, "c": 1, "m": 100, "M": 1000},
    "salmonella": "Ausencia/25 g",
    "salmonella_vigilancia": {"n": 5, "c": 0},
}

# Ajusta con lo que definiste en tu manual
INCLUSION = {
    "grosor_mm": (3, 5),
    "temp_deshidratacion_C": (55, 60),
    "temp_almacenamiento_C": {4: (2, 6), 28: (26, 30)},
}
EXCLUSION = ["moho visible antes de procesar", "zonas negras o blandas",
             "olor anormal", "daño importante"]
ELIMINACION = ["crecimiento en control de esterilidad",
               "crecimiento en control de diluyente",
               "muestra perdida o sin etiqueta"]
