# Referencia: ENAHO 2024, módulos 34 y 02

## Archivos

| Módulo | Archivo | Una fila por | Filas | Llaves | Factor |
|---|---|---|---|---|---|
| 34 · Sumaria | `sumaria-2024.dta` | hogar | 33 691 | `conglome`, `vivienda`, `hogar` | `factor07` |
| 02 · Miembros | `enaho01-2024-200.dta` | persona | 117 721 | las tres + `codperso` | `facpob07` |

Largo de las llaves como texto: `conglome` 6, `vivienda` 3, `hogar` 2, `codperso` 2, `ubigeo` 6.

## Sumaria (módulo 34)

| Variable | Significado |
|---|---|
| `pobreza` | 1 pobre extremo, 2 pobre no extremo, 3 no pobre |
| `mieperho` | miembros del hogar (sin trabajadores del hogar ni pensionistas) |
| `ubigeo` | departamento (2 dígitos) + provincia (2) + distrito (2) |
| `estrato` | 1–5 urbano, 6–8 rural |
| `dominio` | 1 Costa norte, 2 Costa centro, 3 Costa sur, 4 Sierra norte, 5 Sierra centro, 6 Sierra sur, 7 Selva, 8 Lima Metropolitana |
| `factor07` | factor de expansión del hogar |
| `linea`, `linpe` | línea de pobreza total y extrema (soles por persona al mes) |
| `gashog2d`, `inghog1d` | gasto e ingreso anual del hogar |

## Miembros (módulo 02)

| Variable | Significado |
|---|---|
| `p203` | parentesco: 1 jefe, 2 cónyuge, 3 hijo, 4 yerno/nuera, 5 nieto, 6 padres/suegros, 7 otros parientes, 8 trabajador del hogar, 9 pensionista, 10 otros no parientes, 11 hermano |
| `p204` | ¿es miembro del hogar? 1 sí, 2 no |
| `p205` | ¿ausente más de 30 días? 1 sí, 2 no |
| `p206` | ¿presente más de 30 días? 1 sí, 2 no |
| `p207` | sexo: 1 hombre, 2 mujer |
| `p208a` | edad en años |
| `facpob07` | factor de expansión de la persona |

Residente habitual: `(p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1)`.

## Columnas de `salidas/personas_<año>.parquet`

Llaves y `ubigeo` como texto; `departamento` (nombre) y `cod_dep` (2 dígitos);
`area` (Urbano / Rural); `dominio`, `estrato`; `sexo` (Hombre / Mujer); `edad`;
`grupo_edad` (0-13, 14-29, 30-44, 45-64, 65+); `pobreza` (código original);
`pobre` y `pobre_extremo` (0/1); `mieperho`, `factor07`, `facpob07`.

## Cifras oficiales de control (2024)

- Pobreza monetaria nacional: 27,6 % de la población.
- Población expandida: unos 34,5 millones de personas.

Para otras variables de los módulos, revisa el diccionario PDF que viene en cada ZIP del INEI.
