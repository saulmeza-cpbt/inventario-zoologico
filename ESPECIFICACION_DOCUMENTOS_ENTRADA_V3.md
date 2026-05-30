# 📄 ESPECIFICACIÓN TÉCNICA: Documentos de Entrada V3
## Sistema de Agrupación por Tipo de Documento

**Fecha:** 30/04/2026  
**Versión:** 3.0 (Arquitectura mejorada)  
**Estado:** Especificación completa

---

## 🎯 OBJETIVO

Reemplazar el sistema actual de "Entradas simples por factura" con un sistema de **Documentos de Entrada** que permita múltiples tipos de documento, cada uno con sus propias reglas, validaciones y ciclo de vida.

---

## 📋 TIPOS DE DOCUMENTO DE ENTRADA

### **1. FACTURA (Proveedor)**
```
Características:
- Documento: Una factura de proveedor
- Monto: Generalmente >= $1,000
- Validación: RFC proveedor, número de factura único
- Artículos: Múltiples artículos en la misma factura
- Ciclo: Pago completo → Se cierra

Datos:
├─ Folio factura (FAC-2026-001)
├─ RFC proveedor
├─ Nombre proveedor
├─ Fecha de factura
├─ Monto total
├─ Artículos[] (cantidad, precio unitario)
├─ IVA incluido/excluido
├─ Fecha de pago
└─ Responsable (quien recibió)

Validaciones:
✓ Número de factura único
✓ RFC válido
✓ Suma de artículos = monto total
✓ Nombre proveedor consistente (detectar repetidos)
```

### **2. ACTA DE ENTREGA (Material calendarizado)**
```
Características:
- Documento: Un acta de entrega por envío calendarizado
- Monto: Variable (puede ser múltiples entregas parciales)
- Validación: Artículos y cantidades según calendario
- Artículos: Generalmente 1-3 tipos (ej: limpieza, cloro)
- Ciclo: Entregas mensuales durante el año

Datos:
├─ Folio acta (ACT-2026-04)
├─ Mes/período
├─ Proveedor (contratista)
├─ Artículos con cantidades esperadas vs. recibidas
├─ Fecha de entrega
├─ Observaciones de calidad
├─ Responsable (quien recibió)
└─ Estado: Completa / Parcial / Con novedades

Validaciones:
✓ Acta no duplicada
✓ Cantidades dentro del rango esperado
✓ Articulos coinciden con contrato original
```

### **3. FACTURA CAJA CHICA**
```
Características:
- Documento: Múltiples compras menores (<$1,000 c/u)
- Monto: <= $1,000 por artículo
- Validación: Total caja chica <= límite mensual
- Artículos: Varios, generalmente 1 artículo c/u
- Ciclo: Reporte mensual de gastos menores

Datos:
├─ Folio caja chica (CAJA-2026-04)
├─ Mes
├─ Artículos con monto individual
├─ Proveedores variados (pequeños)
├─ Fecha de reporte
├─ Total gastado
├─ Responsable (quien gestionó)
└─ Observaciones

Validaciones:
✓ Cada artículo <= $1,000
✓ Total caja chica <= límite (ej: $5,000/mes)
✓ Documentos justificantes (tickets, facturas)
```

### **4. SOLICITUD DE PEDIDO**
```
Características:
- Documento: Una orden de compra enviada a proveedor
- Monto: Estimado (se actualiza con factura posterior)
- Validación: Stock mínimo estimado, presupuesto aprobado
- Artículos: Múltiples artículos solicitados
- Ciclo: Genera una factura posterior cuando llega

Datos:
├─ Folio solicitud (SOL-2026-0147)
├─ Proveedor (pre-seleccionado)
├─ Artículos solicitados con cantidad y precio estimado
├─ Fecha de solicitud
├─ Fecha estimada de llegada
├─ Monto estimado
├─ Estado: Solicitada / Parcial recibida / Recibida
├─ Responsable (quien solicitó)
└─ Observaciones

Validaciones:
✓ Proveedor tiene contrato vigente
✓ Monto está en presupuesto
✓ Artículos existen en catálogo
```

### **5. ACTA DE FALLO (Entregas parciales de contrato)**
```
Características:
- Documento: Entregas mensuales de un contrato anual
- Monto: Fracción del contrato total
- Validación: Debe sumarse al total del contrato original
- Artículos: Generalmente 1-5 tipos (ej: uniformes, herramientas)
- Ciclo: 12 entregas mensuales parciales durante el año

Datos:
├─ Folio acta fallo (FALLO-2026-04)
├─ Referencia contrato (CONT-2025-0089)
├─ Mes/número de entrega (4/12)
├─ Artículos con cantidades totales en contrato vs. entregadas
├─ Monto de esta entrega
├─ Monto acumulado hasta ahora
├─ Monto pendiente
├─ Fecha de entrega
├─ Responsable (quien recibió)
└─ Estado: Conforme / Con observaciones

Validaciones:
✓ Total acumulado <= total contrato
✓ Artículos coinciden con contrato
✓ Cantidades dentro de rangos esperados
✓ No más de una entrega por mes (generalmente)
```

---

## 🏗️ NUEVA ARQUITECTURA DE ENTRADAS

### **Flujo de Usuario**

```
┌─────────────────────────────────┐
│ 1. SELECCIONAR TIPO DOCUMENTO   │
│  ├─ Factura                     │
│  ├─ Acta de Entrega            │
│  ├─ Caja Chica                 │
│  ├─ Solicitud de Pedido        │
│  └─ Acta de Fallo              │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ 2. CREAR O SELECCIONAR DOCUMENTO│
│  ├─ [Nuevo documento]           │
│  ├─ Documento existente A       │
│  ├─ Documento existente B       │
│  └─ Documento existente C       │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ 3. AGREGAR ARTÍCULOS (múltiples)│
│  ├─ Artículo 1: cant. precio    │
│  ├─ Artículo 2: cant. precio    │
│  └─ Artículo 3: cant. precio    │
│                                 │
│ [+ Agregar otro artículo]       │
└────────────┬────────────────────┘
             ↓
┌─────────────────────────────────┐
│ 4. VALIDAR Y GUARDAR DOCUMENTO  │
│  ├─ Cálculos automáticos        │
│  ├─ Validaciones específicas     │
│  └─ Crear folio único           │
└─────────────────────────────────┘
```

### **Estructura de Datos**

```javascript
// Documento de Entrada (nuevo contenedor)
{
  id: "ent-0047",
  folio: "FAC-2026-0047",                    // Folio automático
  tipo: "factura" | "acta_entrega" | "caja_chica" | "solicitud" | "fallo",
  
  // Metadatos según tipo
  factura: {
    numeroFactura: "FACT-2026-001",
    rfc: "XXX010101ABC",
    proveedor: "Distribuidora X",
    fechaFactura: "2026-04-25",
    montoTotal: 5000.00
  },
  
  acta_entrega: {
    numeroActa: "ACT-2026-04",
    mes: "Abril 2026",
    proveedor: "Contratista Y",
    estado: "Completa" | "Parcial"
  },
  
  caja_chica: {
    mes: "Abril 2026",
    totalGastado: 3500.00
  },
  
  solicitud: {
    numeroSolicitud: "SOL-2026-0147",
    proveedor: "Proveedor Z",
    estadoSolicitud: "Recibida"
  },
  
  fallo: {
    numeroFallo: "FALLO-2026-04",
    numeroContrato: "CONT-2025-0089",
    numeroEntrega: "4/12",
    montoContrato: 36000.00
  },
  
  // Datos comunes
  fecha: "2026-04-30",
  responsable: "Juan Pérez",
  area: "MANTENIMIENTO",
  
  // Artículos agrupados
  articulos: [
    {
      codigo: "M-2160007",
      nombre: "Bio papel sanitario",
      cantidad: 10,
      unidad: "PIEZA",
      costoUnitario: 55.58,
      ivaRate: 0.16,
      totalSiva: 555.80,
      totalCiva: 644.72,
      observaciones: ""
    },
    // ... más artículos
  ],
  
  // Totales agregados
  totales: {
    cantidadArticulos: 3,
    montoSiva: 2000.00,
    montoIva: 320.00,
    montoCiva: 2320.00
  },
  
  // Control de estado
  estado: "Completo" | "Pendiente" | "Parcial",
  observaciones: "Entrega con demora de 2 días",
  
  // Auditoría
  ts: 1714521600000,
  creadoPor: "usuario1",
  modificadoEn: "2026-04-30 14:30"
}
```

---

## ✅ VALIDACIONES POR TIPO

### **FACTURA**
```javascript
Validaciones:
✓ Número factura debe ser único
✓ RFC debe ser válido (18 caracteres)
✓ Proveedor no vacío
✓ Monto total >= $1,000
✓ Suma de artículos ≈ monto total (tolerancia ±$1)
✓ IVA consistente (0% o 16%)
✓ Responsable no vacío
```

### **ACTA DE ENTREGA**
```javascript
Validaciones:
✓ Número acta único
✓ Mes no duplicado (1 acta por mes máximo)
✓ Artículos esperados según calendario
✓ Cantidades dentro de rango ±10%
✓ Proveedor = contratista conocido
✓ Fecha no futura
```

### **CAJA CHICA**
```javascript
Validaciones:
✓ Cada artículo <= $1,000
✓ Total <= límite mensual (ej: $5,000)
✓ Mínimo 1 artículo
✓ Máximo 20 artículos por caja chica
✓ Documentos justificantes adjuntos (opcional)
```

### **SOLICITUD DE PEDIDO**
```javascript
Validaciones:
✓ Número solicitud único
✓ Proveedor seleccionado
✓ Artículos existen en catálogo
✓ Monto estimado > 0
✓ Fecha estimada de llegada >= hoy
✓ Responsable no vacío
```

### **ACTA DE FALLO**
```javascript
Validaciones:
✓ Número fallo único
✓ Contrato referenciado existe
✓ Artículos coinciden con contrato
✓ Número entrega <= total entregas contrato
✓ Monto acumulado <= monto total contrato
✓ Cantidades dentro de rango esperado
```

---

## 📊 CAMBIOS EN REPORTES

### **Historial de Entradas**

**Antes:** Flat list de todas las entradas mezcladas  
**Después:** Agrupado por tipo de documento

```
┌─ FACTURAS (7 documentos)
│  ├─ FAC-2026-0045: Distribuidora X, $5,000 ✓
│  ├─ FAC-2026-0046: Proveedor Y, $2,300 ✓
│  └─ FAC-2026-0047: Empresa Z, $8,500 ✓
│
├─ ACTAS DE ENTREGA (4 documentos)
│  ├─ ACT-2026-02: Feb - Limpieza, $1,200 ✓
│  ├─ ACT-2026-03: Mar - Químicos, $1,500 ✓
│  └─ ACT-2026-04: Abr - Limpieza, $1,300 ✓
│
├─ CAJA CHICA (2 documentos)
│  ├─ CAJA-2026-03: Mar, $4,800 ✓
│  └─ CAJA-2026-04: Abr, $3,200 ✓
│
├─ SOLICITUDES DE PEDIDO (3 documentos)
│  ├─ SOL-2026-0145: Proveedor A (recibida)
│  ├─ SOL-2026-0146: Proveedor B (parcial)
│  └─ SOL-2026-0147: Proveedor C (pendiente)
│
└─ ACTAS DE FALLO (1 documento)
   └─ FALLO-2026-03: Contrato 2025-0089, Entrega 3/12 ✓
```

---

## 🔍 AGRUPACIÓN DE ARTÍCULOS

### **Ejemplo: Factura con múltiples artículos**

```
FACTURA FAC-2026-0047
Proveedor: Distribuidora de Limpieza
Fecha: 2026-04-25
Número Factura: FACT-2026-001

┌─────────────────────────────────────────┐
│ ARTÍCULOS EN ESTA FACTURA               │
├─────────────────────────────────────────┤
│ 1. Bio papel sanitario                  │
│    10 PIEZA × $55.58 = $555.80          │
│    + IVA 16% = $644.72                  │
│                                         │
│ 2. Bio pinol                            │
│    5 LITRO × $33.64 = $168.20           │
│    + IVA 16% = $195.11                  │
│                                         │
│ 3. Biofabuloso lavanda                  │
│    3 LITRO × $39.44 = $118.32           │
│    + IVA 16% = $137.25                  │
├─────────────────────────────────────────┤
│ TOTALES:                                │
│ Subtotal s/IVA: $842.32                 │
│ IVA 16%:        $134.77                 │
│ TOTAL c/IVA:    $977.09                 │
└─────────────────────────────────────────┘
```

---

## 🎨 INTERFAZ DE USUARIO MEJORADA

### **Pantalla 1: Seleccionar tipo de documento**

```
┌──────────────────────────────────────────┐
│ Registrar nueva entrada                  │
├──────────────────────────────────────────┤
│                                          │
│ ¿Qué tipo de entrada es?                │
│                                          │
│ ○ Factura de proveedor                  │
│ ○ Acta de entrega (material calendriz.) │
│ ○ Factura de caja chica                 │
│ ○ Solicitud de pedido                   │
│ ○ Acta de fallo (entregas parciales)    │
│                                          │
│        [ Continuar ]                    │
└──────────────────────────────────────────┘
```

### **Pantalla 2: Crear o seleccionar documento**

```
¿Nuevo documento o usar uno existente?

[ Crear nuevo documento FAC-2026-0048 ]

O selecciona uno pendiente:
├─ FAC-2026-0046 (En progreso) - $2,300
├─ FAC-2026-0047 (En progreso) - $8,500
└─ NONE

Selecciona: FAC-2026-0048 ✓
```

### **Pantalla 3: Datos del documento**

```
FACTURA FAC-2026-0048
─────────────────────────────────────

Número factura: FACT-2026-001
RFC proveedor:  XXX010101ABC
Proveedor:      Distribuidora Y
Fecha factura:  2026-04-25
Responsable:    Juan Pérez

[ Guardar datos del documento ]
```

### **Pantalla 4: Agregar artículos (tabla)**

```
ARTÍCULOS EN FAC-2026-0048
────────────────────────────────────────

Artículo          Cantidad Unitario  Total s/IVA
─────────────────────────────────────────────
Bio papel         10       $55.58    $555.80
Bio pinol          5       $33.64    $168.20
Biofabuloso        3       $39.44    $118.32
                                     ─────────
                                    $842.32

[+ Agregar otro artículo]

Monto s/IVA:  $842.32
IVA 16%:      $134.77
Monto c/IVA:  $977.09

[ Guardar factura completa ]
```

---

## 📈 MÉTRICAS Y REPORTES NUEVOS

### **Dashboard de Entradas**

```
RESUMEN POR TIPO DE DOCUMENTO

Facturas:           7 documentos | $45,200 total
Actas Entrega:      4 documentos | $5,300 total
Caja Chica:         2 documentos | $8,000 total
Solicitudes:        3 documentos | $12,500 (estimado)
Actas Fallo:        1 documento  | $3,000 (parcial)
────────────────────────────────────────────────
TOTAL ENTRADAS:    17 documentos | $73,000+

Artículos agregados: 47 artículos
Documentos pendientes: 2
Documentos completos: 15
```

---

## 🔄 INTEGRACIÓN CON STOCK

Cada artículo dentro de un documento afecta el stock:

```
ARTÍCULO: Bio papel (M-2160007)

Documento             Cantidad  Tipo
────────────────────────────────────
Stock inicial:        247       CATALOGO
FAC-2026-0045         +50       FACTURA
FAC-2026-0047         +10       FACTURA
ACT-2026-04           +5        ACTA_ENTREGA
CAJA-2026-04          +2        CAJA_CHICA
────────────────────────────────────
Stock actual:         314       TOTAL
```

---

## 🎯 VENTAJAS DE ESTA ARQUITECTURA

1. **Flexibilidad** — Soporta múltiples tipos de documento sin forzar datos
2. **Claridad** — Cada tipo tiene su flujo y validaciones específicas
3. **Agrupación** — Los artículos se ven en contexto de su documento
4. **Auditoría** — Trazabilidad completa de qué llegó por dónde
5. **Reportes** — Se pueden agrupar y analizar por tipo de documento
6. **Escalabilidad** — Fácil agregar nuevos tipos de documento en el futuro
7. **Control** — Validaciones específicas por tipo previenen errores

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### **Fase 1: Infraestructura (2 horas)**
```
✓ Crear módulo DocumentosEntrada
✓ Agregar tipos de documento (enum)
✓ Crear estructura de datos mejorada
✓ Implementar validadores por tipo
```

### **Fase 2: UI (3 horas)**
```
✓ Pantalla: Seleccionar tipo documento
✓ Pantalla: Crear/seleccionar documento
✓ Tabla: Agregar artículos múltiples
✓ Resumen: Totales automáticos
```

### **Fase 3: Integraciones (2 horas)**
```
✓ Integración con Stock
✓ Historial agrupado por tipo
✓ Reportes mejorados
✓ Dashboard nuevo
```

### **Fase 4: Testing (1 hora)**
```
✓ Validaciones por tipo
✓ Cálculos de totales
✓ Persistencia
✓ Edge cases
```

**Estimado total:** 8 horas  
**Estado:** Especificación completa, lista para desarrollo

---

## 📝 CONCLUSIÓN

Este nuevo sistema de **Documentos de Entrada** transforma el módulo actual en una solución profesional que maneja la complejidad real del negocio:

- ✅ Facturas normales (proveedor)
- ✅ Entregas calendarizadas (actas)
- ✅ Gastos menores (caja chica)
- ✅ Órdenes de compra (solicitudes)
- ✅ Entregas parciales (fallos)

Cada tipo con sus propias reglas, validaciones y ciclo de vida.

**¿Procedemos con la implementación?**
