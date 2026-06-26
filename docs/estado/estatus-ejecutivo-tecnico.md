# Estatus Ejecutivo-Técnico — Zoo Tamatán Inventario V3.0

**Documento maestro estratégico**
**Fecha:** 25 de junio de 2026
**Ámbito:** Estado actual + diagnóstico PR C (trazabilidad / factor-caja) + NUT-A (Nutrición Light)
**Naturaleza:** Solo documentación. No describe trabajo implementado en esta sesión; describe el estado verificado y el plan propuesto.

> Este documento integra la fotografía técnica del proyecto y el diagnóstico de las dos próximas líneas de trabajo (Códigos PR C y Nutrición NUT-A). Sus versiones derivadas son:
> - `docs/estado/estatus-ejecutivo-tecnico.pdf` (mismo contenido, formato sobrio para impresión/distribución).
> - `docs/nutricion/diagnostico-nutricion-light.md` (profundiza la Sección 5).
> - `docs/roadmap/roadmap-codigos-y-nutricion.md` (profundiza la Sección 6).

---

## 1. Estado actual del proyecto (verificado)

Estado confirmado por inspección de `git` y del código el 25 de junio de 2026:

| Concepto | Valor verificado |
|---|---|
| Rama de trabajo | `claude/vigorous-panini-b40936` (worktree), árbol limpio |
| `origin/main` | `64cea7a` — `docs(bitacora): documentar APP.logger.getLogs() como async` |
| `origin/gh-pages` | `277e717` — deploy vinculación de códigos desde Movimiento rápido |
| PRs abiertos | Ninguno |
| Repo | Limpio (sin cambios staged, modificados ni sin trackear) |

Hitos relevantes ya cerrados:

- **PR #24 (docs getLogs async)** — cerrado en `main 64cea7a`. Docs-only, sin deploy.
- **PR #26 / Códigos-A** — en producción. Persistencia de aliases de código de barras:
  store `zoo_tamatán_codigos_barras_v1`, `getCodigosBarras()`, `saveCodigosBarras()`,
  respaldo export/import de aliases, y merge runtime en `window.CATALOGO_CODIGOS_BARRAS`.
- **PR #27 / Códigos-B** — en producción. UI para vincular códigos físicos no reconocidos
  desde Movimiento rápido, autocompletar por nombre/código interno, botón "Cambiar vínculo",
  cancelación que restaura la tarjeta, sobrescritura que registra WARN, `escapeHtml` en Scanner
  y escape de la Bitácora.

Estado funcional de partida para lo que sigue:

- Códigos-A y Códigos-B están en producción.
- `data/catalogos/catalogo_codigos_barras.js` **sigue vacío** (`window.CATALOGO_CODIGOS_BARRAS = {}`),
  sin aliases reales estáticos; los aliases viven en `localStorage` bajo `zoo_tamatán_codigos_barras_v1`.
- **No existe** `codigoBarrasLeido` en ningún módulo (verificado: 0 coincidencias en el repo).
- **No existe** factor / caja / presentación.
- **No existe** módulo Nutrición.
- **No se ha tocado** `calcularStockTeorico` para PR C.
- Salidas-B / `calcularStockTeorico` async queda como fase futura separada.

---

## 2. Arquitectura actual de códigos de barras

Modelo de alias **código de barras físico → código interno administrativo**. El código interno
sigue siendo el identificador principal del inventario; el de barras es solo un índice de búsqueda.

### 2.1 Persistencia (LocalStore)

- Clave canónica: `zoo_tamatán_codigos_barras_v1` (con acento exacto), registrada en
  `js/data/LocalStore.js`.
- Contrato async (devuelve promesas desde el día 1, aunque hoy resuelva sobre `localStorage`):
  - `getCodigosBarras() -> Promise<{ [barcode]: alias }>` — lee un **MAPA objeto**, no un array
    (`leerMapa`, default `{}`).
  - `saveCodigosBarras(obj) -> Promise<void>`.

### 2.2 Forma del alias

```js
window.CATALOGO_CODIGOS_BARRAS = {
  "<codigo_de_barras>": { area: "<Snack|Tienda>", codigo: "<codigo_interno>" }
};
```

- La llave es el código de barras como `String` (respeta ceros a la izquierda).
- `codigo` es el código interno administrativo destino.
- `area` documenta a qué área pertenece (sirve para avisar si el área seleccionada es la equivocada).
- Relación muchos-a-uno: varias llaves pueden apuntar al mismo código interno.

### 2.3 Reflejo en runtime (HTML)

- El HTML inicializa `window.CATALOGO_CODIGOS_BARRAS ||= {}` y luego mezcla lo persistido:
  `repo.getCodigosBarras().then(rt => Object.assign(window.CATALOGO_CODIGOS_BARRAS, rt))`
  (regla **runtime-gana**), de modo que el catálogo estático vacío + lo guardado conviven.
- `guardarAlias({ barcode, area, codigo })` persiste vía `repo.saveCodigosBarras` y refleja en
  vivo en `window.CATALOGO_CODIGOS_BARRAS` para que `resolverCodigo` lo vea sin recargar.

### 2.4 Resolución en Movimiento rápido (`js/modScanner.js`)

`resolverCodigo(area, escaneado)` sigue este orden:

1. ¿Es código interno del área? → devuelve el artículo **con `barcode: ''`**.
2. Si no, ¿está en `CATALOGO_CODIGOS_BARRAS`? → resuelve al interno y lo busca en el área;
   devuelve el artículo **con `barcode: <código físico escaneado>`** (`modScanner.js:89`).
3. Si el alias existe pero apunta a otra área → `{ _mismatch: <área> }` (aviso, no registra).
4. Si nada coincide → `null` (abre el mini-formulario de vinculación).

### 2.5 UI de vinculación (PR #27)

- Mini-formulario al no reconocer un código: autocompletar por nombre o código interno del área
  (hasta 8 sugerencias, texto escapado con `escapeHtml`).
- Botón **"Cambiar vínculo"** (`cambiarVinculo()`): reabre el formulario para re-vincular un código
  ya asociado, reutilizando el mismo `barcode` y el flujo `vincular()` → `guardarAlias`.
- Sobrescritura de un alias existente: `confirm()` + registro **WARN** en bitácora; si se cancela,
  nada cambia y se restaura la tarjeta vigente.

### 2.6 Respaldo (`js/modRespaldo.js`)

- `CLAVE_CODIGOS_BARRAS = 'zoo_tamatán_codigos_barras_v1'` se respalda **aparte** del loop de las
  5 claves array, porque su valor es un objeto-mapa.
- Exportación: incluye los aliases en `datos[...]` y `conteos.codigosBarras = Object.keys(aliases).length`.
- Importación: valida que sea objeto (no array, no null) con `hayAlias`; persiste y refleja en vivo con
  `window.CATALOGO_CODIGOS_BARRAS = Object.assign(window.CATALOGO_CODIGOS_BARRAS || {}, aliasObj)`.

### 2.7 Catálogo estático

`data/catalogos/catalogo_codigos_barras.js` **sigue vacío** a propósito: documenta la forma y las
reglas, pero `window.CATALOGO_CODIGOS_BARRAS = {}`. Mientras esté vacío, Movimiento rápido funciona
igual usando el código interno directamente; los aliases reales se acumulan en runtime/`localStorage`.

---

## 3. Diagnóstico PR C — trazabilidad avanzada

### 3.1 Hallazgo central (verificado en código)

Cuando un movimiento se resuelve **por alias**, el dato del código físico **ya existe** en memoria
pero **se descarta al persistir**:

- `resolverCodigo` adjunta `barcode: <código físico>` al artículo resuelto por alias
  (`js/modScanner.js:89`), y `artActual` lo conserva (`modScanner.js:33`, asignado en `buscar()`).
- La tarjeta verde incluso lo muestra ("Código de barras: …") y ofrece "Cambiar vínculo"
  (`modScanner.js:145-146`).
- Pero al construir el objeto `articulo` que se envía a registrar (`modScanner.js:258-264`) **solo**
  se copian `descripcion`, `codigo`, `unidad`, `precio`, `cantidad`. El `barcode` **no** se incluye
  → se pierde la trazabilidad de "qué código físico se escaneó realmente".

### 3.2 Por qué es aditivo y de bajo riesgo

- El dato ya está disponible (`artActual.barcode`); no requiere nueva resolución ni nuevas fuentes.
- La capa de Salidas persiste el array tal cual: `articulos: [...articulos]` (`js/modSalidas.js:180`),
  copia superficial que **conserva campos extra** del objeto artículo. Por tanto, agregar un campo
  nuevo en el objeto que arma `modScanner` fluye hacia el registro **sin** reescribir la firma de
  Salidas.
- Es un campo nuevo opcional: los registros viejos sin él siguen siendo válidos (ausencia = `''`).

### 3.3 Alcance de PR C-1 (`codigoBarrasLeido`)

- Propagar `codigoBarrasLeido` en el objeto `articulo` que arma Movimiento rápido, tomándolo de
  `artActual.barcode` (vacío cuando se buscó por código interno directo).
- Verificar que el campo sobreviva en la ruta de **entrada rápida** (`registrarEntradaRapida`) igual
  que en la de salida antes de darlo por cerrado (la ruta de salida ya lo conserva por el spread).
- **NO** tocar `calcularStockTeorico` en C-1.
- **NO** cambiar cantidades ni el cálculo de stock en C-1: es puramente trazabilidad (un campo
  informativo que viaja con el movimiento).
- factor / caja / presentación va **después** (PR C-2 / C-3), no en C-1.

### 3.4 Resumen de riesgo C-1

Bajo. Es un campo aditivo, el dato ya existe en memoria, la persistencia de Salidas lo arrastra por
el spread, y no altera ninguna aritmética de inventario. El punto a verificar es la ruta de entrada.

---

## 4. Modelo futuro de factor / caja / presentación

Objetivo: registrar que un escaneo de "1 caja" equivale a N unidades base, sin contaminar el modelo
simple de aliases ni la aritmética actual de stock.

Principios de diseño propuestos:

- Los **aliases se mantienen simples**: `{ area, codigo }`. No se les agrega factor.
- El factor vive en un **store separado futuro**: `zoo_tamatán_factor_cajas_v1`.
- El factor es **barcode-scoped**: se asocia al código de barras escaneado (una caja tiene su propio
  código), no al artículo interno; así un mismo artículo puede tener presentación "pieza" y "caja".
- El **stock se mantiene en unidad base**. El factor no cambia cómo se almacena el stock; solo
  cómo se interpreta una lectura.
- El factor se **aplica en tiempo de registro**: al registrar el movimiento se multiplica la cantidad
  escaneada por el factor de esa presentación para obtener unidades base. El stock sigue contándose
  en unidad base.
- **Salidas-B queda separado**: la migración de `calcularStockTeorico` a async (y sus consumidores)
  es una fase independiente y no es prerequisito del factor.

Secuencia: primero el store del factor (C-2), luego su aplicación a los movimientos (C-3). Ver Sección 6.

---

## 5. NUT-A — Nutrición Light (diagnóstico resumido)

> Profundizado en `docs/nutricion/diagnostico-nutricion-light.md`.

Alcance propuesto: un **inventario operativo de alimentos**, no un sistema científico de dietas.

- Entradas de proveedor (recepción de alimento).
- Salidas diarias (consumo operativo del día).
- Stock de nutrición (existencias de alimentos).
- Unidades operativas: **kg / pieza / manojo**.
- Scanner reutilizable (mismo patrón que Movimiento rápido).
- Ticket de báscula (peso registrado en la recepción/salida).
- Destino / uso operativo simple (a qué se destina la salida), **sin** modelo nutricional científico.

Explícitamente **fuera de alcance** de NUT-A: tablas de requerimientos por especie, formulación de
dietas, balance de nutrientes, cálculos veterinarios. Eso es una fase científica posterior, si llega.

Principio rector: **no mezclar Nutrición con Salidas generales.** Nutrición es un inventario operativo
paralelo con sus propias claves de almacenamiento, su propio stock y sus propios reportes.

---

## 6. Roadmap

> Profundizado en `docs/roadmap/roadmap-codigos-y-nutricion.md`.

**Línea Códigos (trazabilidad / factor):**

- **PR C-1** — `codigoBarrasLeido`: propagar el código físico escaneado al registro. Aditivo, sin
  tocar `calcularStockTeorico`, sin cambiar cantidades.
- **PR C-2** — factor store: crear `zoo_tamatán_factor_cajas_v1` (factor barcode-scoped). Solo
  persistencia + UI de captura del factor; aún no aplica a movimientos.
- **PR C-3** — factor aplicado a movimientos: multiplicar cantidad escaneada por factor al registrar,
  manteniendo stock en unidad base.

**Línea Nutrición:**

- **NUT-A** — documentación / diagnóstico (este bloque; sin código).
- **NUT-B** — catálogo de alimentos.
- **NUT-C** — entradas de nutrición.
- **NUT-D** — salidas de nutrición.
- **NUT-E** — stock / reportes de nutrición.
- **NUT-F** — ticket de báscula avanzado.

**Fase futura separada (no en este roadmap inmediato):** Salidas-B (`calcularStockTeorico` async +
sus 4 consumidores) y Entradas (caché + debounce).

---

## 7. Riesgos

| # | Riesgo | Descripción | Mitigación propuesta |
|---|---|---|---|
| 1 | Stock por nombre | El emparejamiento de salidas usa `descripcion`/nombre como clave (`modSalidas.js`); nombres no normalizados fragmentan el stock. | Documentar la convención de nombres; a futuro, apoyarse más en código interno. |
| 2 | Respaldo | Olvidar exportar antes de migrar de origen (`localhost` vs `github.io`) pierde aliases/datos; el `localStorage` está particionado por origen. | Reforzar el hábito de respaldo; el import ya hace respaldo de seguridad automático. |
| 3 | Unidades | Mezclar kg/pieza/manojo (Nutrición) o pieza/caja (factor) sin disciplina produce conteos erróneos. | Unidad base explícita; factor barcode-scoped; validación en captura. |
| 4 | Trazabilidad | Hoy se pierde `codigoBarrasLeido`; sin él no se puede auditar qué código físico generó un movimiento. | PR C-1 (aditivo). |
| 5 | Capacitación | Nuevas funciones (vinculación, factor, nutrición) requieren entrenamiento del personal de almacén. | Guías cortas por función; reutilizar el patrón de Movimiento rápido para reducir curva. |
| 6 | Báscula / ticket | Captura manual del peso es propensa a error; integración avanzada es compleja. | NUT-A: ticket simple (peso manual); báscula avanzada se aísla en NUT-F. |
| 7 | No mezclar Nutrición con Salidas generales | Reutilizar las claves/flujo de Salidas para alimentos contaminaría el inventario general y los reportes. | Nutrición con claves, stock y reportes propios desde el inicio. |

---

## 8. Recomendación final

- **Siguiente paso inmediato recomendado:** elegir entre **PR C-1** (`codigoBarrasLeido`) o **NUT-A**
  (documentación/diagnóstico, ya cubierto por estos documentos) según prioridad operativa. Si la
  prioridad es cerrar trazabilidad de códigos antes de abrir un módulo nuevo, **PR C-1** es la opción
  de menor riesgo y mayor retorno inmediato.
- **No implementar factor todavía** (C-2/C-3 van después de C-1).
- **No implementar Nutrición en código todavía** (NUT-B en adelante son fases posteriores).
- Salidas-B (`calcularStockTeorico` async) permanece como fase futura separada y no bloquea lo anterior.

> Decisión pendiente del responsable: aprobar el orden PR C-1 → NUT-A (o invertirlo). Este documento
> no implementa nada; solo deja el diagnóstico listo para esa decisión.
