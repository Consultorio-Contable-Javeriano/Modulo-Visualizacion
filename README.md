# Módulo de geolocalización — Consultorio Contable Javeriano

Módulo (2) del proyecto "Implementación del sistema integrado de registro,
geolocalización y gestión SOFI" (Práctica Social Universitaria, Ingeniería de
Sistemas, Pontificia Universidad Javeriana).

Es un widget en JavaScript con Leaflet sobre OpenStreetMap que muestra un
mapa coroplético de las 20 localidades de Bogotá, coloreado por cantidad de
personas atendidas. Se embebe por `<iframe>` en la página institucional del
Consultorio y consume una API de solo lectura del módulo de registro.

Todo el código está en [`widget/`](widget/). Instrucciones, contrato de la
API y pendientes con el subgrupo de registro en
[`widget/README.md`](widget/README.md).

## Privacidad (Ley 1581 de 2012)

- La información se muestra siempre agregada por localidad, nunca por
  dirección ni por persona.
- Este repositorio solo contiene datos sintéticos de ejemplo. El Excel del
  Consultorio (`*.xlsx`) y cualquier conteo derivado de datos reales
  (`datos_reales_localidades.json`) están en `.gitignore` y nunca deben
  subirse.
