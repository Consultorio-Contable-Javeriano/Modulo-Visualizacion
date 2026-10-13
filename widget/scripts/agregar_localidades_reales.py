"""
Genera `datos_reales_localidades.json` (conteo de personas por localidad de
Bogotá) a partir del Excel de inscripción del Consultorio, para probar el
widget localmente con una distribución real.

Privacidad (Ley 1581 de 2012):
- Del Excel SOLO se leen:
  * las columnas cuyo encabezado contiene "Localidad";
  * "Número de Identificación" y "Hora de inicio", únicamente para quitar
    inscripciones repetidas de una misma persona (se conserva la más
    reciente). Se usan solo en memoria: nunca se imprimen ni se guardan.
  Las demás columnas (nombre, teléfono, correo, etc.) nunca se cargan: se
  descartan en la misma lectura (`usecols`).
- La salida es únicamente un conteo agregado de personas por localidad, sin
  nada a nivel de persona.
- Las localidades con entre 1 y 4 personas se publican como "menos de 5"
  (`"cantidad": null, "menos_de": 5`): el número exacto no se escribe en la
  salida, para que nadie pueda deducir quién se inscribió.
- La salida es pública (se sube al repositorio y se publica en el mapa), por
  eso nunca debe contener nada más que este conteo.

Uso (desde la carpeta raíz del repositorio):

    .venv/bin/python widget/scripts/agregar_localidades_reales.py "/ruta/al/Excel.xlsx"

Por defecto escribe `widget/mock-api/datos_reales_localidades.json`, que es
el archivo que lee el widget; se puede cambiar con `--salida`.
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
SALIDA_POR_DEFECTO = CARPETA_WIDGET / "mock-api" / "datos_reales_localidades.json"

# Conteos entre 1 y UMBRAL_RESERVA - 1 se publican como "menos de UMBRAL_RESERVA".
UMBRAL_RESERVA = 5


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


def buscar_columna(encabezados, nombre):
    for c in encabezados:
        if normalizar(c) == nombre:
            return c
    sys.exit(f"El Excel no tiene la columna '{nombre}'.")


def leer_localidades_por_persona(ruta_excel):
    """Devuelve una lista con la localidad de cada persona (una por persona,
    de su inscripción más reciente). Solo se cargan las columnas de localidad,
    identificación y hora de inicio."""
    encabezados = pd.read_excel(ruta_excel, nrows=0).columns
    col_localidad = [c for c in encabezados if "LOCALIDAD" in normalizar(c)]
    if not col_localidad:
        sys.exit("El Excel no tiene ninguna columna con 'Localidad' en el encabezado.")
    col_id = buscar_columna(encabezados, "NUMERO DE IDENTIFICACION")
    col_fecha = buscar_columna(encabezados, "HORA DE INICIO")

    print("Columnas leídas (solo estas):")
    for c in [*col_localidad, col_id, col_fecha]:
        print(f"  - {normalizar(c)[:90]}")

    df = pd.read_excel(ruta_excel, usecols=[*col_localidad, col_id, col_fecha], dtype=str)
    # Una persona responde una sola de estas preguntas (virtual o presencial),
    # así que se toma el primer valor no vacío de cada fila.
    df["localidad"] = df[col_localidad].bfill(axis=1).iloc[:, 0]

    # Quitar inscripciones repetidas: misma identificación (solo dígitos) ->
    # se conserva la más reciente. Las filas sin identificación se cuentan
    # tal cual, porque no hay forma de saber si están repetidas.
    df["_id"] = df[col_id].str.replace(r"\D", "", regex=True).replace("", None)
    df["_fecha"] = pd.to_datetime(df[col_fecha], errors="coerce")
    df = df.sort_values("_fecha")
    repetidas = df["_id"].notna() & df["_id"].duplicated(keep="last")
    print(f"\nInscripciones repetidas descartadas: {repetidas.sum()}")

    return df.loc[~repetidas, "localidad"].dropna().tolist()


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("excel", help="Ruta al Excel de inscripción")
    parser.add_argument("--salida", default=str(SALIDA_POR_DEFECTO))
    args = parser.parse_args()

    oficiales = cargar_localidades_oficiales()
    valores = leer_localidades_por_persona(args.excel)

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
    resultado = []
    for clave, (codigo, nombre) in sorted(oficiales.items(), key=lambda x: -conteo[x[0]]):
        n = conteo[clave]
        if 0 < n < UMBRAL_RESERVA:
            resultado.append({"codigo_loc": codigo, "nombre": nombre,
                              "cantidad": None, "menos_de": UMBRAL_RESERVA})
        else:
            resultado.append({"codigo_loc": codigo, "nombre": nombre, "cantidad": n})
    reservadas = [r["nombre"] for r in resultado if r["cantidad"] is None]

    # Mismo formato que mock-api/localidades.json: el arreglo que espera el
    # widget (contrato de la API).
    Path(args.salida).write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nValores de localidad leídos: {len(valores)}")
    print(f"Emparejados con una localidad oficial: {sum(conteo.values())}")
    print(f"Publicadas como 'menos de {UMBRAL_RESERVA}': {', '.join(reservadas) or 'ninguna'}")
    print(f"Archivo generado: {args.salida}")
    if no_emparejados:
        print("\n⚠️  Valores que NO se pudieron emparejar (no se contaron):")
        for valor, n in no_emparejados.most_common():
            print(f"  {n:>4}  {valor!r}")


if __name__ == "__main__":
    main()
