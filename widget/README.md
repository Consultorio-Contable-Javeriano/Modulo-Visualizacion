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
- `mock-api/db.json` — datos de ejemplo (sintéticos, no son información real
  de personas atendidas) usados para levantar una API de prueba local.
- `package.json` — define `npm run mock-api` para levantar esa API de prueba
  y `npm run api-datos-reales` para la prueba local con conteos reales (ver
  abajo).
- `scripts/agregar_localidades_reales.py` — genera los conteos reales por
  localidad a partir del Excel del Consultorio (solo para pruebas locales).

Todos los comandos de este README se ejecutan dentro de la carpeta `widget/`,
salvo que se indique otra cosa.

## Cómo probarlo localmente (con datos de ejemplo)

1. `npm install` (instala `json-server`, que simula una API real a partir de
   un archivo JSON — así se prueba el mismo código de `fetch` que se usará
   con la API real, no solo un objeto fijo en el código).
2. `npm run mock-api` — levanta la API de prueba en `http://localhost:3001/localidades`.
3. Abre `index.html` en el navegador (doble clic, o sírvelo con cualquier
   servidor estático). Debe mostrar el mapa coloreado; si cierras la API de
   prueba y recargas, debe aparecer un mensaje de error en vez de romperse.

## Cómo conectar la API real cuando esté lista

Dentro de `index.html`, al inicio del `<script>`, está esto:

```js
const CONFIG = {
  FUENTE_DATOS: "http://localhost:3001/localidades",
  // Cuando el módulo de registro exponga la API real, cambiar SOLO esta línea:
  // FUENTE_DATOS: "https://<dominio-consultorio>/api/geolocalizacion/localidades",
};
```

Ese es el único cambio necesario. El resto del widget (coloreado, leyenda,
tooltips, manejo de errores) ya está escrito de forma genérica y no depende
de si la fuente es la API de prueba o la real.

Contrato esperado de esa API — debe responder un arreglo JSON así:

```json
[
  { "codigo_loc": "8", "nombre": "Kennedy", "cantidad": 196 },
  { "codigo_loc": "10", "nombre": "Engativá", "cantidad": 176 }
]
```

`codigo_loc` es el código DANE de la localidad (1 a 20), que es el campo que
cruza con la geometría del mapa — por eso es más confiable que cruzar por
nombre. Avísale a este contrato al subgrupo de registro: necesitan exponer un
endpoint GET con CORS habilitado para el dominio donde quede publicado este
widget (si quedan en dominios distintos), ya que el navegador bloquea por
defecto peticiones entre dominios distintos si el backend no lo permite
explícitamente.

## Cómo probarlo con una distribución real (sin usar datos reales en el repo)

Mientras no exista la API real, se puede generar una distribución más
realista a partir del Excel del Consultorio. El script lee ÚNICAMENTE las
columnas cuyo encabezado contiene "Localidad" (el resto de columnas —nombre,
identificación, teléfono, correo, etc.— nunca se cargan) y produce solo un
conteo por localidad.

1. Desde la **raíz del repositorio** (no desde `widget/`), con un entorno
   virtual de Python (solo la primera vez: `python3 -m venv .venv` y
   `.venv/bin/pip install -r widget/scripts/requirements.txt`):

   ```bash
   .venv/bin/python widget/scripts/agregar_localidades_reales.py "/ruta/al/Excel.xlsx"
   ```

   Genera `widget/datos_reales_localidades.json` e imprime en pantalla los
   valores de localidad que no pudo emparejar con las 20 oficiales (por
   ejemplo, localidades de otras ciudades). Esos no se cuentan.

   El archivo usa el mismo formato que `mock-api/db.json`
   (`{"localidades": [...]}`) para que `json-server` lo sirva igual: la ruta
   `/localidades` responde exactamente el arreglo que espera el widget.

2. Ese archivo está en `.gitignore` (igual que cualquier `.xlsx`): no se sube.
   Para comprobarlo: `git check-ignore -v widget/datos_reales_localidades.json`.
3. `npm run api-datos-reales` — lo sirve en `http://localhost:3002/localidades`.
4. Cambie **temporalmente** `CONFIG.FUENTE_DATOS` en `index.html` a
   `http://localhost:3002/localidades` y abra el widget.
5. Al terminar, **devuelva** `CONFIG.FUENTE_DATOS` a
   `http://localhost:3001/localidades` antes de hacer commit, para que el
   repositorio funcione solo con datos sintéticos.

Limitación: como el script no puede leer el número de identificación, no
elimina inscripciones duplicadas de una misma persona. Para la prueba visual
esto es aceptable; la API real del registro sí debería contar personas únicas.

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
      únicas (sin duplicados), siempre agregado por localidad.
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
