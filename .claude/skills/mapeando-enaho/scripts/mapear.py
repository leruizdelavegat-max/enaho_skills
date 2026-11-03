"""Mapa de pobreza ponderada por departamento.

Uso: uv run python .claude/skills/mapeando-enaho/scripts/mapear.py --anio 2024
"""
import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

NOMBRES = {"pobre": "Pobreza monetaria", "pobre_extremo": "Pobreza extrema"}
CAMPOS_CODIGO = ["FIRST_IDDP", "IDDPTO", "CCDD", "CODDEP"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--indicador", choices=list(NOMBRES), default="pobre")
    p.add_argument("--salidas", default="salidas")
    p.add_argument("--geojson", default="datos/peru_departamental.geojson")
    p.add_argument("--mapas", default="mapas")
    a = p.parse_args()

    ruta = Path(a.salidas) / f"personas_{a.anio}.parquet"
    if not ruta.exists():
        sys.exit(f"No existe {ruta}. Usa primero la skill limpiando-enaho.")
    if not Path(a.geojson).exists():
        sys.exit(f"No existe {a.geojson}. Usa primero la skill descargando-enaho.")

    base = pd.read_parquet(ruta)
    g = base.assign(_num=base[a.indicador] * base.facpob07).groupby(["cod_dep", "departamento"])
    tabla = (100 * g._num.sum() / g.facpob07.sum()).rename("tasa").reset_index()
    nacional = 100 * (base[a.indicador] * base.facpob07).sum() / base.facpob07.sum()

    geo = gpd.read_file(a.geojson)
    campo = next((c for c in CAMPOS_CODIGO if c in geo.columns), None)
    if campo is None:
        sys.exit(f"El GeoJSON no tiene campo de código; columnas: {list(geo.columns)}")
    geo["cod_dep"] = geo[campo].astype(str).str.strip().str.zfill(2)

    mapa = geo.merge(tabla, on="cod_dep", how="left", validate="1:1")
    faltan = mapa.loc[mapa.tasa.isna(), "cod_dep"].tolist()
    if len(mapa) != 25 or faltan:
        sys.exit(f"La unión no da 25 departamentos completos: {len(mapa)} polígonos, sin dato: {faltan}")

    mapas = Path(a.mapas)
    mapas.mkdir(parents=True, exist_ok=True)
    nombre = "pobreza" if a.indicador == "pobre" else a.indicador
    destino = mapas / f"{nombre}_departamento.png"

    fig, ax = plt.subplots(figsize=(7, 9))
    mapa.plot(column="tasa", cmap="YlOrRd", edgecolor="white", linewidth=0.6, ax=ax, legend=True,
              legend_kwds={"label": "% de la población", "shrink": 0.5})
    for _, fila in mapa.iterrows():
        pt = fila.geometry.representative_point()
        ax.annotate(f"{fila.tasa:.0f}", (pt.x, pt.y), ha="center", va="center", fontsize=7)
    ax.set_title(f"{NOMBRES[a.indicador]} por departamento, {a.anio}\nPerú: {nacional:.1f} %",
                 loc="left", fontweight="bold")
    ax.set_axis_off()
    fig.text(0.02, 0.02, f"Fuente: INEI, ENAHO {a.anio}. Ponderado con facpob07.", fontsize=7, color="#555")
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"{NOMBRES[a.indicador]} nacional {a.anio}: {nacional:.1f} %\n")
    print(tabla.sort_values("tasa", ascending=False).round(1).to_string(index=False))
    print(f"\n-> {destino}")


if __name__ == "__main__":
    main()
