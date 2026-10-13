"""
Genera `datos_reales_localidades.json` (conteo de personas por localidad de
Bogotá) a partir del Excel de inscripción del Consultorio, para probar el
widget localmente con una distribución real.

Privacidad (Ley 1581 de 2012):
- Del Excel SOLO se leen las columnas cuyo encabezado contiene "Localidad".
  Las demás columnas (nombre, identificación, teléfono, correo, etc.) nunca se
  cargan en memoria: se descartan en la misma lectura (`usecols`).
- La salida es únicamente un conteo agregado por localidad, sin nada a nivel
  de persona.
- La salida queda ignorada por git (ver `.gitignore` en la raíz). No la suba
  al repositorio ni la comparta.

Uso (desde la carpeta raíz del repositorio):

    .venv/bin/python widget/scripts/agregar_localidades_reales.py "/ruta/al/Excel.xlsx"

Por defecto escribe `widget/datos_reales_localidades.json`; se puede cambiar
con `--salida`.
"""

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

CARPETA_WIDGET = Path(__file__).resolve().parent.parent
INDEX_HTML = CARPETA_WIDGET / "index.html"
SALIDA_POR_DEFECTO = CARPETA_WIDGET / "datos_reales_localidades.json"


def normalizar(texto):
    """'  Engativá ' -> 'ENGATIVA' (sin tildes, mayúsculas, espacios simples)."""
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().upper()


def cargar_localidades_oficiales():
    """Lee los nombres/códigos de las 20 localidades del GeoJSON embebido en
    index.html, para que el script y el mapa usen exactamente la misma
    referencia."""
    for linea in INDEX_HTML.read_text(encoding="utf-8").splitlines():
        if linea.startswith("const LOCALIDADES_GEOJSON = "):
            geojson = json.loads(
                linea[len("const LOCALIDADES_GEOJSON = "):].rstrip().rstrip(";")
            )
            return {
                normalizar(f["properties"]["nombre"]): (
                    str(f["properties"]["codigo_loc"]),
                    f["properties"]["nombre"],
                )
                for f in geojson["features"]
            }
    sys.exit(f"No se encontró LOCALIDADES_GEOJSON dentro de {INDEX_HTML}")


# Variantes que se aceptan además del nombre oficial (ya normalizadas).
SINONIMOS = {
    "CANDELARIA": "LA CANDELARIA",
    "MARTIRES": "LOS MARTIRES",
    "SANTAFE": "SANTA FE",
    "RAFAEL URIBE": "RAFAEL URIBE URIBE",
}


def leer_solo_localidades(ruta_excel):
    """Devuelve una lista con el valor de localidad de cada fila. Ninguna otra
    columna del Excel se carga."""
    columnas = [
        c for c in pd.read_excel(ruta_excel, nrows=0).columns if "LOCALIDAD" in normalizar(c)
    ]
    if not columnas:
        sys.exit("El Excel no tiene ninguna columna con 'Localidad' en el encabezado.")
    print("Columnas leídas (solo estas):")
    for c in columnas:
        print(f"  - {normalizar(c)[:90]}")

    df = pd.read_excel(ruta_excel, usecols=columnas, dtype=str)
    # Una persona responde una sola de estas preguntas (virtual o presencial),
    # así que se toma el primer valor no vacío de cada fila.
    return df.bfill(axis=1).iloc[:, 0].dropna().tolist()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("excel", help="Ruta al Excel de inscripción")
    parser.add_argument("--salida", default=str(SALIDA_POR_DEFECTO))
    args = parser.parse_args()

    oficiales = cargar_localidades_oficiales()
    valores = leer_solo_localidades(args.excel)

    conteo = Counter()
    no_emparejados = Counter()
    for valor in valores:
        clave = normalizar(valor)
        clave = SINONIMOS.get(clave, clave)
        if clave in oficiales:
            conteo[clave] += 1
        else:
            no_emparejados[valor] += 1

    # Se incluyen las 20 localidades, también las que tienen 0, para que el
    # mapa no las pinte como "sin datos".
    resultado = sorted(
        (
            {"codigo_loc": codigo, "nombre": nombre, "cantidad": conteo[clave]}
            for clave, (codigo, nombre) in oficiales.items()
        ),
        key=lambda r: -r["cantidad"],
    )

    # Mismo formato que mock-api/db.json: json-server lo sirve en
    # /localidades, que responde el arreglo que espera el widget.
    Path(args.salida).write_text(
        json.dumps({"localidades": resultado}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nValores de localidad leídos: {len(valores)}")
    print(f"Emparejados con una localidad oficial: {sum(conteo.values())}")
    print(f"Archivo generado: {args.salida}")
    if no_emparejados:
        print("\n⚠️  Valores que NO se pudieron emparejar (no se contaron):")
        for valor, n in no_emparejados.most_common():
            print(f"  {n:>4}  {valor!r}")


if __name__ == "__main__":
    main()
