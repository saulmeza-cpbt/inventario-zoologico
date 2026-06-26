# Roadmap — Códigos & Nutrición

**Fecha:** 25 de junio de 2026
**Ámbito:** Secuencia propuesta para la línea Códigos (trazabilidad / factor) y la línea Nutrición.
**Naturaleza:** Solo documentación / planificación. Ningún ítem está implementado.
**Relacionado:** `docs/estado/estatus-ejecutivo-tecnico.md` · `docs/nutricion/diagnostico-nutricion-light.md`

---

## 1. Punto de partida (verificado)

- `origin/main` = `64cea7a`; `origin/gh-pages` = `277e717`; sin PRs abiertos; repo limpio.
- Códigos-A (PR #26) y Códigos-B (PR #27) en producción.
- `catalogo_codigos_barras.js` vacío; aliases en `zoo_tamatán_codigos_barras_v1`.
- No existe `codigoBarrasLeido`, ni factor/caja, ni módulo Nutrición.
- `calcularStockTeorico` no tocado; Salidas-B (async) es fase futura separada.

---

## 2. Línea Códigos (trazabilidad → factor)

### PR C-1 — `codigoBarrasLeido`
- **Qué:** propagar el código físico escaneado al registro del movimiento.
- **De dónde sale el dato:** `artActual.barcode` ya existe al resolver por alias
  (`js/modScanner.js:89`); hoy se descarta al armar el `articulo` (`modScanner.js:258-264`).
- **Por qué bajo riesgo:** aditivo; Salidas persiste `articulos: [...articulos]`
  (`js/modSalidas.js:180`), copia superficial que conserva campos extra.
- **Restricciones:** NO tocar `calcularStockTeorico`; NO cambiar cantidades; verificar también la
  ruta de **entrada rápida** antes de cerrar.
- **Resultado:** cada movimiento sabe qué código físico lo originó (auditoría/trazabilidad).

### PR C-2 — factor store
- **Qué:** crear el store `zoo_tamatán_factor_cajas_v1` (factor **barcode-scoped**) + UI de captura.
- **Diseño:** aliases siguen simples `{ area, codigo }`; el factor vive aparte. Stock en unidad base.
- **Restricciones:** solo persistencia + captura; **aún no** se aplica a los movimientos.

### PR C-3 — factor aplicado a movimientos
- **Qué:** al registrar, multiplicar la cantidad escaneada por el factor de la presentación para
  obtener unidades base.
- **Diseño:** stock se mantiene en unidad base; el factor se aplica en tiempo de registro.
- **Depende de:** C-2 (store del factor) y, recomendable, C-1 (trazabilidad ya presente).

---

## 3. Línea Nutrición

### NUT-A — documentación / diagnóstico
- **Qué:** alcance y diagnóstico (ver `docs/nutricion/diagnostico-nutricion-light.md`). Sin código.
- **Estado:** cubierto por la documentación de esta sesión.

### NUT-B — catálogo de alimentos
- **Qué:** catálogo de alimentos con unidad base operativa (kg / pieza / manojo) y claves propias.

### NUT-C — entradas de nutrición
- **Qué:** recepción de alimento a proveedor; líneas con cantidad, unidad y (opcional) ticket de báscula.

### NUT-D — salidas de nutrición
- **Qué:** consumo diario; líneas con cantidad, unidad y destino/uso operativo.

### NUT-E — stock / reportes de nutrición
- **Qué:** existencias por alimento (entradas − salidas en unidad base) y reportes propios.

### NUT-F — ticket de báscula avanzado
- **Qué:** captura/integración avanzada del peso de báscula (aislada del flujo simple de NUT-C/D).

---

## 4. Fase futura separada (fuera del roadmap inmediato)

- **Salidas-B:** migrar `calcularStockTeorico` a async + sus 4 consumidores.
- **Entradas:** caché + debounce.

No bloquean PR C ni NUT-A; se planifican aparte.

---

## 5. Dependencias y orden sugerido

```
Códigos:   C-1  →  C-2  →  C-3
Nutrición: NUT-A → NUT-B → NUT-C → NUT-D → NUT-E → NUT-F
```

- C-1 es independiente y de menor riesgo: buen primer paso.
- C-2 antes de C-3 (el store debe existir antes de aplicarlo).
- NUT-B…NUT-F son secuenciales; NUT-A (docs) es prerequisito de criterio, no de código.
- Las dos líneas pueden intercalarse según prioridad operativa; no comparten claves ni stock.

---

## 6. Reglas transversales (vigentes para toda la fase)

- Disciplina docs-first: documentar → aprobar → implementar sin commit → validar → PR → merge + deploy.
- No tocar `calcularStockTeorico` salvo en su fase dedicada (Salidas-B).
- No mezclar Nutrición con Salidas generales (claves/stock/reportes propios).
- Aliases simples `{ area, codigo }`; factor en store separado; stock en unidad base.

---

## 7. Recomendación de arranque

**Siguiente paso inmediato:** PR C-1 (`codigoBarrasLeido`) **o** NUT-A según prioridad. Si el objetivo
es cerrar trazabilidad antes de abrir un módulo nuevo, arrancar por **PR C-1** (menor riesgo, retorno
inmediato). No implementar factor ni Nutrición en código todavía.
