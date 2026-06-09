// ── CATÁLOGO DE CÓDIGOS DE BARRAS (ALIAS) ───────────────────────────────────
// Mapa de código de barras físico/comercial (EAN/UPC impreso en el producto)
// → código interno administrativo del inventario.
//
// IMPORTANTE: el CÓDIGO INTERNO sigue siendo el identificador PRINCIPAL del
// inventario (campo `c` en CATALOGO_INVENTARIO / `codigo` en
// CATALOGO_ARTICULOS_POR_AREA). Este archivo es SOLO un índice de búsqueda
// (alias): permite escanear/escribir el código de barras físico y resolverlo
// al código interno. No reemplaza ni modifica los catálogos existentes.
//
// FORMA:
//   window.CATALOGO_CODIGOS_BARRAS = {
//     "<codigo_de_barras>": { area: "<Snack|Tienda>", codigo: "<codigo_interno>" }
//   };
//
// REGLAS:
//   - La llave es el código de barras como STRING (respeta ceros a la izquierda).
//   - `codigo` es el código interno administrativo al que resuelve.
//   - `area` documenta a qué área pertenece (sirve para avisar si el usuario
//     tiene seleccionada el área equivocada).
//   - Un mismo producto puede tener varios códigos de barras → varias llaves
//     pueden apuntar al mismo código interno (relación muchos-a-uno).
//
// EJEMPLO (ilustrativo — NO son datos reales, no descomentar en producción):
//   window.CATALOGO_CODIGOS_BARRAS = {
//     "7501234567890": { area: "Snack",  codigo: "S-2380001" },
//     "7500000000017": { area: "Tienda", codigo: "T-001" }
//   };
//
// Por ahora el catálogo está VACÍO: se llenará cuando se tengan los códigos de
// barras reales de los productos. Mientras esté vacío, el Movimiento rápido
// funciona igual usando el código interno directamente.
window.CATALOGO_CODIGOS_BARRAS = {
};
