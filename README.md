# Análisis de calidad de un snack deshidratado de nopal con recubrimiento bioactivo

Proyecto final de cuatrimestre. Análisis por código (Python / Google Colab) de la estabilidad microbiológica y fisicoquímica de un snack deshidratado de nopal (*Opuntia ficus-indica*), con criterios codificados a partir del RTCA 67.04.50:17.

## Diseño experimental
- **Tratamientos:** T1 sin recubrimiento, T2 recubrimiento base (mucílago de nopal, pectina, glicerol), T3 recubrimiento bioactivo (base + extracto acuoso de romero).
- **Almacenamiento:** 4 °C y 28 °C; análisis en los días 0, 4, 8 y 12.
- **Microbiología (solo día 0):** recuento presuntivo de *E. coli* en agar EMB (placas por tratamiento y dilución 10⁻¹, 10⁻² y 10⁻³) y detección presuntiva de *Salmonella* spp. en agar SS (3 placas por tratamiento, dilución 10⁻¹, sembradas tras preenriquecimiento).
- **Fisicoquímico y visual:** pH, pérdida de masa, fotografías con apariencia, color, olor y deterioro visible.

## Estructura del repositorio
- `criterios.py`: criterios del RTCA y criterios de inclusión, exclusión y eliminación.
- `analisis.py`: funciones de cálculo (UFC/g, validación de controles, reporte presuntivo de *E. coli* y *Salmonella*, pérdida de masa).
- `datos/`: `placas.csv`, `morfologia.csv`, `fisicoquimico.csv`, `observaciones.csv`.
- `fotos/`: evidencia fotográfica. `snack/4C` y `snack/28C` (una foto por unidad y día, código `T1-4-D0.png`) y `placas/EMB` y `placas/SS` (una foto por placa, por ejemplo `EMB-T1-d1.png` o `SS-T1-r1.png`).
- `resultados/`: tablas y gráficas generadas por el código.
- Cuaderno de Colab: `notebook_colab.ipynb` [REVISAR: súbelo al repo desde Colab con Archivo → Guardar una copia en GitHub].

## Cómo ejecutarlo
1. Abrir el cuaderno en Google Colab.
2. Clonar el repositorio e instalar dependencias (`pip install -r requirements.txt`).
3. Ejecutar las celdas en orden: microbiología y fisicoquímico.

## Criterios codificados
- **Clasificación:** RTCA 67.04.50:17, grupo 4, subgrupo 4.2.2 (frutas y vegetales desecados o deshidratados), tipo B.
- ***E. coli*:** límite de registro 10² UFC/g.
- ***Salmonella* spp.:** ausencia en 25 g.
- **Inclusión:** láminas de 3 a 5 mm; deshidratación a 55–60 °C; temperatura de almacenamiento dentro del rango definido (4 °C y 28 °C con tolerancia).
- **Exclusión de materia prima:** moho visible, zonas negras o blandas, olor anormal, daño importante.
- **Eliminación de datos o corridas:** crecimiento en controles de esterilidad o diluyente, muestra perdida o sin etiqueta, temperatura de almacenamiento fuera de rango.

## Resultados microbiológicos (día 0, presuntivos)

tratamiento,ecoli_presuntivo,crecimiento_EMB_UFC_g,nota_crecimiento,salmonella,cumple_ecoli,cumple_salm
T1,< 10^2 UFC/g (sin colonias típicas),> 2.5e+06,TNTC en todas las placas leídas (valor mínimo),Presencia presuntiva/25 g (pendiente de confirmación),True,False
T2,< 10^2 UFC/g (sin colonias típicas),2.30e+05,estimado (< 25 colonias en la placa),Presencia presuntiva/25 g (pendiente de confirmación),True,False
T3,< 10^2 UFC/g (sin colonias típicas),1.69e+06,,Ausencia/25 g,True,True

Interpretación: hubo crecimiento abundante en todos los tratamientos, incluido el control sin recubrimiento, sin diferencias atribuibles al recubrimiento. En EMB ninguna colonia mostró el brillo verde metálico típico de *E. coli*. En SS todas las placas tuvieron colonias con puntos negros (producción de H₂S), compatibles con *Salmonella* pero también con otros géneros; sin confirmación bioquímica el resultado se reporta como presuntivo y no como positivo confirmado.
Se exploró además una medición automática del cambio de color (ΔE en el espacio CIELAB respecto al día 0), pero se descartó: el porcentaje de píxeles asignados al snack frente al fondo varió entre 26 y 100 % según la fotografía y los valores no concordaron con la evaluación visual (por ejemplo, ΔE de 28 en una muestra sin cambio de color visible). El cambio de color se reporta únicamente con la escala ordinal visual (0 a 2).

## Resultados fisicoquímicos y visuales
[REVISAR: describe las tendencias de `resultados/ph.png`, `resultados/perdida_masa_pct.png` y `resultados/deltaE_color.png`, e indica hasta qué día llegan los datos.]

## Justificación de los códigos
Se buscaron herramientas existentes antes de escribir código propio:

| Herramienta | Qué hace | Por qué no se usó como núcleo |
|---|---|---|
| [CalCFU](https://pypi.org/project/calcfu) (PyPI) | Calcula UFC según el estándar NCIMS 2400 | Está pensado para métodos de lácteos, no para el RTCA ni para agar EMB. Se usó como referencia de estructura. |
| [WeCFU](https://github.com/WeStrainGroup/WeCFU) | Cuenta colonias a partir de fotos de placas | Su filtro está orientado a colonias claras; aquí el criterio es morfológico (brillo verde metálico en EMB) y el conteo fue manual. |
| [CFUCounter](https://github.com/dedovskaya/CFUCounter) | Cuenta colonias con una red neuronal (Mask R-CNN) | Requiere un entorno pesado y desactualizado para Colab. |
| [REPOP](https://elifesciences.org/articles/107122v1) | Estimación bayesiana de poblaciones a partir de conteos | Requiere réplicas que este diseño (una placa por dilución) no tiene. Queda como trabajo futuro. |

Para el plan de muestreo (n, c, m, M) no se encontró una implementación pública en Python, por lo que se escribió una lógica propia siguiendo los planes de atributos de 2 y 3 clases (referencia: herramienta de análisis de planes de muestreo microbiológico de la FAO/OMS).

El código propio implementa exactamente el protocolo de laboratorio: fórmula UFC/g (colonias ÷ volumen sembrado × factor de dilución), selección de la placa más confiable por dilución, manejo de placas TNTC y no confiables, validación de controles, y reporte presuntivo diferenciando "crecimiento" de "colonias típicas".

## Limitaciones
- Una placa por dilución, sin duplicado; microbiología solo en el día 0.
- Agar EMB en lugar de TBX para *E. coli* (método de referencia): el resultado es presuntivo y la comparación con el RTCA es orientativa.
- Agar SS y caldo nutritivo no selectivo en lugar de XLD/HE/BS con enriquecimiento selectivo; sin confirmación bioquímica (TSI, LIA, urea).
- Con crecimiento abundante o confluente, otras colonias pudieron enmascarar colonias típicas.
- El análisis automático de color no fue confiable por la variabilidad de iluminación y fondo en las fotografías; el color se evaluó visualmente con una escala ordinal por un solo observador.

## Alcance
Los resultados corresponden a un ejercicio académico. No constituyen un dictamen de registro sanitario, que requiere un laboratorio acreditado y la autoridad competente (MINSA/AUPSA).

## Uso de herramientas de IA
Se utilizó Claude (Anthropic) como asistente para estructurar el repositorio, redactar y depurar el código en Python, buscar herramientas existentes en GitHub y PyPI, y redactar este README. El diseño experimental, el trabajo de laboratorio, el registro de datos y su revisión fueron realizados por los autores.
