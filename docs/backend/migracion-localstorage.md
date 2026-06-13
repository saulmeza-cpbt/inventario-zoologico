# Migración desde localStorage y capa de persistencia — Fase 6

> Parte del paquete de diseño de la Fase 6. Índice en [README.md](README.md).
> Documento de **diseño**: no toca `localStorage`, no agrega código a producción.

Contiene: **§2** mapeo de las claves actuales a tablas + estrategia de seed, y **§6** la capa de
persistencia (`DataStore` / `LocalStore` / `ApiStore`) que permite migrar sin reescribir los módulos.

---

## 2. Mapeo desde localStorage actual

| Clave localStorage actual | → Tabla cabecera | → Tabla detalle | Notas de migración |
|---|---|---|---|
| `zoo_tamatán_entradas_v3` | `entradas` | `entrada_articulos` | `datos.*` → `folio_documento` + columnas dedicadas + resto a `datos_extra` (JSONB). `tipo` se conserva tal cual. |
| `zoo_tamatán_salidas_v1` | `salidas` | `salida_articulos` | `area` → `area_origen_id` (lookup por nombre). `articulos[].descripcion` → `descripcion`. |
| `zoo_tamatán_solicitudes_v1` | `solicitudes` | `solicitud_articulos` | `estado` se conserva con los mismos 4 valores. `folio` es físico (SP-). |
| `zoo_tamatán_levantamientos_v1` | `levantamientos` | `levantamiento_articulos` | `resumen{}` → `resumen` JSONB. `diferencia` recalculable. |
| `zoo_tamatán_bitacora_v3` | `bitacora` | — | `msg`→`mensaje`. `tsISO` es la fuente de verdad temporal; `ts` (locale) se descarta o se reconstruye. `usuario_id = NULL` para datos heredados. |
| `CATALOGO_INVENTARIO` (JS) | `articulos` | — | `c`→`codigo_interno`, `n`→`nombre`, `u`→`unidad`, `p`→`precio_referencia`, `e`→`existencia_inicial`. |
| `CATALOGO_ARTICULOS_POR_AREA` (JS) | `articulos` (upsert) | — | Backfill de artículos del maestro que no estén en la base; `precio_referencia`/`existencia_inicial` = 0. |
| `CATALOGO_CODIGOS_BARRAS` (JS) | `codigos_barras` | — | clave (barcode)→`codigo_barras`; `.codigo`→resuelve a `articulo_id`; `.area` se valida contra el área del artículo. |

**Vehículo de carga inicial:** el JSON que ya produce `modRespaldo` (`{ _meta, datos: { <5 claves> } }`)
es exactamente el insumo de un script de importación único (seed). No hay que inventar formato nuevo.

**Reglas de transformación clave durante el seed:**
- Resolver `area` (texto) → `area_id` por nombre exacto (las 5 áreas ya son fijas).
- Resolver `codigo`/`descripcion` → `articulo_id` por `codigo_interno`; si no existe, dejar `NULL` y conservar el texto.
- Conservar `id` originales (`ent-…`, `sal-…`) en una columna `id_legado` opcional para trazabilidad/idempotencia del seed.

> El destino de cada campo (`folio_documento`, `datos_extra`, `id_legado`, etc.) está definido en
> [modelo-datos.md](modelo-datos.md) §3 y §4.

---

## 6. Capa de persistencia futura (lo más importante de esta fase)

**Objetivo:** que hoy siga funcionando con `localStorage` y mañana cambie a API **sin reescribir los módulos**.

### El problema a evitar

Hoy `localStorage` es **síncrono** y cada módulo lo toca directo (`localStorage.getItem(KEY)`).
Una API es **asíncrona** (`fetch` → `Promise`). Si la capa de datos se diseña síncrona, **toda la UI
habría que reescribirla** al migrar. La regla de oro:

> 🔑 **La capa de datos debe ser asíncrona (basada en Promesas) desde el día 1, aún sobre `localStorage`.**
> Los módulos hacen `await repo.getSalidas()` hoy (resuelve al instante) y `await repo.getSalidas()`
> mañana (resuelve por red). **La firma no cambia.**

### Arquitectura propuesta: un contrato, dos implementaciones

```
                 ┌──────────────────────────────┐
   Módulos UI ── │  DataStore  (contrato/interfaz)│  ← los módulos solo conocen ESTO
 (createModX)    └──────────────┬───────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                     ▼
      LocalStore (hoy)                       ApiStore (mañana)
   localStorage + Promise.resolve         fetch() a /entradas, /salidas…
   stock calculado en cliente             stock desde GET /stock (vista SQL)
```

### El contrato (mismas funciones que pediste)

```js
// data/store/DataStore.js — CONTRATO (documentado; JS no tiene interfaces formales).
// Toda función devuelve Promise. Ningún módulo de UI toca localStorage ni fetch directamente.
//
//   getEntradas(filtro?)          -> Promise<Entrada[]>
//   saveEntrada(entrada)          -> Promise<Entrada>       (asigna folio)
//   getSalidas(filtro?)           -> Promise<Salida[]>
//   saveSalida(salida)            -> Promise<Salida>
//   getSolicitudes(filtro?)       -> Promise<Solicitud[]>
//   saveSolicitud(s)              -> Promise<Solicitud>
//   updateSolicitudEstado(id, e)  -> Promise<void>
//   getLevantamientos(filtro?)    -> Promise<Levantamiento[]>
//   saveLevantamiento(l)          -> Promise<Levantamiento>
//   getStock(area)                -> Promise<StockRow[]>    (calc. cliente HOY / vista SQL MAÑANA)
//   getBitacora(filtro?)          -> Promise<Evento[]>
//   registrarBitacora(evento)     -> Promise<void>
//   exportarTodo()                -> Promise<Payload>       (respaldo)
//   importarTodo(payload)         -> Promise<Resumen>
```

### Implementación de hoy (envuelve la lógica actual, sin cambiarla)

```js
// data/store/LocalStore.js
window.createLocalStore = ({ calcularStockTeorico } = {}) => {
  const KEYS = {
    entradas:       'zoo_tamatán_entradas_v3',
    salidas:        'zoo_tamatán_salidas_v1',
    solicitudes:    'zoo_tamatán_solicitudes_v1',
    levantamientos: 'zoo_tamatán_levantamientos_v1',
    bitacora:       'zoo_tamatán_bitacora_v3',
  };
  const leer    = (k) => { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch { return []; } };
  const escribir= (k, d) => { try { localStorage.setItem(k, JSON.stringify(d)); } catch {} };

  return {
    getSalidas: async (f = {}) => {                 // async aunque sea instantáneo
      let l = leer(KEYS.salidas);
      if (f.area) l = l.filter(s => s.area === f.area);
      return l;
    },
    saveSalida: async (s) => { const l = leer(KEYS.salidas); l.unshift(s); escribir(KEYS.salidas, l); return s; },
    getStock:   async (area) => calcularStockTeorico(area),   // HOY: se calcula en el cliente
    // …resto del contrato igual…
  };
};
```

### Implementación de mañana (misma firma, distinto motor)

```js
// data/store/ApiStore.js  — NO se implementa todavía; es el destino.
window.createApiStore = ({ baseUrl, getToken }) => {
  const req = (path, opts = {}) => fetch(baseUrl + path, {
    ...opts,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}`, ...(opts.headers||{}) },
  }).then(r => r.ok ? r.json() : Promise.reject(r));

  return {
    getSalidas: (f = {}) => req(`/salidas?` + new URLSearchParams(f)),
    saveSalida: (s) => req('/salidas', { method: 'POST', body: JSON.stringify(s) }),
    getStock:   (area) => req(`/stock?area=${encodeURIComponent(area)}`),  // MAÑANA: vista SQL
    // …resto del contrato igual…
  };
};
```

### Selección en un solo lugar (feature flag)

```js
// El resto de la app NO sabe cuál está activo.
const repo = (window.APP_CONFIG?.backend === 'api')
  ? createApiStore({ baseUrl: window.APP_CONFIG.apiUrl, getToken: () => sessionStorage.token })
  : createLocalStore({ calcularStockTeorico });
```

### Cómo cambian los módulos (mínimo, gracias al patrón actual)

Hoy: `createModSalidas({ ui, logger, calcularStockTeorico })` y dentro toca `localStorage`.
Mañana: `createModSalidas({ ui, logger, repo })` y dentro hace `await repo.saveSalida(...)`.
**El cambio es localizado** porque ya inyectas dependencias — no hay `localStorage` esparcido por la UI,
queda encapsulado en `LocalStore`.

### Plan de migración por etapas (reversible en cada paso)

> Esta es la vista *a nivel de capa de datos*. El plan institucional completo (8 fases) está en
> [decision-backend.md](decision-backend.md) §8; la equivalencia entre ambas numeraciones se indica allí.

| Etapa | Qué se hace | Riesgo |
|---|---|---|
| **6.0** | Este diagnóstico. | Nulo (solo doc). |
| **6.1** | Crear `LocalStore` + contrato y refactorizar módulos para usar `repo` async, **sin cambiar backend**. Todo sigue en `localStorage`. | Bajo — comportamiento idéntico, validable con la app actual. |
| **6.2** | Elegir backend (ver [decision-backend.md](decision-backend.md) §7), crear esquema SQL + `vista_stock`, sin conectar la app. | Bajo — trabajo aislado. |
| **6.3** | Implementar `ApiStore` + `/auth/login`. Probar contra el backend con un usuario de prueba. | Medio. |
| **6.4** | Seed: importar el respaldo JSON actual a la BD (script único, idempotente vía `id_legado`). | Medio — datos reales. |
| **6.5** | Cutover: activar `APP_CONFIG.backend='api'`. `localStorage` queda como caché/respaldo offline. | Controlado por flag, reversible. |

---

**Relacionado:** [api-futura.md](api-futura.md) (endpoints que consume `ApiStore`) ·
[modelo-datos.md](modelo-datos.md) (tablas destino del mapeo).
