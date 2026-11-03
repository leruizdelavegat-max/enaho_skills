# Referencia: descarga de la ENAHO

## URL de cada módulo

```
https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/<codigo>-Modulo<NN>.zip
```

- `<codigo>`: código de la encuesta en el portal Microdatos del INEI.
- `<NN>`: número de módulo con dos dígitos (`34` = Sumaria, `02` = Miembros del hogar).

| Año | Código | Encuesta |
|---|---|---|
| 2024 | 966 | ENAHO Metodología actualizada, anual |

Para otro año, busca el código en https://proyectos.inei.gob.pe/microdatos/
(Consulta por encuestas → ENAHO Metodología ACTUALIZADA → Condiciones de vida y pobreza,
periodo anual) y pásalo con `--codigo`. No adivines códigos.

## Qué trae cada ZIP

Cada ZIP trae una carpeta con el `.dta` y PDFs (diccionario, ficha técnica, cuestionario).
El script extrae solo los `.dta` y los deja directamente en `datos/`.

## Límites departamentales

`datos/peru_departamental.geojson` viene de
https://github.com/juaneladio/peru-geojson (`peru_departamental_simple.geojson`):
25 polígonos (24 departamentos y la Provincia Constitucional del Callao), con el nombre en
la propiedad `NOMBDEP`.
