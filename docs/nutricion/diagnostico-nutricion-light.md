# Diagnóstico NUT-A — Nutrición Light

**Fecha:** 25 de junio de 2026
**Ámbito:** Diagnóstico y alcance del módulo de inventario operativo de alimentos.
**Naturaleza:** Solo documentación. No hay código de Nutrición en el repositorio todavía.
**Relacionado:** `docs/estado/estatus-ejecutivo-tecnico.md` (Sección 5) · `docs/roadmap/roadmap-codigos-y-nutricion.md`

---

## 1. Propósito

Nutrición Light es un **inventario operativo de alimentos** para el zoológico: registrar lo que
entra (compras/recepción a proveedor), lo que sale cada día (consumo operativo) y cuánto queda en
existencia. Su valor es de control de almacén y trazabilidad básica del alimento, **no** de
nutrición científica.

Declaración explícita de límite: NUT-A **no** es un sistema de dietas. No calcula requerimientos por
especie, no formula raciones, no balancea nutrientes ni reemplaza criterio veterinario.

---

## 2. Alcance de NUT-A

Incluye (objetivo del módulo, a implementar en fases NUT-B…NUT-F, no en NUT-A):

- **Entradas de proveedor:** recepción de alimento (qué, cuánto, de quién, cuándo).
- **Salidas diarias:** consumo operativo del día.
- **Stock de nutrición:** existencias actuales de cada alimento.
- **Unidades operativas:** kg / pieza / manojo.
- **Scanner:** captura por código, reutilizando el patrón de Movimiento rápido.
- **Ticket de báscula:** peso registrado en recepción/salida (en NUT-A, captura simple del peso).
- **Destino / uso operativo:** a qué se destina una salida (de forma simple y operativa).

Fuera de alcance de NUT-A (fase científica futura, si llega):

- Tablas de requerimiento nutricional por especie.
- Formulación / balance de dietas.
- Cálculos veterinarios o de nutrientes.
- Planificación de raciones por animal.

---

## 3. Principio rector: aislamiento de Salidas generales

**No mezclar Nutrición con Salidas generales.** El inventario de alimentos es un dominio paralelo:

- Claves de almacenamiento **propias** (p. ej. familia `zoo_tamatán_nutricion_*`), separadas de
  `zoo_tamatán_salidas_v1` y de las demás claves existentes.
- Stock **propio** de alimentos, independiente del stock de Snack/Tienda.
- Reportes **propios** de Nutrición.

Motivo: reutilizar las claves/flujo de Salidas para alimentos contaminaría el inventario general,
los conteos y los reportes existentes, y mezclaría unidades (pieza vs kg/manojo). El aislamiento
mantiene ambos dominios limpios y auditables por separado.

---

## 4. Modelo de datos operativo (propuesto, no implementado)

Esquema conceptual sujeto a refinamiento en NUT-B:

- **Alimento (catálogo):** identificador interno, nombre, unidad base operativa (kg / pieza / manojo),
  proveedor habitual (opcional), código(s) de barras asociado(s) (opcional).
- **Entrada de nutrición:** fecha, proveedor, líneas { alimento, cantidad, unidad, peso de ticket de
  báscula (opcional), responsable }.
- **Salida de nutrición:** fecha, líneas { alimento, cantidad, unidad, destino/uso operativo,
  responsable }.
- **Stock de nutrición:** derivado de entradas − salidas, en unidad base por alimento.

Notas:

- Las unidades kg / pieza / manojo conviven; cada alimento declara su unidad base y los movimientos se
  registran en esa unidad para evitar mezclas.
- Si más adelante se aplica factor/caja (línea Códigos PR C-2/C-3), el patrón sería el mismo: stock en
  unidad base, factor aplicado en tiempo de registro. NUT-A no depende de ese trabajo.

---

## 5. Reutilización de patrones existentes

NUT-A se beneficia de lo ya construido, sin tocarlo:

- **Patrón factory con inyección de dependencias** (igual que `modStock` / `modSalidas` / `modScanner`):
  un `createModNutricion({ ui, repo, logger, ... })` mantendría la separación de responsabilidades.
- **Contrato LocalStore async** (`js/data/LocalStore.js`): se ampliaría con métodos propios de
  nutrición (`getAlimentos`/`saveAlimentos`, etc.) siguiendo la misma firma async, sin romper a los
  consumidores actuales.
- **Scanner:** el flujo de Movimiento rápido (resolver código → confirmar artículo → cantidad →
  registrar) es directamente análogo para alimentos.
- **Respaldo:** las nuevas claves se sumarían al export/import de `modRespaldo` cuando existan.

Esto reduce la curva de aprendizaje del personal (misma UX) y el riesgo de implementación (mismos
patrones probados).

---

## 6. Decisión pendiente: store de aliases para Nutrición

Nutrición Light **reutilizará el patrón de scanner / aliases** ya probado en Movimiento rápido
(resolver un código físico al artículo interno correspondiente), pero **queda pendiente decidir**
dónde viven los aliases de los códigos de barras de alimentos:

- **Opción A — store general compartido:** reutilizar el store de aliases existente
  `zoo_tamatán_codigos_barras_v1`.
- **Opción B — store separado:** crear un store propio para los códigos de alimentos.

Restricciones que esta decisión **no** altera:

- **No** debe mezclarse Nutrición con Salidas generales (claves, stock y reportes propios; ver Sección 3).
- El patrón de scanner/aliases se reutiliza tal cual; lo único abierto es la **ubicación del store** de aliases.

**NUT-A no fija esta decisión:** solo documenta que el módulo debe reutilizar el patrón de
scanner/aliases sin mezclar Nutrición con Salidas generales. **La decisión se tomará en NUT-B**, no en NUT-A.

---

## 7. Riesgos específicos de Nutrición

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | Unidades mezcladas (kg/pieza/manojo) | Unidad base por alimento; validación en captura. |
| 2 | Báscula / ticket manual propenso a error | NUT-A: peso manual simple; integración avanzada aislada en NUT-F. |
| 3 | Contaminar Salidas generales | Claves, stock y reportes propios desde el inicio (Sección 3). |
| 4 | Capacitación del personal | Reutilizar UX de Movimiento rápido; guía corta por función. |
| 5 | Trazabilidad del alimento | Registrar destino/uso operativo y, si aplica, código escaneado (alineado con PR C-1). |
| 6 | Expectativa de "sistema de dietas" | Comunicar el límite de alcance: NUT-A es inventario operativo, no nutrición científica. |

---

## 8. Recomendación

- NUT-A se considera **cubierto a nivel diagnóstico** por este documento; no requiere código.
- La implementación empieza en **NUT-B (catálogo de alimentos)** y avanza por el roadmap.
- Decidir prioridad relativa frente a la línea Códigos (PR C-1) antes de abrir código de Nutrición.
- **No implementar Nutrición en código todavía** hasta autorización explícita.
