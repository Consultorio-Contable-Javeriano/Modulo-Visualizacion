// json-server necesita un objeto con "rutas"; este archivo envuelve los datos
// de ejemplo para que http://localhost:3001/localidades responda el mismo
// arreglo que mock-api/localidades.json (una sola fuente de datos sintéticos).
module.exports = () => ({ localidades: require("./localidades.json") });
