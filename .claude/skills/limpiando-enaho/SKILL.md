---
name: limpiando-enaho
description: Limpia los módulos 34 (Sumaria) y 02 (Miembros) de la ENAHO del INEI y arma una base de personas residentes en salidas/personas_<año>.parquet. Úsala cuando pidan limpiar, unir o calcular pobreza con la ENAHO.
allowed-tools: Bash(uv run python .claude/skills/limpiando-enaho/scripts/limpiar.py *), Read
---

# Limpiar la ENAHO

Si no existen `datos/sumaria-<año>.dta` y `datos/enaho01-<año>-200.dta`, usa primero la skill
`descargando-enaho`.

1. Corre `uv run python .claude/skills/limpiando-enaho/scripts/limpiar.py --anio $0`
   (si no hay argumento, usa `--anio 2024`).
2. Revisa `salidas/validacion.txt`. Cada línea dice OK o REVISAR. Si hay un REVISAR, no
   sigas: explica cuál falló y por qué.
3. Para otras variables, lee `reference.md`.

## Seis trampas (el script ya las resuelve; no las deshagas en código propio)

1. **Ceros a la izquierda:** `conglome`, `vivienda`, `hogar`, `codperso` y `ubigeo` son texto
   (`"015009"`, `"010101"`). Nunca los conviertas a número.
2. **Nombres rotos:** la columna del año llega como `aÑo`. Los nombres se normalizan
   (minúsculas, sin tildes) y el año queda como `anio`.
3. **No todos son residentes:** el módulo 200 tiene 117 721 filas, pero solo 108 664 son
   residentes habituales. La base solo conserva residentes.
4. **Uniones que duplican:** la unión persona → hogar usa `validate="m:1"`.
5. **Encuestas no son personas:** todo resultado poblacional se pondera con `facpob07`
   (personas) o `factor07` (hogares). Nunca reportes conteos de la muestra como población.
6. **Códigos, no números:** `pobreza` 1, 2, 3 son categorías. Pobre es `pobreza <= 2`.
   Nunca promedies `pobreza`; usa las columnas `pobre` y `pobre_extremo`.
