---
name: mapeando-enaho
description: Hace el mapa de pobreza por departamento del Perú con la ENAHO, uniendo la base limpia salidas/personas_<año>.parquet al GeoJSON de los 25 departamentos por código, y guarda mapas/pobreza_departamento.png. Úsala cuando pidan un mapa o la pobreza por departamento o región.
allowed-tools: Bash(uv run python .claude/skills/mapeando-enaho/scripts/mapear.py *), Read
---

# Mapear la pobreza por departamento

Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.
Si no existe `datos/peru_departamental.geojson`, usa primero la skill `descargando-enaho`.

1. Corre `uv run python .claude/skills/mapeando-enaho/scripts/mapear.py`
   (agrega `--indicador pobre_extremo` si piden pobreza extrema).
2. El script imprime la tabla de los 25 departamentos, ordenada de mayor a menor,
   y guarda `mapas/pobreza_departamento.png` (o `mapas/pobre_extremo_departamento.png`).
3. Responde con las cifras de la tabla: los tres departamentos más pobres, los tres menos
   pobres y el promedio nacional.

## Reglas

- La pobreza por departamento se pondera con `facpob07`.
- La unión con el GeoJSON es **por código** (`cod_dep`, 2 dígitos con cero a la izquierda),
  nunca por nombre: "Áncash" y "ANCASH" no coinciden, "01" y "01" sí.
- Si la unión no da exactamente 25 departamentos, el script se detiene. No lo fuerces:
  revisa el campo de código del GeoJSON.
- Lima incluye Lima Metropolitana y Lima Provincias; Callao va aparte.
