---
name: descargando-enaho
description: Descarga del INEI los módulos 34 (Sumaria) y 02 (Miembros) de la ENAHO en formato STATA, los descomprime en datos/ y baja el GeoJSON de los 25 departamentos del Perú. Úsala cuando pidan descargar o bajar la ENAHO, o cuando otra skill no encuentre los archivos .dta en datos/.
allowed-tools: Bash(uv run python .claude/skills/descargando-enaho/scripts/descargar.py *), Read
---

# Descargar la ENAHO

1. Corre `uv run python .claude/skills/descargando-enaho/scripts/descargar.py --anio $0`
   (si no hay argumento, usa `--anio 2024`).
2. Revisa `datos/descarga.txt`: debe listar `sumaria-<año>.dta`, `enaho01-<año>-200.dta`
   y `peru_departamental.geojson`, cada uno con su tamaño.
3. Si un archivo ya existe, el script no lo vuelve a bajar. Usa `--forzar` solo si el usuario lo pide.
4. Si el portal del INEI falla (caída, certificado), informa el error tal cual. No desactives
   la verificación SSL ni busques espejos no oficiales.

Para años distintos de 2024, el código de encuesta cambia: lee `reference.md`.
