# Prototipo del módulo de geolocalización — Consultorio Contable Javeriano

Esto corresponde a la etapa PC2 del cronograma (semanas 8–9): un prototipo
navegable del widget en JavaScript con Leaflet/OpenStreetMap, listo para
validar el diseño con el interlocutor antes de conectarlo a la API real del
módulo de registro. El widget ya está preparado para esa integración: solo
consume datos por `fetch`, nunca los trae embebidos, así que pasar de datos
de prueba a datos reales es cuestión de cambiar una sola línea.

## Archivos

- `index.html` — el widget completo (ideal para embeberlo luego vía
  `<iframe>` en la página institucional del Consultorio Contable, tal como se
  definió en el documento de contextualización).
- Límites de las 20 localidades de Bogotá (fuente: repositorio público
  `decolector/bta-geodata`, ya recortado y simplificado): van embebidos
  dentro de `index.html` (constante `LOCALIDADES_GEOJSON`) porque es
  geografía fija, nunca cambia.
- `mock-api/localidades.json` — datos de ejemplo (sintéticos, no son
  información real de personas atendidas), ya en el formato exacto de la API.
  Es la fuente de datos por defecto del widget.
- `mock-api/db.js` — adaptador para que `json-server` sirva ese mismo archivo
  como API en `http://localhost:3001/localidades`.
- `package.json` — define `npm run mock-api`, que levanta un servidor local con
  el widget y la API de prueba.
- `scripts/agregar_localidades_reales.py` — genera los conteos reales por
  localidad a partir del Excel del Consultorio (solo para pruebas locales).

Todos los comandos de este README se ejecutan dentro de la carpeta `widget/`,
salvo que se indique otra cosa.

## Cómo probarlo localmente (con datos de ejemplo)

1. `npm install` (solo la primera vez; instala `json-server`).
2. `npm run mock-api`
3. Abra `http://localhost:3001/index.html` en el navegador. Debe mostrar el
   mapa coloreado con el aviso "Datos de ejemplo".

No funciona abriendo `index.html` con doble clic: el navegador no permite que
una página abierta desde un archivo pida datos con `fetch`. Siempre hay que
abrirlo a través de un servidor como el de `npm run mock-api`.

Para probar el mensaje de error, cambie `CONFIG.FUENTE_DATOS` a
`http://localhost:3001/localidades` (la API de prueba en su propia ruta, como
será la real), recargue, y luego detenga `npm run mock-api` (Ctrl+C) y vuelva
a recargar.

## Cómo conectar la API real cuando esté lista

Dentro de `index.html`, al inicio del `<script>`, está esto:

```js
const CONFIG = {
  FUENTE_DATOS: "mock-api/datos_reales_localidades.json",
  // FUENTE_DATOS: "https://<dominio-consultorio>/api/geolocalizacion/localidades",
  DATOS_DE_EJEMPLO: false,
};
```

Hay que poner la URL real en `FUENTE_DATOS`. `DATOS_DE_EJEMPLO: true` muestra
un aviso de "datos de ejemplo" en el encabezado; úselo solo si apunta a
`mock-api/localidades.json`.

No hay que cambiar nada más. El resto del widget (coloreado, leyenda,
tooltips, manejo de errores) ya está escrito de forma genérica y no depende
de si la fuente es la API de prueba o la real.

Contrato esperado de esa API — debe responder un arreglo JSON así:

```json
[
  { "codigo_loc": "8", "nombre": "Kennedy", "cantidad": 196 },
  { "codigo_loc": "10", "nombre": "Engativá", "cantidad": 176 },
  { "codigo_loc": "13", "nombre": "Teusaquillo", "cantidad": null, "menos_de": 5 }
]
```

Las localidades con entre 1 y 4 personas se envían **sin el número exacto**
(`"cantidad": null, "menos_de": 5`) y el mapa muestra "menos de 5". Así nadie
puede deducir quién se inscribió en una localidad con muy pocas personas. Esto
tiene que hacerlo quien genera los datos (el script o la API), no el mapa: si
el número exacto viajara en el JSON, cualquiera podría verlo.

`codigo_loc` es el código DANE de la localidad (1 a 20), que es el campo que
cruza con la geometría del mapa — por eso es más confiable que cruzar por
nombre. Avísale a este contrato al subgrupo de registro: necesitan exponer un
endpoint GET con CORS habilitado para el dominio donde quede publicado este
widget (si quedan en dominios distintos), ya que el navegador bloquea por
defecto peticiones entre dominios distintos si el backend no lo permite
explícitamente.

## Datos reales: cómo se generan

Mientras no exista la API real, el mapa usa un conteo generado a partir del
Excel de inscripción del Consultorio con `scripts/agregar_localidades_reales.py`.

Regla de privacidad: **se pueden usar y publicar datos reales, pero solo como
conteo de personas por localidad**. El Excel y cualquier dato de una persona
nunca entran al repositorio (`*.xlsx` está en `.gitignore`).

El script lee ÚNICAMENTE:

- las columnas cuyo encabezado contiene "Localidad";
- "Número de Identificación" y "Hora de inicio", solo para quitar
  inscripciones repetidas de una misma persona (se conserva la más reciente).
  Se usan únicamente en memoria: nunca se imprimen ni se guardan.

El resto de columnas (nombre, teléfono, correo, etc.) nunca se cargan.

Para actualizar los datos (por ejemplo, con un Excel nuevo):

1. Desde la **raíz del repositorio** (no desde `widget/`), con un entorno
   virtual de Python (solo la primera vez: `python3 -m venv .venv` y
   `.venv/bin/pip install -r widget/scripts/requirements.txt`):

   ```bash
   .venv/bin/python widget/scripts/agregar_localidades_reales.py "/ruta/al/Excel.xlsx"
   ```

   Sobrescribe `widget/mock-api/datos_reales_localidades.json` e imprime en
   pantalla cuántas inscripciones repetidas quitó, qué localidades quedaron
   como "menos de 5" y los valores de localidad que no pudo emparejar con las
   20 oficiales (por ejemplo, de otras ciudades). Esos no se cuentan.

2. Revise el archivo generado (solo debe tener `codigo_loc`, `nombre`,
   `cantidad` y, a veces, `menos_de`) y súbalo con un commit: GitHub Pages lo
   publica solo.

El Excel nunca se copia dentro de la carpeta del proyecto: el script lo lee
desde donde esté (por ejemplo, el escritorio).

## Versión publicada (GitHub Pages)

El workflow `.github/workflows/pages.yml` (en la raíz del repositorio) publica
el widget cada vez que se suben cambios a `main` dentro de `widget/`. Solo
publica `index.html` y los dos archivos de conteo de `mock-api/` (el real y el
de ejemplo).

Dirección: https://consultorio-contable-javeriano.github.io/Modulo-Visualizacion/

Configuración (una sola vez, la hace un administrador del repositorio): en
GitHub, **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Cómo embeberlo en la página institucional

Una vez esté publicado en algún servidor (el de la FCEA, GitHub Pages, u otro):

```html
<iframe src="https://<url-del-widget>/index.html" width="100%" height="650" style="border:none;"></iframe>
```

## Pendiente por coordinar con el subgrupo de registro

- [ ] **URL real de la API** de solo lectura (endpoint GET), por ejemplo
      `https://<dominio-consultorio>/api/geolocalizacion/localidades`, para
      ponerla en `CONFIG.FUENTE_DATOS`.
- [ ] **Contrato de respuesta**: arreglo JSON
      `[{ "codigo_loc": "8", "nombre": "Kennedy", "cantidad": 196 }, ...]`,
      con `codigo_loc` = código de localidad 1–20 y `cantidad` = personas
      únicas (sin duplicados), siempre agregado por localidad. Localidades con
      1–4 personas: `"cantidad": null, "menos_de": 5` (ver arriba).
- [ ] **CORS habilitado** en el backend Spring Boot para el dominio donde se
      publique este widget (por ejemplo con `@CrossOrigin(origins = "...")` o
      una configuración global de CORS). Sin esto el navegador bloquea la
      petición y el widget muestra el mensaje de error.
- [ ] Definir qué hace la API con las personas que no son de Bogotá o no
      tienen localidad (no incluirlas en la respuesta).
- [ ] Confirmar que la API nunca devuelve datos a nivel de persona
      (Ley 1581 de 2012).

## Pendiente para las siguientes semanas (según el cronograma)

- Conectar a la API real una vez el módulo de registro la exponga (semana 9–10).
- Coordinar con el equipo de comunicaciones/web de la FCEA el embebido real en
  el sitio institucional (también semana 9–10, ligado al riesgo del PC3).
- Validar con el interlocutor que la agregación por localidad cumple el
  requisito de no exponer ubicaciones individuales.
