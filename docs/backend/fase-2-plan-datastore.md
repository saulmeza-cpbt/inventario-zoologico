# Fase 2 — Plan de la capa DataStore / LocalStore async

**Proyecto:** Zoo Tamatán — Inventario V3.0
**Tipo de documento:** Diagnóstico técnico y plan (NO implementación)
**Fecha:** 2026-06-13
**Depende de:** [README.md](README.md) (Fase 1) · detalle de la capa en [migracion-localstorage.md](migracion-localstorage.md) §6.

> ⚠️ **Alcance de esta fase.** Este documento es **solo diseño/plan**. No crea `DataStore` ni
> `LocalStore`, no migra ningún módulo, no toca HTML/JS/catálogos, no agrega dependencias, no cambia
> persistencia ni comportamiento, no toca gh-pages. Es el plano para que la Fase 2 (la capa de
> persistencia abstraída) se implemente después como una serie de PRs pequeños y reversibles.

**Objetivo de la Fase 2:** introducir una capa de persistencia abstraída para que **hoy** el sistema
siga usando `localStorage` exactamente igual, pero **mañana** pueda cambiarse a API/backend **sin
reescribir todos los módulos**.

---

## Aclaraciones clave (alcance y supuestos)

- **El stock sigue siendo derivado, NO persistido.** Se calcula en cada render
  (`base abril + entradas − salidas`) vía `calcularStockTeorico`. No entra al `DataStore` como dato
  guardable; a lo sumo, en una fase posterior, como lectura derivada (`getStock`) servida por una vista SQL.
- **Salidas y Entradas son los módulos de MAYOR riesgo**, porque sus datos se leen de forma
  **síncrona y cruzada** desde fuera de su módulo (ver §2). Se migran **al final**.
- **Solicitudes es el mejor piloto** porque está **aislado**: nadie más lee sus datos (ver §6).
- **Orden de migración:** Solicitudes → Levantamientos → Bitácora → Salidas → Entradas.
- **Ubicación propuesta para la implementación futura:** `js/data/LocalStore.js`
  (coherente con `js/` donde ya viven los módulos), **salvo que decidamos otra cosa después**.

---

## 1. Diagnóstico: puntos que leen/escriben `localStorage` hoy

Inventario completo (14 sitios en 3 archivos):

| # | Ubicación | Colección | Op | Acoplamiento |
|---|---|---|---|---|
| 1 | `zoo11AM_v3.0_DOCUMENTOS_ENTRADA.html:1058` `cargar()` | entradas | lee | Cachea en `estado.documentos` (única colección con caché en memoria) |
| 2 | `…html:1074` `guardar()` | entradas | escribe | **Debounce 2000ms** (`CONFIG.SAVE_DEBOUNCE`) + `updateStatus` |
| 3 | `…html:1090` `logger.cargarLogs()` | bitácora | lee | — |
| 4 | `…html:1093` `logger.guardarLogs()` | bitácora | escribe | Cap 200 LIFO + `console.*`; **lo invocan TODOS los módulos** |
| 5 | `…html:1897` `calcularStockTeorico()` | salidas | lee | ⚠️ **lectura síncrona cruzada** |
| 6 | `…html:1918-1919` `modSolicitudes` (`cargar`/`guardarLS`) | solicitudes | lee/escribe | **Aislado** (nadie más la lee) |
| 7 | `…html:2037-2038` `modLevantamientos` (`cargar`/`guardarLS`) | levantamientos | lee/escribe | **Aislado** (nadie más la lee) |
| 8 | `…html:2272` wiring `getSalidas` (reportes) | salidas | lee | ⚠️ **lectura síncrona cruzada** |
| 9 | `js/modSalidas.js:17-18` (`cargar`/`guardarLS`) | salidas | lee/escribe | Consumida por #5 y #8 |
| 10 | `js/modRespaldo.js:25,124` | **las 5 claves** | lee/escribe | Export/import masivo |

**Ya desacoplados (NO tocan `localStorage` directamente):**
- `js/modStock.js` — usa `calcularStockTeorico` (inyectado) + `window.CATALOGO_INVENTARIO`.
- `js/modScanner.js` — delega en `registrarSalida` / `registrarEntrada` inyectados.
- `js/modReportes.js` — recibe `getEntradas` / `getSalidas` inyectados (solo lectura).

> **5 claves canónicas** (con acento exacto `á`): `zoo_tamatán_entradas_v3`, `zoo_tamatán_salidas_v1`,
> `zoo_tamatán_solicitudes_v1`, `zoo_tamatán_levantamientos_v1`, `zoo_tamatán_bitacora_v3`.
> El registro canónico de claves vive en `js/modRespaldo.js` (`CLAVES`).

---

## 2. Mapa de acoplamiento (el hallazgo que manda en el plan)

```
                         calcularStockTeorico(area)   ← lee SALIDAS de localStorage (#5, síncrono)
                                   │  (síncrono)
            ┌──────────────────────┼───────────────────────┐
            ▼                       ▼                        ▼
       modStock.render     modSalidas (validación      modLevantamientos
                            de stock disponible)        (existencia teórica)

   wiring reportes.getSalidas  ← lee SALIDAS de localStorage (#8, síncrono) → modReportes
```

- **`salidas`** se lee síncronamente desde **fuera** de `modSalidas`: por `calcularStockTeorico` (#5)
  y por el wiring de reportes (#8). Y `calcularStockTeorico` lo consumen **síncronamente** Stock,
  la validación de Salidas y Levantamientos.
- **`entradas`** vive cacheada en `estado.documentos` y alimenta historial, dashboard y
  `calcularStockTeorico`, además del **debounce de 2000ms** al guardar.

➡️ **Conclusión:** volver `async` `salidas` o `entradas` propaga `await` en cascada a varios
consumidores síncronos. Por eso se migran al final, y **Solicitudes / Levantamientos** (aisladas)
van primero.

---

## 3. Contrato `DataStore` propuesto

Nivel-colección (calca 1:1 el patrón `cargar()` / `guardarLS()` actual → mínimo riesgo).
Todo devuelve `Promise`:

```
getEntradas()            -> Promise<Entrada[]>        saveEntradas(arr)        -> Promise<void>
getSalidas()             -> Promise<Salida[]>         saveSalidas(arr)         -> Promise<void>
getSolicitudes()         -> Promise<Solicitud[]>      saveSolicitudes(arr)     -> Promise<void>
getLevantamientos()      -> Promise<Levantamiento[]>  saveLevantamientos(arr)  -> Promise<void>
getBitacora()            -> Promise<Evento[]>         saveBitacora(arr)        -> Promise<void>
registrarBitacora(ev)    -> Promise<void>   // append 1 evento (unshift + cap 200), NO reemplaza
```

**Notas de diseño:**
- `getX()` lee la colección completa; `saveX(arr)` reemplaza la colección completa
  (idéntico a `guardarLS` de hoy). `registrarBitacora(ev)` añade un evento (read-modify-write atómico).
- **`getStock` NO está en el contrato:** el stock es derivado (ver Aclaraciones). Sigue siendo
  `calcularStockTeorico`.
- **Reconciliación con Fase 1:** el §6 de [migracion-localstorage.md](migracion-localstorage.md)
  esbozó `saveEntrada` (por-registro) y `getStock`. Para **Fase 2** se usa la versión nivel-colección
  (más segura, refleja el código actual). El `saveEntrada` por-registro y el folio asignado por
  servidor quedan para Fase 6/7.

---

## 4. Diseño de `LocalStore` async

`LocalStore` envuelve **exactamente** la lógica de hoy; solo devuelve promesas.

```js
// js/data/LocalStore.js  (NUEVO; factory, mismo patrón que los módulos existentes)
window.createLocalStore = () => {
  const KEYS = {
    entradas:       'zoo_tamatán_entradas_v3',
    salidas:        'zoo_tamatán_salidas_v1',
    solicitudes:    'zoo_tamatán_solicitudes_v1',
    levantamientos: 'zoo_tamatán_levantamientos_v1',
    bitacora:       'zoo_tamatán_bitacora_v3',
  };
  const leer = (k)    => { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch { return []; } };
  const grab = (k, d) => { try { localStorage.setItem(k, JSON.stringify(d)); } catch {} };  // mismo swallow

  return {
    getSolicitudes:  async ()    => leer(KEYS.solicitudes),
    saveSolicitudes: async (arr) => grab(KEYS.solicitudes, arr),
    // …idéntico para entradas / salidas / levantamientos / bitácora…
    registrarBitacora: async (ev) => {                 // replica logger.registrar (cap 200 LIFO)
      const logs = leer(KEYS.bitacora);
      logs.unshift(ev);
      if (logs.length > 200) logs.pop();
      grab(KEYS.bitacora, logs);
    },
  };
};
```

**Lo que se preserva tal cual (cero cambio de comportamiento):**
- Las **5 claves con acento exacto**.
- `|| '[]'` para colección vacía.
- El `try/catch {}` que **traga el error de cuota** de `localStorage` (igual que hoy).
- El orden `unshift` (más reciente primero) y el **cap 200 LIFO** de bitácora.
- Sin timing nuevo: `async` + microtask resuelve ≈ inmediato; el flujo percibido no cambia.

**Punto a decidir (bitácora):** hoy el cap 200 + `console.*` viven en `logger.registrar`
(`…html:1096`). Propuesta: `registrarBitacora` hace el read-modify-write con el cap, y
`logger.registrar` delega en él conservando el `console.*`. Así la regla no se duplica.

---

## 5. Estrategia de migración gradual (patrón "strangler")

Un módulo a la vez, sin tocar los demás. Por cada módulo migrado:

1. Añadir `repo` a las deps del factory: p. ej. `createModSolicitudes({ ui, logger, repo })`.
2. Reemplazar el `cargar()` / `guardarLS()` internos por `await repo.getX()` / `await repo.saveX()`.
3. Volver `async` los métodos públicos que leen/escriben (`render`, `guardar`, `cambiarEstado`) y
   envolver su cuerpo en `try/catch` con `ui.toast` (los `onclick` inline toleran promesas, pero hay
   que capturar errores como ya se hace hoy).
4. **Coexistencia segura:** mientras un módulo usa `repo` y otro sigue con su `cargar/guardarLS`
   propio, **ambos leen/escriben la MISMA clave** → no hay inconsistencia. Eso permite migrar de a
   poco, sin un "big bang".

`modRespaldo` puede seguir usando las claves crudas durante toda la Fase 2 (o enrutarse por el
`DataStore` al final); no bloquea nada.

### Orden de migración (de menor a mayor riesgo)

| Orden | Módulo | Por qué ahí |
|---|---|---|
| 1 | **Solicitudes** | Aislado; piloto que prueba el patrón de extremo a extremo (ver §6). |
| 2 | **Levantamientos** | Aislado; idéntico patrón al piloto. |
| 3 | **Bitácora** | `registrarBitacora` + que `logger` delegue. Toca a todos los llamadores, pero solo como side-effect. |
| 4 | **Salidas** | Aquí se debe volver `async` `calcularStockTeorico` **y sus 4 consumidores** (Stock, validación de Salidas, Levantamientos, wiring de reportes) en el mismo PR. |
| 5 | **Entradas** | Al final: caché `estado.documentos` + debounce 2000ms + dashboard/historial. |

---

## 6. Por qué Solicitudes es el piloto

`modSolicitudes` (`…html:1914-2030`) es la colección **más aislada** del sistema:

- Tiene su **propio KEY** (`zoo_tamatán_solicitudes_v1`) y su **propio `render`**.
- **Ningún otro módulo lee sus datos**: no la usan Stock, ni Reportes, ni `calcularStockTeorico`, ni
  el respaldo en caliente.
- Su superficie pública es pequeña y autocontenida (`guardar`, `cambiarEstado`, `render`, `limpiar`).

Por eso migrarla **demuestra el patrón completo** (factory con `repo`, métodos async, coexistencia
con módulos no migrados) con **radio de impacto casi nulo**. Si algo sale mal, solo afecta a
Solicitudes, no al cálculo de stock ni a entradas/salidas.

---

## 7. Riesgos de volver async lo síncrono + mitigaciones

| Riesgo | Detalle | Mitigación |
|---|---|---|
| **Cascada de async** | `salidas`/`entradas` se leen síncronamente fuera de su módulo (#5, #8). Volverlas async obliga a propagar `await` a `calcularStockTeorico` y sus consumidores. | No migrar salidas/entradas hasta el PR que **también** vuelve async `calcularStockTeorico` (pasos 4-5). |
| **Handlers `onclick` inline** | Un método público async devuelve una promesa no esperada → si lanza, rechazo no capturado. | Cada método async envuelve su cuerpo en `try/catch` + `ui.toast` (igual que hoy). |
| **Carreras de escritura** | "Guardar el array completo" + clics rápidos → *last-write-wins* podría perder un registro. Hoy, al ser síncrono, no hay carrera. | Con microtasks sigue siendo serial; mantener `registrarBitacora` atómico (read-modify-write en una sola fn). Cola de escritura solo si más adelante hay async real (API). |
| **Debounce de entradas** | `guardar()` espera 2000ms antes de persistir. | Dejar el debounce en la capa APP; `saveEntradas` escribe al ser invocada. Se aborda en el paso 5. |
| **Caché `estado.documentos`** | Entradas tiene caché en memoria; ¿`LocalStore` pasa a ser la fuente única? | Decisión postergada al paso 5 (entradas al final). |
| **Orden de render tras `await`** | Entre el `await` y el pintado del DOM podría colarse otra acción del usuario. | Releer los datos **después** del `await` dentro de `render()`. Ventana ≈0 con `localStorage`. |
| **Duplicar la regla de bitácora** | Cap 200 + `console.*` viven hoy en `logger`. | `registrarBitacora` centraliza el cap; `logger` delega y conserva el `console.*` (ver §4). |

---

## 8. Validación esperada (sin backend)

- **Paridad de comportamiento por consola** vía `APP.*`: esta SPA repinta desde su estado interno y
  revierte la manipulación del DOM, así que **se prueba la lógica, no el pixel**.
- **Snapshot de `localStorage` antes/después** de un flujo migrado → el JSON resultante (claves,
  forma, orden) debe ser **idéntico** al de hoy.
- **Check de paridad temporal (solo en dev, se quita antes del merge):** comparar `cargar()` legacy
  vs `await repo.getSolicitudes()` y assert de igualdad.
- **Guion manual del piloto (Solicitudes):** crear una solicitud → recargar la página → persiste;
  filtrar por área/estado; `cambiarEstado`; sin errores en consola.
- **Regresión transversal:** Stock no cambia números, Reportes CSV igual, Respaldo export/import
  igual (misma clave compartida).
- **Sin deploy:** validar solo en `http://localhost:3000/zoo11AM_v3.0_DOCUMENTOS_ENTRADA.html`;
  **no se toca gh-pages**. Ojo con el **pitfall del debounce 2000ms** cuando se llegue a probar entradas.

---

## 9. Primer PR de código sugerido (después de este documento)

**`feat(persistencia): capa DataStore + LocalStore async (piloto Solicitudes)`**

Contenido mínimo y de bajo riesgo:
- **Nuevo** `js/data/LocalStore.js` — factory `createLocalStore()` con el **contrato completo** de las
  5 colecciones (async), aunque solo se use una.
- Contrato `DataStore` documentado (cabecera JSDoc en ese archivo, o `js/data/DataStore.js` solo-comentarios).
- 1 línea de `<script src="js/data/LocalStore.js">` antes del IIFE + `const repo = createLocalStore();`.
- **Migrar SOLO `modSolicitudes`** a `repo` (piloto). Todo lo demás **intacto** y aún con su
  `cargar/guardarLS` (coexisten sobre la misma clave → seguro).
- Sin backend, sin dependencias, sin cambio funcional, sin gh-pages.

> **Opción aún más conservadora (dos pasos):** PR-2a introduce `LocalStore` **cargado pero sin usar**
> (cero wiring, cero cambio de comportamiento) + el check de paridad en dev; PR-2b migra Solicitudes.
> Se recomienda el PR combinado (piloto) porque demuestra valor real con riesgo todavía mínimo.

**Después del piloto**, los siguientes PRs siguen el orden de §5: Levantamientos → Bitácora →
Salidas (con `calcularStockTeorico` async) → Entradas (caché + debounce).

---

## Resumen

- La capa `DataStore` (async, nivel-colección) desacopla los módulos de `localStorage` **sin cambiar
  comportamiento** y deja el sistema listo para que mañana `ApiStore` lo sustituya sin reescribir la UI.
- **Stock = derivado, no persistido.** **Salidas/Entradas = mayor riesgo** (lecturas síncronas
  cruzadas) → al final. **Solicitudes = piloto** (aislado). **Bitácora/Salidas/Entradas = después.**
- Implementación futura propuesta en `js/data/LocalStore.js` (revisable).
- **Nada se implementa en esta fase.** El siguiente paso accionable es el **PR piloto de §9**.
