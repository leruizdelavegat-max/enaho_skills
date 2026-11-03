---
name: graficando-enaho
description: Grafica la pobreza de la ENAHO por área, sexo, grupo de edad o departamento a partir de la base limpia salidas/personas_<año>.parquet y guarda PNG en figuras/. Úsala cuando pidan un gráfico, una tabla o una comparación de pobreza con la ENAHO.
allowed-tools: Bash(uv run python .claude/skills/graficando-enaho/scripts/graficar.py *), Read
---

# Graficar la pobreza

Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.

1. Elige el corte según la pregunta: `area`, `sexo`, `grupo_edad` o `departamento`.
   Elige el indicador: `pobre` (pobreza total) o `pobre_extremo`.
2. Corre `uv run python .claude/skills/graficando-enaho/scripts/graficar.py --por <corte> --indicador <indicador>`.
   Para varios cortes a la vez: `--por area sexo grupo_edad`.
3. El script imprime la tabla ponderada y guarda `figuras/<indicador>_por_<corte>.png`.
   Responde con las cifras de la tabla, no con lo que "se ve" en el gráfico.

## Reglas

- Toda tasa se pondera con `facpob07`. Nunca grafiques conteos de la muestra.
- Pobre es la columna `pobre` (0/1). Nunca promedies la columna `pobreza` (1, 2, 3).
- El título del PNG dice el año y la fuente: "Fuente: INEI, ENAHO <año>".
- Si la pregunta pide un corte que no está en la base (por ejemplo, nivel educativo), dilo:
  hace falta otro módulo y una nueva limpieza.
