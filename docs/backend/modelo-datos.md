# Modelo de datos — Fase 6

> Parte del paquete de diseño de la Fase 6. Índice en [README.md](README.md).
> Documento de **diseño**: no implementa esquema ni toca producción.

Contiene: **§1** modelo de datos mínimo, **§3** campos actuales a conservar, **§4** campos nuevos para backend.

---

## 1. Modelo de datos mínimo

Notación: `PK` clave primaria, `FK` clave foránea, `UQ` único, `→` relación.

### Entidades núcleo (catálogo / seguridad)

```
roles                         areas                         usuarios
─────                         ─────                         ────────
id            PK              id            PK              id              PK
nombre        UQ              nombre        UQ              nombre
permisos      JSONB           icono                         email           UQ
                              color                         password_hash
                              activo                        rol_id          FK → roles.id
                                                            area_id         FK → areas.id (NULL = todas)
                                                            activo
```

```
articulos                                   codigos_barras
─────────                                   ──────────────
id                 PK                        id              PK
codigo_interno     UQ   ← identificador real codigo_barras   UQ   ← EAN/UPC físico
nombre                                       articulo_id     FK → articulos.id   (muchos→uno)
unidad                                       activo
precio_referencia
existencia_inicial      ← campo `e` (base abril, para el cálculo de stock)
area_id            FK → areas.id
activo
```

### Movimientos (cabecera + detalle)

```
entradas                                    entrada_articulos
────────                                    ─────────────────
id              PK                           id            PK
folio           UQ   ← interno (FAC-26-0001) entrada_id    FK → entradas.id  (ON DELETE CASCADE)
tipo                 (factura | caja_chica | articulo_id   FK → articulos.id (NULL si no catalogado)
                      acta_entrega |         nombre              ← snapshot del nombre
                      entrada_rapida)        codigo             ← snapshot del código
folio_documento      ← folio FÍSICO          cantidad
area_destino_id FK → areas.id                unitario           ← precio unitario
responsable                                  importe            ← cantidad × unitario (o columna calculada)
motivo
datos_extra     JSONB ← campos por tipo
                       (rfc, proveedor, fecha factura, mes, contrato…)
fecha
```

```
salidas                                     salida_articulos
───────                                     ────────────────
id              PK                           id            PK
folio           UQ   (opcional, ver §3)      salida_id     FK → salidas.id (CASCADE)
area_origen_id  FK → areas.id                articulo_id   FK → articulos.id (NULL si no catalogado)
motivo               (obligatorio)           descripcion
responsable                                  codigo
fecha                                         unidad
                                              cantidad
```

```
solicitudes                                 solicitud_articulos
───────────                                 ───────────────────
id              PK                           id              PK
folio                ← folio físico (SP-…)   solicitud_id    FK → solicitudes.id (CASCADE)
area_id         FK → areas.id                descripcion
fecha                                         cantidad
proyecto                                      unidad
presupuestal
solicitante
estado               (Pendiente | Autorizada | Recibida | Cancelada)
justificacion
```

```
levantamientos                              levantamiento_articulos
──────────────                              ───────────────────────
id              PK                           id                PK
semana                                        levantamiento_id  FK → levantamientos.id (CASCADE)
area_id         FK → areas.id                codigo
fecha                                         descripcion
responsable                                   unidad
resumen         JSONB ← {total,faltantes,    fisica
                         sobrantes}           teorica
                                              diferencia        ← fisica − teorica (o calculada)
                                              obs
```

### Auditoría y stock

```
bitacora                                    vista_stock   (VIEW, no tabla)
────────                                    ───────────
id          PK                               area_id
nivel           (INFO|WARN|ERROR)            articulo_id
mensaje                                      codigo_interno
entidad         ← folio/área afectada        descripcion
accion          ← verbo de negocio           unidad
usuario_id  FK → usuarios.id (NULL = sistema) precio
ts                                            base        = existencia_inicial
                                              entradas    = Σ entrada_articulos
                                              salidas     = Σ salida_articulos
                                              stock       = base + entradas − salidas
```

### Relaciones (resumen)

- `usuarios` **N→1** `roles`, `usuarios` **N→1** `areas`
- `articulos` **N→1** `areas`; `codigos_barras` **N→1** `articulos` (un artículo, varios barras)
- `entradas` **1→N** `entrada_articulos`; `salidas` **1→N** `salida_articulos`
- `solicitudes` **1→N** `solicitud_articulos`; `levantamientos` **1→N** `levantamiento_articulos`
- `entrada_articulos.articulo_id` / `salida_articulos.articulo_id` **N→1** `articulos` (opcional/nullable)
- `vista_stock` se **deriva** de `articulos + entrada_articulos + salida_articulos` (no se escribe)

> **Decisión de diseño — snapshot vs. FK en el detalle.** Los renglones de detalle guardan
> **a la vez** `articulo_id` (vínculo) **y** `nombre`/`codigo`/`unidad` (copia histórica). Así un
> cambio futuro en el catálogo no altera documentos ya emitidos, y los movimientos viejos sin
> artículo catalogado (que hoy existen como texto libre) siguen siendo válidos con `articulo_id = NULL`.

---

## 3. Campos actuales que deben conservarse

| Concepto | Hoy (localStorage) | Mañana (columna) | Cómo se conserva |
|---|---|---|---|
| Identificador | `id` (`ent-…`,`sal-…`,`sp-…`,`lev-…`) | `id` (PK nuevo) + `id_legado` (texto) | PK la genera la BD; el id viejo se guarda en `id_legado`. |
| Folio interno | `folio` (`FAC-26-0001`) | `folio` (UQ) | Se conserva literal. La generación pasa a ser responsabilidad del backend (ver nota). |
| Folio físico | `datos.folioDocumento` | `folio_documento` | Columna dedicada (hoy va dentro de `datos`). |
| Tipo | `tipo` | `tipo` (enum/text) | Mismos 4 valores: `factura`, `caja_chica`, `acta_entrega`, `entrada_rapida`. |
| Área origen/destino | `area` / `datos.areaDestino` | `area_origen_id` / `area_destino_id` (FK) | De texto a FK; el nombre sigue disponible vía join. |
| Responsable | `responsable` | `responsable` (texto) **+** `usuario_creador_id` (FK) | El texto se conserva; además se ata al usuario que captura. |
| Motivo | `motivo` / `datos.motivo` | `motivo` | Columna dedicada (obligatoria en salidas). |
| Artículos | `articulos[]` (embebido) | tabla `*_articulos` (1→N) | Se normaliza a tabla hija con FK a la cabecera. |
| Código interno admin. | `codigo` / `c` | `codigo` (snapshot) + `articulo_id` (FK) | Doble registro: histórico + vínculo. |
| Código de barras | clave de `CATALOGO_CODIGOS_BARRAS` | `codigos_barras.codigo_barras` | Tabla propia, alias muchos-a-uno al artículo. |
| Cantidad | `cantidad` | `cantidad` (numeric) | Igual. |
| Unidad | `unidad` / `u` | `unidad` | Igual. |
| Precio unitario | `unitario` / `precio` / `p` | `unitario` (detalle) / `precio_referencia` (catálogo) | Se separa "precio del movimiento" de "precio de referencia del catálogo". |
| Importe | (calculado en reportes) | `importe` (columna calculada) | Se persiste como columna generada `cantidad × unitario`. |
| Marca de tiempo | `ts` (epoch) / `tsISO` | `fecha` / `ts` (`timestamptz`) | `timestamptz` reemplaza a epoch + string locale. |
| Estado | `estado` (solicitudes) | `estado` | Mismos valores; ver §4 para `estado_registro` (distinto concepto). |
| Eventos de bitácora | colección `bitacora` | tabla `bitacora` + `usuario_id` | Se conserva nivel/mensaje/entidad/acción; se añade autor. |

> **Nota sobre la generación de folio.** Hoy el contador es
> `documentos.filter(tipo===t).length + 1`, que solo funciona porque hay un único cliente.
> Con backend multiusuario esto produce **colisiones**. El folio debe generarse **en el servidor**
> (secuencia por `tipo`+año, o `SEQUENCE` de Postgres) dentro de la misma transacción que inserta la entrada.

---

## 4. Campos nuevos necesarios para backend

Se aplican de forma **uniforme** a todas las tablas de movimiento (entradas, salidas, solicitudes,
levantamientos) y, donde aplique, a catálogo:

| Campo | Tipo | Propósito |
|---|---|---|
| `usuario_creador_id` | FK → usuarios | Quién creó el registro (autoría real, hoy ausente). |
| `usuario_actualizador_id` | FK → usuarios | Quién hizo la última modificación. |
| `usuario_autorizador_id` | FK → usuarios (NULL) | Solo donde hay flujo de autorización (p. ej. solicitudes `Autorizada`). |
| `fecha_creacion` | `timestamptz` (default now) | Auditoría temporal de alta. |
| `fecha_actualizacion` | `timestamptz` | Auditoría temporal de cambio (trigger `updated_at`). |
| `eliminado_logico` | `boolean` (default false) | Borrado lógico — nunca DELETE físico de movimientos. |
| `estado_registro` | enum (`activo`,`anulado`,`borrador`) | Ciclo de vida del **registro** (distinto del `estado` de negocio de solicitudes). |
| `version_registro` | `int` (default 1) | Bloqueo optimista — evita que dos usuarios pisen el mismo registro. |
| `origen_dispositivo` | text | Trazabilidad: `web`, `scanner`, `import`, `seed`. |
| `id_legado` | text (NULL) | Conserva el `id` original de localStorage para idempotencia del seed y trazabilidad. |

> **Distinción importante:** `estado` (negocio: Pendiente/Autorizada/…) **≠** `estado_registro`
> (técnico: activo/anulado/borrador) **≠** `eliminado_logico` (visibilidad). Son tres ejes
> independientes y conviene no fusionarlos.

---

**Relacionado:** [api-futura.md](api-futura.md) (cómo se exponen estas entidades) ·
[migracion-localstorage.md](migracion-localstorage.md) (cómo se cargan los datos actuales).
