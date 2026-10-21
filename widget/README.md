# Widget de geolocalización — Consultorio Contable Javeriano

Mapa interactivo de las 20 localidades de Bogotá, coloreado según la cantidad
de personas atendidas por el Consultorio Contable Javeriano. Está hecho en
JavaScript con Leaflet sobre OpenStreetMap y se embebe por `<iframe>` en la
página institucional del Consultorio.

**Versión publicada:** https://consultorio-contable-javeriano.github.io/Modulo-Visualizacion/

Hoy muestra el conteo real de las inscripciones del Nivel 1 (segundo semestre
de 2026), generado a partir del Excel del Consultorio. Cuando el módulo de
registro exponga su API, el widget leerá los datos de ella cambiando una sola
línea (ver [Conectar la API real](#conectar-la-api-real)).

## Cómo usarlo

### Ver el mapa

1. Abra la [versión publicada](https://consultorio-contable-javeriano.github.io/Modulo-Visualizacion/)
   en cualquier navegador (computador o celular). No necesita instalar nada ni
   iniciar sesión.
2. Lea el encabezado: dice de qué son los datos y cuántas personas hay en
   total.
3. Mire los colores: entre más oscura la localidad, más personas atendidas.
   La leyenda (abajo a la derecha) dice qué rango corresponde a cada color.
4. Pase el cursor sobre una localidad (en celular, tóquela) para ver su nombre
   y su cantidad, junto al cursor y en el recuadro de arriba a la derecha. Si
   dice "menos de 5", la localidad tiene entre 1 y 4
   personas (ver [Privacidad](#privacidad-ley-1581-de-2012)).
5. Acerque o aleje con la rueda del mouse, con los botones **+** / **−** o
   con dos dedos en el celular. Arrastre para moverse. Sumapaz aparece al
   alejar el mapa hacia el sur.
6. Si sale un mensaje de error, pulse **Reintentar**. Si sale una advertencia
   en rojo, algunos registros llegaron mal y no se dibujaron; avise al equipo
   del módulo.

### Tareas frecuentes del equipo

| Quiero... | Vaya a |
|---|---|
| Probar el widget en mi computador | [Cómo probarlo localmente](#cómo-probarlo-localmente) |
| Actualizar el mapa con un Excel nuevo | [Actualizar los datos reales](#actualizar-los-datos-reales) |
| Cambiar el texto del encabezado o la fuente de datos | [Configuración](#configuración) |
| Conectar el mapa a la API del registro | [Conectar la API real](#conectar-la-api-real) |
| Poner el mapa en otra página web | [Cómo embeberlo](#cómo-embeberlo-en-la-página-institucional) |

## Qué muestra

- **Mapa coroplético:** cada localidad se colorea según su cantidad de
  personas atendidas (6 rangos, de claro a oscuro, calculados a partir de los
  datos). Al pasar el cursor se ve el nombre y la cantidad.
- **Encabezado:** de qué son los datos (`CONFIG.DESCRIPCION_DATOS`) y el total
  de personas.
- **"Menos de 5":** las localidades con entre 1 y 4 personas no muestran el
  número exacto (ver [Privacidad](#privacidad-ley-1581-de-2012)). Por eso,
  cuando hay localidades así, el total se muestra como "al menos N personas".
- **Encuadre inicial sobre la zona urbana.** Sumapaz, casi toda rural, queda
  fuera del encuadre inicial para que las demás localidades no se vean
  diminutas; se ve al alejar el mapa.
- **Manejo de errores:**
  - Si la fuente de datos no responde, se muestra un mensaje con un botón
    **Reintentar**.
  - Si llegan registros mal formados (código de localidad que no existe,
    cantidad que no es un número, localidad repetida), se ignoran y se muestra
    una advertencia en rojo en el encabezado (con detalle en la consola del
    navegador). Las localidades válidas se dibujan igual.

## Privacidad (Ley 1581 de 2012)

- La información se muestra **siempre agregada por localidad**, nunca por
  dirección ni por persona.
- Se pueden usar y publicar datos reales, pero **solo como conteo de personas
  por localidad**. El Excel del Consultorio y cualquier dato de una persona
  nunca entran al repositorio (`*.xlsx` está en `.gitignore`).
- Las localidades con **entre 1 y 4 personas** se publican sin el número
  exacto (`"cantidad": null, "menos_de": 5`) y el mapa muestra "menos de 5".
  Con números tan pequeños, alguien que conozca a la persona podría deducir que
  se inscribió. Esta reserva la hace quien genera los datos (el script o la
  API), no el mapa: si el número exacto viajara en el JSON, cualquiera podría
  verlo.
- Se cuentan **personas únicas**: si alguien se inscribió varias veces, cuenta
  una sola vez.

## Archivos

```
widget/
  index.html                          el widget completo
  mock-api/
    datos_reales_localidades.json     conteo real por localidad (lo que muestra el mapa hoy)
    localidades.json                  datos de ejemplo (sintéticos), para pruebas
    db.js                             adaptador para servir localidades.json con json-server
  scripts/
    agregar_localidades_reales.py     genera el conteo real a partir del Excel
    requirements.txt                  dependencias de Python del script
  package.json                        define `npm run mock-api` (servidor local)
```

- Los límites de las 20 localidades (fuente: repositorio público
  `decolector/bta-geodata`, recortado y simplificado) van embebidos dentro de
  `index.html` (constante `LOCALIDADES_GEOJSON`), porque es geografía fija.
- La carpeta se llama `mock-api` porque simula lo que más adelante entregará
  la API real.

## Configuración

Todo lo que se puede ajustar está al inicio del `<script>` de `index.html`:

```js
const CONFIG = {
  FUENTE_DATOS: "mock-api/datos_reales_localidades.json",
  DATOS_DE_EJEMPLO: false,
  DESCRIPCION_DATOS: "Inscripciones Nivel 1 · segundo semestre de 2026",
};
```

- `FUENTE_DATOS`: de dónde se leen los datos (un archivo junto a la página o
  la URL de una API).
- `DATOS_DE_EJEMPLO`: en `true` muestra el aviso "Datos de ejemplo
  (sintéticos)". Úselo solo si `FUENTE_DATOS` apunta a
  `mock-api/localidades.json`.
- `DESCRIPCION_DATOS`: texto del encabezado que dice de qué son los datos.
  **Actualícelo cuando cambien los datos** (otro curso, otro semestre).

## Cómo probarlo localmente

Todos los comandos de esta sección se ejecutan dentro de la carpeta `widget/`.

1. `npm install` (solo la primera vez; instala `json-server`).
2. `npm run mock-api`
3. Abra `http://localhost:3001/index.html` en el navegador.

No funciona abriendo `index.html` con doble clic: el navegador no permite que
una página abierta desde un archivo pida datos con `fetch`. Siempre hay que
abrirlo a través de un servidor como el de `npm run mock-api`.

Pruebas útiles (cambiando `CONFIG.FUENTE_DATOS` temporalmente, y
devolviéndolo a `"mock-api/datos_reales_localidades.json"` antes de hacer
commit):

- **Datos de ejemplo:** `"mock-api/localidades.json"`.
- **API en otro servidor:** `"http://localhost:3001/localidades"`, que sirve
  los datos de ejemplo como lo haría la API real.
- **Error y botón Reintentar:** una dirección donde no haya nada, por ejemplo
  `"http://localhost:3999/localidades"`.

## Actualizar los datos reales

Mientras no exista la API real, el conteo se genera a partir del Excel de
inscripción con `scripts/agregar_localidades_reales.py`. El script lee
ÚNICAMENTE:

- las columnas cuyo encabezado contiene "Localidad";
- "Número de Identificación" y "Hora de inicio", solo para quitar
  inscripciones repetidas de una misma persona (se conserva la más reciente).
  Se usan únicamente en memoria: nunca se imprimen ni se guardan.

El resto de columnas (nombre, teléfono, correo, etc.) nunca se cargan.

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

2. Si los datos son de otro curso o semestre, actualice
   `CONFIG.DESCRIPCION_DATOS` en `index.html`.
3. Revise el archivo generado (solo debe tener `codigo_loc`, `nombre`,
   `cantidad` y, a veces, `menos_de`) y súbalo con un commit: GitHub Pages lo
   publica solo.

El Excel nunca se copia dentro de la carpeta del proyecto: el script lo lee
desde donde esté (por ejemplo, el escritorio).

## Conectar la API real

Cuando el módulo de registro exponga su API, basta con poner su URL en
`CONFIG.FUENTE_DATOS`, por ejemplo
`"https://<dominio-consultorio>/api/geolocalizacion/localidades"`. No hay que
cambiar nada más: el coloreado, la leyenda, el total y el manejo de errores
funcionan igual con cualquier fuente que respete el contrato.

### Contrato de la API

`GET` que responde un arreglo JSON, una entrada por localidad:

```json
[
  { "codigo_loc": "8", "nombre": "Kennedy", "cantidad": 196 },
  { "codigo_loc": "10", "nombre": "Engativá", "cantidad": 176 },
  { "codigo_loc": "13", "nombre": "Teusaquillo", "cantidad": null, "menos_de": 5 }
]
```

- `codigo_loc`: código DANE de la localidad, de `"1"` a `"20"`. Es el campo
  que cruza con la geometría del mapa (más confiable que cruzar por nombre).
- `nombre`: nombre de la localidad.
- `cantidad`: número entero de personas únicas (sin duplicados), o `null` si
  la localidad tiene entre 1 y 4 personas.
- `menos_de`: solo cuando `cantidad` es `null`; vale `5`.

Si la API está en un dominio distinto al del widget, debe tener **CORS
habilitado** para el dominio del widget; si no, el navegador bloquea la
petición y el widget muestra el mensaje de error.

## Publicación (GitHub Pages)

El workflow `.github/workflows/pages.yml` (en la raíz del repositorio) publica
el widget cada vez que se suben cambios a `main` dentro de `widget/`. Solo
publica `index.html` y los dos archivos de conteo de `mock-api/` (el real y el
de ejemplo); nada más del repositorio.

Configuración (una sola vez, ya hecha): en GitHub, **Settings → Pages →
Build and deployment → Source: GitHub Actions**.

## Cómo embeberlo en la página institucional

```html
<iframe src="https://consultorio-contable-javeriano.github.io/Modulo-Visualizacion/"
        width="100%" height="650" style="border:none;"></iframe>
```

Si más adelante se publica en otro servidor (por ejemplo, el de la FCEA), se
cambia la dirección en `src`.

## Pendiente por coordinar con el subgrupo de registro

- [ ] **URL real de la API** de solo lectura (endpoint GET), para ponerla en
      `CONFIG.FUENTE_DATOS`.
- [ ] **Contrato de respuesta** según la sección
      [Contrato de la API](#contrato-de-la-api), incluida la reserva de
      "menos de 5" y el conteo de personas únicas.
- [ ] **CORS habilitado** en el backend Spring Boot para el dominio del widget
      (hoy `https://consultorio-contable-javeriano.github.io`), por ejemplo con
      `@CrossOrigin(origins = "...")` o una configuración global de CORS.
- [ ] Definir qué hace la API con las personas que no son de Bogotá o no
      tienen localidad (no incluirlas en la respuesta).
- [ ] Confirmar que la API nunca devuelve datos a nivel de persona
      (Ley 1581 de 2012).

## Pendiente para las siguientes semanas (según el cronograma)

- Conectar a la API real una vez el módulo de registro la exponga (semana 9–10).
- Coordinar con el equipo de comunicaciones/web de la FCEA el embebido real en
  el sitio institucional (también semana 9–10, ligado al riesgo del PC3).
- Validar con el interlocutor que la agregación por localidad (y la reserva de
  "menos de 5") cumple el requisito de no exponer ubicaciones individuales.
