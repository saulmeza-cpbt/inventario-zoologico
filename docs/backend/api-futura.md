# API futura (conceptual) — Fase 6

> Parte del paquete de diseño de la Fase 6. Índice en [README.md](README.md).
> Documento de **diseño**: endpoints conceptuales, **sin implementar**. No se crea servidor.

Contiene: **§5** estrategia de API futura.

---

## 5. Estrategia de API futura (conceptual, sin implementar)

Convenciones: REST sobre JSON, autenticación por **JWT Bearer**, autorización por **rol** y **área**.
Filtros vía query string reutilizando los que ya existen en la UI (`?area=`, `?mes=AAAA-MM`).

### Autenticación / seguridad
| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/auth/login` | Devuelve JWT + perfil (rol, área). |
| POST | `/auth/logout` | Invalida sesión/token. |
| GET | `/auth/me` | Perfil del usuario autenticado. |

### Catálogo y seguridad
| Método | Endpoint | Notas |
|---|---|---|
| GET | `/usuarios` / `POST /usuarios` | Alta/baja (solo rol admin). |
| GET | `/roles` | Catálogo de roles + permisos. |
| GET | `/areas` | Las 5 áreas. |
| GET | `/articulos?area=&q=` | Reemplaza a `CATALOGO_INVENTARIO` + maestro. |
| GET | `/codigos-barras?codigo=` | Resolución alias→interno (lo que hoy hace `resolverCodigo`). |

### Movimientos
| Método | Endpoint | Mapea a la operación actual |
|---|---|---|
| POST | `/entradas` | `guardarDocumento` / `registrarEntradaRapida` (folio lo asigna el server). |
| GET | `/entradas?area=&mes=&tipo=` | Historial de entradas. |
| POST | `/salidas` | `registrarSalida` (validación de stock en server, ver nota). |
| GET | `/salidas?area=&mes=` | Historial de salidas. |
| POST | `/solicitudes` · `PATCH /solicitudes/{id}` | Alta y cambio de `estado`. |
| GET | `/solicitudes?area=&estado=` | Concentrado de solicitudes. |
| POST | `/levantamientos` · `GET /levantamientos?area=` | Conteo físico e historial. |

### Consulta / reportes / auditoría
| Método | Endpoint | Notas |
|---|---|---|
| GET | `/stock?area=` | Lee la **vista** `vista_stock` (cálculo en BD, no en cliente). |
| GET | `/reportes/entradas?area=&mes=` · `/reportes/salidas?…` | Devuelve filas listas para CSV (o `?formato=csv`). |
| GET | `/bitacora?entidad=&nivel=` | Auditoría. |
| POST | `/respaldo/exportar` · `POST /respaldo/importar` | Equivalente al módulo actual (admin); útil para el seed inicial. |

> **Nota — validación de stock al dar salida.** Hoy `registrarSalida` valida contra el stock
> calculado **en el cliente** (bloqueo suave con `confirm`). En backend, esa validación debe correr
> **dentro de la transacción** del `POST /salidas` (el server consulta `vista_stock` y decide). El
> "override por stock insuficiente" se traslada a un flag explícito en el body (p. ej.
> `{ forzar: true }`) que exige rol autorizado y deja el `WARN` en bitácora — preservando la regla actual.

---

**Relacionado:** estos endpoints son justamente los que consume `ApiStore` en la capa de persistencia
descrita en [migracion-localstorage.md](migracion-localstorage.md) §6. Las entidades que devuelven se
definen en [modelo-datos.md](modelo-datos.md).
