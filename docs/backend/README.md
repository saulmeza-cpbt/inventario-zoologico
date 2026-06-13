# Fase 6 — Preparación para Backend y Base de Datos

**Proyecto:** Zoo Tamatán — Inventario V3.0
**Tipo de documento:** Diagnóstico técnico y propuesta de migración (NO implementación)
**Fecha:** 2026-06-12
**Estado del sistema:** En producción (gh-pages), persistencia 100% `localStorage`.

> ⚠️ **Alcance de esta fase.** Este conjunto de documentos es **solo diseño/arquitectura**. No se crea
> servidor, no se cambia la persistencia, no se toca código de producción (HTML, JS, catálogos), no se
> agregan dependencias, no se toca `localStorage` ni gh-pages. Es el plano para que la migración futura
> sea un cambio controlado y reversible, no una reescritura.

---

## Índice

| Documento | Contenido |
|---|---|
| **README.md** (este archivo) | Diagnóstico del sistema actual (§0) y resumen ejecutivo. |
| [modelo-datos.md](modelo-datos.md) | Modelo de datos mínimo (§1), campos a conservar (§3), campos nuevos (§4). |
| [api-futura.md](api-futura.md) | Endpoints conceptuales de la API futura (§5). |
| [migracion-localstorage.md](migracion-localstorage.md) | Mapeo `localStorage` → tablas (§2) y capa de persistencia `DataStore`/`LocalStore`/`ApiStore` (§6). |
| [decision-backend.md](decision-backend.md) | Comparación de backends con 9 criterios (§7), plan de migración por fases (§8), primer paso recomendado (§9). |

> La numeración de secciones (§0–§9) se conserva del análisis original para trazabilidad entre documentos.

---

## 0. Diagnóstico del sistema actual

El sistema guarda **5 colecciones** en `localStorage` y consume **3 catálogos estáticos**
embebidos en JS (no en `localStorage`). El stock **no se almacena**: se calcula en cada render.

| Clave localStorage | Colección | Forma de cada registro |
|---|---|---|
| `zoo_tamatán_entradas_v3` | Entradas (documentos) | `{ id, folio, tipo, articulos[], datos{}, ts }` |
| `zoo_tamatán_salidas_v1` | Salidas | `{ id, area, motivo, responsable, articulos[], fecha, ts }` |
| `zoo_tamatán_solicitudes_v1` | Solicitudes | `{ id, folio, area, fecha, proyecto, presupuestal, solicitante, estado, justificacion, articulos[], ts }` |
| `zoo_tamatán_levantamientos_v1` | Levantamientos | `{ id, semana, area, fecha, responsable, articulos[], resumen{}, ts }` |
| `zoo_tamatán_bitacora_v3` | Bitácora | `{ nivel, msg, entidad, accion, ts, tsISO }` |

| Catálogo (JS estático) | Variable global | Forma |
|---|---|---|
| Inventario base abril | `CATALOGO_INVENTARIO` | `{ [area]: [{ c, n, u, p, e }] }` |
| Maestro ene–abr | `CATALOGO_ARTICULOS_POR_AREA` | `{ [area]: [{ codigo, nombre }] }` |
| Alias de barras | `CATALOGO_CODIGOS_BARRAS` | `{ [barcode]: { area, codigo } }` |

**Hallazgos relevantes para la migración:**

1. **El código interno es el identificador real del producto** (`c` / `codigo`); el código de
   barras es un **alias muchos-a-uno** que resuelve al interno. El modelo de datos debe respetarlo.
2. **No hay usuarios ni roles.** "Responsable" y "solicitante" son texto libre, no entidades.
3. **El folio tiene dos naturalezas distintas:** el folio interno autogenerado (`FAC-26-0001`) y el
   **folio físico del documento** (`datos.folioDocumento`, capturado por el usuario). Ambos deben conservarse.
4. **Los artículos están anidados (embebidos)** dentro de cada documento. En SQL serán tablas hijas.
5. **El stock es derivado, no almacenado.** En backend debe ser una **vista SQL**, no una tabla.
6. **Ya existe el patrón de inyección de dependencias** (`createModX({ ... })`). Es el punto exacto
   donde se inserta la futura capa de datos sin reescribir los módulos.
7. **El respaldo JSON ya define el "contrato de migración":** exporta las 5 claves con `_meta`.
   Ese mismo formato sirve como **vehículo de carga inicial** hacia la base de datos.

---

## Resumen ejecutivo

- El sistema ya tiene el **asiento arquitectónico** (inyección de dependencias) para insertar una
  capa de datos sin reescribirse.
- La pieza crítica es hacer esa capa **asíncrona desde el día 1** (Fase 2 del plan), aún sobre `localStorage`.
  Ver [migracion-localstorage.md](migracion-localstorage.md) §6.
- El modelo de datos respeta lo que hace único a este sistema: **código interno como identificador**,
  **barras como alias**, **folio físico vs. interno**, **stock derivado (vista)**.
  Ver [modelo-datos.md](modelo-datos.md).
- El respaldo JSON existente **ya es el vehículo de migración** de datos.
- Backend recomendado: **Supabase/PostgreSQL** si la institución permite nube; **FastAPI + PostgreSQL**
  si se exige on-premise/control total. Intercambiable gracias al contrato `DataStore`.
  Ver [decision-backend.md](decision-backend.md).
- **Nada de esto se implementa en esta fase.** El siguiente paso accionable es la **Fase 2** del plan
  (introducir `DataStore` + `LocalStore`, todavía sobre `localStorage`).
