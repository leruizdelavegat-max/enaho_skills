"""Gráficos de pobreza ponderada a partir de salidas/personas_<anio>.parquet.

Uso: uv run python .claude/skills/graficando-enaho/scripts/graficar.py --por area sexo --indicador pobre
"""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

CORTES = ["area", "sexo", "grupo_edad", "departamento"]
NOMBRES = {"pobre": "Pobreza monetaria", "pobre_extremo": "Pobreza extrema"}
ETIQUETAS = {"area": "área", "sexo": "sexo", "grupo_edad": "grupo de edad", "departamento": "departamento"}


def tasa_ponderada(base, por, indicador):
    g = base.assign(_num=base[indicador] * base.facpob07).groupby(por, observed=True)
    t = (100 * g._num.sum() / g.facpob07.sum()).rename("tasa_%").to_frame()
    t["poblacion_miles"] = g.facpob07.sum() / 1e3
    t["muestra"] = g.size()
    return t


def graficar(tabla, por, indicador, anio, nacional, destino):
    if por == "departamento":
        tabla = tabla.sort_values("tasa_%")
    alto = max(2.5, 0.35 * len(tabla) + 1.2)
    fig, ax = plt.subplots(figsize=(7, alto))
    barras = ax.barh(tabla.index.astype(str), tabla["tasa_%"], color="#2f6f9f")
    ax.bar_label(barras, labels=[f"{v:.1f} %" for v in tabla["tasa_%"]], padding=3, fontsize=9)
    ax.axvline(nacional, color="#c0392b", lw=1, ls="--")
    ax.text(nacional, len(tabla) - 0.4, f" Perú {nacional:.1f} %", color="#c0392b", fontsize=8, va="bottom")
    ax.set_xlim(0, max(tabla["tasa_%"].max(), nacional) * 1.18)
    ax.set_xlabel("% de la población")
    ax.set_title(f"{NOMBRES[indicador]} por {ETIQUETAS[por]}, {anio}", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, f"Fuente: INEI, ENAHO {anio}. Ponderado con facpob07.", fontsize=7, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--por", nargs="+", choices=CORTES, default=["area"])
    p.add_argument("--indicador", choices=list(NOMBRES), default="pobre")
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--salidas", default="salidas")
    p.add_argument("--figuras", default="figuras")
    a = p.parse_args()

    ruta = Path(a.salidas) / f"personas_{a.anio}.parquet"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Usa primero la skill limpiando-enaho.")
    base = pd.read_parquet(ruta)
    figuras = Path(a.figuras)
    figuras.mkdir(parents=True, exist_ok=True)

    nacional = 100 * (base[a.indicador] * base.facpob07).sum() / base.facpob07.sum()
    print(f"{NOMBRES[a.indicador]} nacional {a.anio}: {nacional:.1f} %\n")
    for por in a.por:
        tabla = tasa_ponderada(base, por, a.indicador)
        destino = figuras / f"{a.indicador}_por_{por}.png"
        graficar(tabla, por, a.indicador, a.anio, nacional, destino)
        print(tabla.round(1).to_string())
        print(f"-> {destino}\n")


if __name__ == "__main__":
    main()
