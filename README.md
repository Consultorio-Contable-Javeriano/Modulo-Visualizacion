# Mapa de participación — Consultorio Contable Javeriano

> **Widget de geolocalización (Leaflet + OpenStreetMap):** está en la
> carpeta [`widget/`](widget/). Es el entregable oficial del módulo y se
> embebe por `<iframe>` en la página del Consultorio. Instrucciones, contrato
> de la API y pendientes con el subgrupo de registro en
> [`widget/README.md`](widget/README.md). Lo que sigue en este README
> describe el prototipo anterior en Streamlit.

Aplicación web (Streamlit) que muestra, sobre un mapa interactivo de
Colombia, cuántas personas se inscriben a las capacitaciones del
Consultorio Contable Javeriano, por municipio y departamento.

## ¿Qué hace la app?

1. Lee el Excel de inscripción exportado de Google Forms.
2. Descarta filas incompletas y duplicados (se queda con la
   inscripción más reciente de cada persona, según su número de
   identificación).
3. Limpia el texto libre de "ciudad/municipio" (mayúsculas/minúsculas,
   tildes, guiones, etc.) y lo empareja contra la tabla oficial de
   municipios de Colombia (DIVIPOLA - DANE) usando coincidencia
   aproximada (`rapidfuzz`).
4. A partir del municipio, obtiene el departamento correspondiente.
5. Dibuja un mapa coroplético de Colombia por departamento (Plotly),
   con una tabla de detalle por municipio debajo, y filtros por
   modalidad (virtual/presencial) y búsqueda de municipio.

## Estructura del proyecto

```
app.py                          -> interfaz de Streamlit (lo que se ejecuta)
data_loader.py                  -> lee el Excel "en crudo" (fácil de reemplazar por Google Sheets/BD)
referencia_geografica.py        -> carga la tabla DIVIPOLA y el GeoJSON de departamentos
emparejamiento_municipios.py    -> coincidencia aproximada de texto -> municipio oficial
procesamiento.py                -> limpieza, deduplicación y agregación de los datos
data/                           -> archivo Excel de inscripción
reference/                      -> tabla DIVIPOLA (CSV) y GeoJSON de departamentos
```

## Cómo correrlo localmente

1. Cree y active un entorno virtual (recomendado):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # En Windows: .venv\Scripts\activate
   ```

2. Instale las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

   En Windows PowerShell también puede instalar todo sin activar el entorno:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Coloque su archivo Excel de inscripción dentro de la carpeta
   `data/` (puede conservar el nombre original exportado por Google Forms)
   o súbalo desde la barra lateral de la app una vez esté corriendo. Si hay
   un solo archivo `.xlsx` en `data/`, la aplicación lo detectará
   automáticamente.

4. Ejecute la aplicación:

   ```bash
   streamlit run app.py
   ```

   En Windows PowerShell, si el entorno no está activado:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

5. Abra en el navegador la URL que aparece en la terminal
   (normalmente `http://localhost:8501`).

## Cómo desplegarlo gratis en Streamlit Community Cloud

1. Suba este proyecto a un repositorio de GitHub (incluyendo
   `requirements.txt`, `app.py` y las carpetas `reference/` y, si
   quiere que el archivo de ejemplo quede público, `data/`).
2. Entre a [share.streamlit.io](https://share.streamlit.io) e inicie
   sesión con su cuenta de GitHub.
3. Haga clic en "New app", elija el repositorio, la rama y el archivo
   principal (`app.py`).
4. Haga clic en "Deploy". Streamlit Cloud instalará automáticamente
   lo que está en `requirements.txt` y publicará la app en una URL
   pública gratuita.
5. Si su archivo Excel contiene datos sensibles (nombres, teléfonos,
   identificación), **no lo suba al repositorio**: en vez de eso, use
   el botón "Sube un Excel de inscripción" que aparece en la barra
   lateral de la app ya desplegada para cargarlo manualmente cada vez.

## Notas para el grupo

- La función `load_data_raw` en `data_loader.py` es la única que sabe
  leer el Excel. El día que quieran conectar la app a un Google Sheet
  o a una base de datos, basta con reescribir esa función para que
  devuelva un DataFrame con las mismas columnas: el resto de la app
  no necesita cambiar.
- Los valores de ciudad que no se pudieron emparejar con confianza
  contra la tabla oficial de municipios aparecen en un panel
  desplegable ("⚠️ valores no emparejados") al final de la página,
  para revisarlos a mano.
