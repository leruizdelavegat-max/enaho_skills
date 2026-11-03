"""Descarga los módulos 34 y 02 de la ENAHO y los límites departamentales del Perú.

Uso: python .claude/skills/descargando-enaho/scripts/descargar.py --anio 2024
"""
import argparse
import io
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import truststore

# El servidor del INEI no envía su certificado intermedio; el almacén del sistema operativo
# sí lo completa. La verificación SSL sigue activa.
truststore.inject_into_ssl()

CODIGOS = {2024: 966}
MODULOS = {"34": "sumaria-{anio}.dta", "02": "enaho01-{anio}-200.dta"}
URL_INEI = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/{codigo}-Modulo{modulo}.zip"
URL_LIMITES = ("https://raw.githubusercontent.com/juaneladio/peru-geojson/master/"
               "peru_departamental_simple.geojson")


def bajar(url, intentos=3):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for i in range(1, intentos + 1):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            if i == intentos:
                raise RuntimeError(f"No se pudo descargar {url}: {e}") from e
            print(f"  intento {i} falló ({e}); reintentando...")
            time.sleep(3 * i)


def extraer_dta(contenido, destino, esperado):
    with zipfile.ZipFile(io.BytesIO(contenido)) as z:
        dtas = [n for n in z.namelist() if n.lower().endswith(".dta")]
        if not dtas:
            raise RuntimeError("El ZIP no trae ningún .dta")
        for nombre in dtas:
            (destino / Path(nombre).name.lower()).write_bytes(z.read(nombre))
    if not (destino / esperado).exists():
        raise RuntimeError(f"Se esperaba {esperado}; el ZIP trae: {[Path(n).name for n in dtas]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--codigo", type=int, help="código de encuesta del INEI (ver reference.md)")
    p.add_argument("--destino", default="datos")
    p.add_argument("--forzar", action="store_true", help="vuelve a bajar aunque ya exista")
    a = p.parse_args()

    codigo = a.codigo or CODIGOS.get(a.anio)
    if codigo is None:
        sys.exit(f"No conozco el código de la ENAHO {a.anio}. Búscalo y pásalo con --codigo.")

    destino = Path(a.destino)
    destino.mkdir(parents=True, exist_ok=True)
    log = []

    for modulo, plantilla in MODULOS.items():
        esperado = plantilla.format(anio=a.anio)
        if (destino / esperado).exists() and not a.forzar:
            print(f"{esperado}: ya existe, no se descarga")
        else:
            url = URL_INEI.format(codigo=codigo, modulo=modulo)
            print(f"Descargando {url}")
            contenido = bajar(url)
            print(f"  {len(contenido) / 1e6:.1f} MB")
            extraer_dta(contenido, destino, esperado)
        log.append(f"{esperado}\t{(destino / esperado).stat().st_size / 1e6:.1f} MB")

    limites = destino / "peru_departamental.geojson"
    if not limites.exists() or a.forzar:
        print(f"Descargando {URL_LIMITES}")
        limites.write_bytes(bajar(URL_LIMITES))
    log.append(f"{limites.name}\t{limites.stat().st_size / 1e6:.1f} MB")

    (destino / "descarga.txt").write_text(
        f"ENAHO {a.anio} (código {codigo})\n" + "\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
