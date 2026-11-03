"""Limpia la Sumaria y el módulo 200 de la ENAHO y arma una base de personas residentes.

Uso: uv run python .claude/skills/limpiando-enaho/scripts/limpiar.py --anio 2024
Salidas: salidas/personas_<anio>.parquet y salidas/validacion.txt
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

LLAVES = {"conglome": 6, "vivienda": 3, "hogar": 2, "codperso": 2, "ubigeo": 6}
HOGAR = ["conglome", "vivienda", "hogar"]

DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}

# Cifras de control por año (slide "Seis trampas" y cifra oficial del INEI)
CONTROL = {2024: {"hogares": 33_691, "filas_200": 117_721, "residentes": 108_664,
                  "pobreza": 27.6, "poblacion_millones": 34.5}}


def normalizar_nombre(c):
    """Trampa 2: 'aÑo' -> 'anio'. Minúsculas, sin tildes, solo [a-z0-9_]."""
    c = unicodedata.normalize("NFKD", str(c).lower()).encode("ascii", "ignore").decode("ascii")
    c = re.sub(r"[^a-z0-9_]", "", c)
    return "anio" if c in {"ano", "aao", "ao"} else c


def como_texto(s, largo):
    """Trampa 1: códigos con ceros a la izquierda."""
    if pd.api.types.is_numeric_dtype(s):
        s = s.astype("Int64").astype(str)
    return s.astype(str).str.strip().str.zfill(largo)


def leer(ruta):
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Usa primero la skill descargando-enaho.")
    df = pd.read_stata(ruta, convert_categoricals=False)  # trampa 6: códigos, no etiquetas
    df.columns = [normalizar_nombre(c) for c in df.columns]
    for c, largo in LLAVES.items():
        if c in df.columns:
            df[c] = como_texto(df[c], largo)
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--datos", default="datos")
    p.add_argument("--salidas", default="salidas")
    a = p.parse_args()

    datos, salidas = Path(a.datos), Path(a.salidas)
    salidas.mkdir(parents=True, exist_ok=True)

    sumaria = leer(datos / f"sumaria-{a.anio}.dta")
    miembros = leer(datos / f"enaho01-{a.anio}-200.dta")
    n_hogares, n_filas = len(sumaria), len(miembros)

    # Trampa 3: solo residentes habituales
    res = ((miembros.p204 == 1) & (miembros.p205 == 2)) | ((miembros.p204 == 2) & (miembros.p206 == 1))
    personas = miembros.loc[res, HOGAR + ["codperso", "p203", "p207", "p208a", "facpob07"]]

    # Trampa 4: unión muchos a uno validada
    cols_sumaria = HOGAR + ["ubigeo", "dominio", "estrato", "pobreza", "mieperho", "factor07"]
    base = personas.merge(sumaria[cols_sumaria], on=HOGAR, how="left",
                          validate="m:1", indicator=True)
    huerfanos = int((base._merge != "both").sum())
    base = base.drop(columns="_merge")
    base[["facpob07", "factor07"]] = base[["facpob07", "factor07"]].astype("float64")

    # Trampa 6: pobreza es categoría
    base["pobre"] = (base.pobreza <= 2).astype("int8")
    base["pobre_extremo"] = (base.pobreza == 1).astype("int8")
    base["cod_dep"] = base.ubigeo.str[:2]
    base["departamento"] = base.cod_dep.map(DEPARTAMENTOS)
    base["area"] = base.estrato.le(5).map({True: "Urbano", False: "Rural"})
    base["sexo"] = base.p207.map({1: "Hombre", 2: "Mujer"})
    base["edad"] = base.p208a
    base["grupo_edad"] = pd.cut(base.edad, [-1, 13, 29, 44, 64, 200],
                                labels=["0-13", "14-29", "30-44", "45-64", "65+"]).astype(str)
    base["anio"] = a.anio
    base = base.drop(columns=["p207", "p208a"])

    salida = salidas / f"personas_{a.anio}.parquet"
    base.to_parquet(salida, index=False)

    # Trampa 5: resultados ponderados
    pob_personas = base.facpob07.sum()
    tasa_personas = 100 * (base.pobre * base.facpob07).sum() / pob_personas
    pob_hogares = (sumaria.factor07 * sumaria.mieperho).sum()
    tasa_hogares = 100 * ((sumaria.pobreza <= 2) * sumaria.factor07 * sumaria.mieperho).sum() / pob_hogares

    ctrl = CONTROL.get(a.anio, {})
    lineas = []

    def chequeo(nombre, valor, esperado=None, tolerancia=0, fmt="{:,.0f}"):
        texto = fmt.format(valor)
        if esperado is None:
            estado = "OK" if valor else "REVISAR"
        else:
            ok = abs(valor - esperado) <= tolerancia
            estado = "OK" if ok else "REVISAR"
            texto += f" (esperado {fmt.format(esperado)})"
        lineas.append(f"{estado:8}{nombre}: {texto}")

    chequeo("Hogares en sumaria", n_hogares, ctrl.get("hogares"))
    chequeo("Filas en módulo 200", n_filas, ctrl.get("filas_200"))
    chequeo("Residentes habituales", len(personas), ctrl.get("residentes"))
    chequeo("Hogares duplicados en sumaria", sumaria.duplicated(HOGAR).sum(), 0)
    chequeo("Personas sin hogar en la unión", huerfanos, 0)
    chequeo("Llaves con 6 dígitos en ubigeo", base.ubigeo.str.fullmatch(r"\d{6}").all())
    chequeo("Departamentos encontrados", base.departamento.nunique(), 25)
    chequeo("Población expandida (millones)", pob_personas / 1e6,
            ctrl.get("poblacion_millones"), 0.5, "{:.1f}")
    chequeo("Pobreza % (personas, facpob07)", tasa_personas, ctrl.get("pobreza"), 0.15, "{:.1f}")
    chequeo("Pobreza % (sumaria, factor07 x mieperho)", tasa_hogares, ctrl.get("pobreza"), 0.15, "{:.1f}")

    texto = f"Validación ENAHO {a.anio}\n" + "\n".join(lineas) + f"\nBase: {salida} ({len(base):,} filas)\n"
    (salidas / "validacion.txt").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
