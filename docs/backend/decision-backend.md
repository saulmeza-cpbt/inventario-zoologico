# Decisión de backend y plan de migración — Fase 6

> Parte del paquete de diseño de la Fase 6. Índice en [README.md](README.md).
> Documento de **diseño**: comparación y plan. No implementa backend ni instala dependencias.

Contiene: **§7** comparación de opciones con 9 criterios + recomendación, **§8** plan de migración por
fases, **§9** primer paso recomendado.

---

## 7. Selección preliminar de backend

Evaluación contra los 9 criterios pedidos (✅ fuerte · 🟡 medio · ❌ débil):

| Criterio | Supabase / PostgreSQL | FastAPI + PostgreSQL | Node + Express | PHP / MySQL | SQLite (local) |
|---|---|---|---|---|---|
| Facilidad de despliegue | ✅ front sigue estático; backend gestionado | 🟡 hay que hostear API + BD | 🟡 hay que hostear API + BD | ✅ hosting compartido / cPanel | 🟡 archivo único, pero requiere envoltura server para web |
| Costo | ✅ free tier cubre esta escala | 🟡 server + BD | 🟡 server + BD | ✅ muy barato | ✅ gratis |
| Mantenimiento | ✅ backups/parches/escalado los hace Supabase | 🟡 tú mantienes API y server | 🟡 tú mantienes; npm cambiante | 🟡 manual; cuidar seguridad | ✅ mínimo (un solo usuario) |
| Compatibilidad institucional | 🟡 dato en nube de tercero (revisar región/política) | ✅ on-premise / control total | ✅ on-premise posible | ✅ muy común en gobierno MX | 🟡 solo una PC, no multi-área en red |
| Curva de aprendizaje | 🟡 SQL + RLS + Supabase | 🟡 Python async / Pydantic | ✅ mismo lenguaje que el front | 🟡 stack más antiguo | ✅ simple |
| Multiusuario | ✅ Postgres + RLS por área | ✅ | ✅ | ✅ MySQL | ❌ concurrencia limitada (salvo Turso/libSQL) |
| Autenticación | ✅ Auth integrado (JWT, usuarios, roles) | 🟡 la implementas tú | 🟡 la implementas tú | 🟡 manual | ❌ no incluye |
| Reportes | ✅ SQL + vistas + PostgREST (incl. `?formato=csv`) | ✅ SQL + endpoints a medida | ✅ SQL + endpoints | ✅ SQL | ✅ SQL (solo local) |
| Auditoría | ✅ tabla + triggers + `usuario_id` del JWT | ✅ control total (middleware) | ✅ control total | 🟡 manual / triggers MySQL | 🟡 manual |
| **Veredicto** | **Recomendado** | Alternativa on-prem | Viable (más código) | Si hay hosting PHP institucional | Solo 1 PC offline |

**Único punto donde Supabase NO domina:** *compatibilidad institucional* (el dato vive en la nube de
un tercero). Si la institución exige el dato **on-premise / en territorio nacional**, ese criterio
pesa más que todos los demás y la recomendación cambia a **FastAPI + PostgreSQL** (mismo esquema, misma
`vista_stock`). Conviene **confirmar esta política antes de la Fase 4** del plan (§8).

### Recomendación

**Supabase (PostgreSQL gestionado)** como destino principal **si la institución permite nube**, por
encaje directo:

1. **No rompe el modelo de despliegue actual.** El frontend sigue siendo estático en gh-pages y
   habla con Supabase vía `supabase-js`; no hay que levantar ni mantener un servidor propio.
2. **Resuelve justo lo que hoy falta:** Auth (usuarios), roles y **RLS** (restringir por rol/área)
   mapean 1:1 con las entidades `usuarios`/`roles`/`areas` del modelo de datos.
3. **Es el menor esfuerzo de migración:** PostgREST expone tablas/vistas como API sin escribir CRUD;
   `vista_stock` es literalmente una `VIEW` SQL; el seed parte del respaldo JSON que ya tienes.
4. **Costo:** el free tier cubre con holgura el volumen de un inventario de zoológico.

**Alternativa formal (on-premise / control institucional completo):** si la institución exige
**on-premise / control total del dato**, ir con **FastAPI + PostgreSQL** (mismo esquema, misma
`vista_stock`); el contrato `DataStore` ([migracion-localstorage.md](migracion-localstorage.md) §6)
hace que la decisión sea intercambiable sin tocar la UI. **PHP/MySQL** solo si quedan atados a hosting
institucional existente. **SQLite** queda reservado para un escenario de una sola PC sin red.

---

## 8. Orden recomendado de migración

Ocho fases, cada una **enviable y reversible por separado**. Ninguna fase rompe la anterior:
mientras no se llega a la Fase 6, la app sigue funcionando exactamente como hoy.

| # | Fase | Objetivo / entregable | Estado tras la fase | Riesgo |
|---|---|---|---|---|
| **1** | Documentación / modelo de datos | Este diagnóstico formalizado en `docs/backend/` (ver §9). Sin código. | Igual que hoy | Nulo |
| **2** | Capa de persistencia local abstraída | `DataStore` (contrato async) + `LocalStore`; módulos pasan a usar `repo`. **Sigue todo en `localStorage`.** | Igual que hoy, pero desacoplado | Bajo — comportamiento idéntico, validable con la app actual |
| **3** | Roles locales | Compuerta de UI por rol (`admin` / `capturista` / `consulta`) guardada localmente. Aún **sin auth real**: prepara la UI para permisos. | Permisos visibles, no seguros | Bajo |
| **4** | Backend mínimo | Esquema SQL + `vista_stock` + `ApiStore` contra endpoints básicos, en entorno de **prueba** (no producción). | App sigue en local; backend en paralelo | Medio |
| **5** | Migración desde JSON / localStorage | Seed idempotente (vía `id_legado`) que carga el **respaldo JSON actual** a la BD. Verificación de conteos. | Datos reales en la BD de prueba | Medio — datos reales |
| **6** | Autenticación | `/auth/login` + JWT + usuarios reales. Los "roles locales" de la Fase 3 pasan a roles del servidor. **Cutover por feature-flag.** | App contra backend con login | Medio |
| **7** | Multiusuario | Folio generado en servidor (secuencias), bloqueo optimista (`version_registro`), validación de stock **transaccional**, RLS por área. | Varios usuarios concurrentes seguros | Medio-alto (concurrencia) |
| **8** | Auditoría formal | Bitácora server-side con `usuario_id` del JWT, registros inmutables, triggers `updated_at`, `eliminado_logico`. | Trazabilidad institucional completa | Bajo-medio |

> **Punto de no retorno controlado:** el *cutover* real ocurre en la Fase 6 y se activa con un
> feature-flag (`APP_CONFIG.backend='api'`). Hasta entonces, todo es aditivo y reversible. La política
> de "dato en la nube vs. on-premise" (§7) debe **resolverse antes de la Fase 4**, porque define el backend.

> **Nota sobre el orden "roles locales antes que backend" (Fase 3 antes que 4–6).** Es intencional:
> hoy no existe **ningún** control de acceso. Una compuerta local de roles aporta valor inmediato
> (evita que cualquiera borre/edite) y deja la UI lista para que la auth real de la Fase 6 solo
> tenga que *sustituir la fuente del rol*, no rediseñar la interfaz.

> **Equivalencia con las etapas 6.x** de [migracion-localstorage.md](migracion-localstorage.md) §6:
> Fase 1 = 6.0 · Fase 2 = 6.1 · Fase 4 = 6.2 · Fase 5 = 6.4 · Fase 6 = 6.3 + 6.5.
> Las Fases 3, 7 y 8 detallan lo que esa vista resumía.

---

## 9. Primer paso recomendado

**El primer PR es de solo documentación** — cero código, sin impacto en producción y trivial de
revertir. Es la Fase 1 del §8, y es justamente **este paquete de documentos**.

**Título / commit (respeta la convención `tipo(scope):` del historial):**

```
docs(backend): modelo de datos inicial y estrategia de migración
```

**Estructura de archivos** (este paquete):

| Archivo | Contenido |
|---|---|
| `docs/backend/README.md` | Diagnóstico del sistema actual (§0), resumen ejecutivo, índice y enlaces. |
| `docs/backend/modelo-datos.md` | §1 (entidades/relaciones), §3 (campos a conservar), §4 (campos nuevos). |
| `docs/backend/api-futura.md` | §5 (endpoints conceptuales + notas de auth y validación de stock). |
| `docs/backend/migracion-localstorage.md` | §2 (mapeo de claves → tablas) + §6 (capa `DataStore`/`LocalStore`/`ApiStore`) + seed. |
| `docs/backend/decision-backend.md` | §7 (comparativa de 9 criterios + recomendación), §8 (plan por fases), §9 (este primer paso). |

**Alcance del PR — qué incluye y qué NO:**

- ✅ Incluye: los 5 archivos `.md` anteriores.
- ❌ NO incluye: ningún `.js`, ningún cambio a `localStorage`, ningún servidor, ningún esquema SQL
  ejecutable, ninguna dependencia nueva, ningún cambio a HTML/JS/catálogos/gh-pages.
  **No toca un solo archivo de producción.**

**Criterios de aceptación (revisión humana):**

1. El modelo de datos refleja las estructuras reales (código interno como ID, barras como alias,
   folio físico vs. interno, stock como vista).
2. El mapeo cubre las **5 claves** de `localStorage` y los **3 catálogos**.
3. La decisión de backend queda con su recomendación **y** la pregunta abierta de nube vs. on-premise.
4. El plan por fases es reversible y no compromete código aún.

**Siguiente PR (NO en este):** Fase 2 — introducir `DataStore` + `LocalStore` (ya con código, pero
todavía sobre `localStorage`). Ver [migracion-localstorage.md](migracion-localstorage.md) §6.
