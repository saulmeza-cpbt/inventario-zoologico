# 📚 GUÍA DE USO: Sistema de Documentos de Entrada V3.0
## Zoo Tamatán - Inventario Avanzado

**Fecha:** 30/05/2026  
**Versión:** 3.0 - Documentos de Entrada Multi-tipo  
**Estado:** Listo para usar

---

## 🎯 ¿Qué es lo NUEVO en V3.0?

**V2.1** → Solo soportaba entradas por **factura simple**  
**V3.0** → Soporta **5 tipos de documento** diferentes:

| Tipo | Icono | Uso | Ejemplo |
|------|-------|-----|---------|
| **Factura** | 📋 | Compra a proveedor | FAC-26-0045 |
| **Acta de Entrega** | 📑 | Material calendarizado | ACT-26-04 |
| **Caja Chica** | 💰 | Gastos <$1,000 | CAJA-26-04 |
| **Solicitud de Pedido** | 🛒 | Orden de compra pendiente | SOL-26-0147 |
| **Acta de Fallo** | 📦 | Entregas parciales anuales | FALLO-26-03 |

Cada documento **agrupa múltiples artículos** bajo un mismo documento de referencia.

---

## 🚀 FLUJO DE TRABAJO (4 pasos)

```
┌─────────────────────────────────────────────┐
│ PASO 1: Selecciona tipo de documento         │
│ ├─ 📋 Factura                               │
│ ├─ 📑 Acta de Entrega                       │
│ ├─ 💰 Caja Chica                            │
│ ├─ 🛒 Solicitud de Pedido                   │
│ └─ 📦 Acta de Fallo                         │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ PASO 2: Completa datos del documento        │
│ ├─ Número/Folio (auto-generado)            │
│ ├─ RFC / Proveedor                          │
│ ├─ Fecha                                    │
│ └─ Responsable (quién recibe)              │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ PASO 3: Agrega artículos (ilimitados)       │
│ ├─ Nombre del artículo                      │
│ ├─ Cantidad                                 │
│ ├─ Precio unitario                          │
│ └─ [+ Agregar otro] [Quitar]               │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ PASO 4: Valida y guarda el documento        │
│ ├─ Subtotal s/IVA                          │
│ ├─ IVA 16%                                 │
│ ├─ Total c/IVA                             │
│ └─ [✓ Guardar] [⟲ Limpiar]                 │
└─────────────────────────────────────────────┘
```

---

## 📋 USO POR TIPO DE DOCUMENTO

### **1️⃣ FACTURA (Proveedor Normal)**

**Cuándo usar:**
- Compra a un proveedor con factura oficial
- Monto generalmente >= $1,000
- Número de factura único

**Campos a llenar:**
```
├─ Folio:           FAC-26-0045 (auto-generado)
├─ Número Factura:  FACT-2026-001
├─ RFC Proveedor:   XXX010101ABC
├─ Nombre Proveedor: Distribuidora de Limpieza Y
├─ Fecha Factura:   2026-04-25
└─ Responsable:     Juan Pérez (quien recibe)
```

**Ejemplo de artículos:**
```
Artículo 1: Bio papel sanitario
  • Cantidad: 10 PIEZA
  • Unitario: $55.58
  • Total: $555.80

Artículo 2: Bio pinol
  • Cantidad: 5 LITRO
  • Unitario: $33.64
  • Total: $168.20

Artículo 3: Biofabuloso
  • Cantidad: 3 LITRO
  • Unitario: $39.44
  • Total: $118.32

═══════════════════════════════════
Subtotal s/IVA:    $842.32
IVA 16%:           $134.77
TOTAL c/IVA:       $977.09
═══════════════════════════════════
```

---

### **2️⃣ ACTA DE ENTREGA (Material Calendarizado)**

**Cuándo usar:**
- Material de limpieza que entra cada mes
- Cloro y químicos
- Calendarizado al inicio del año
- Es lo que das para cotejar el material

**Campos a llenar:**
```
├─ Folio:           ACT-26-04 (auto-generado)
├─ Número Acta:     ACT-2026-04
├─ Mes:             Abril 2026
├─ Nombre Proveedor: Contratista de Limpieza X
├─ Fecha Entrega:   2026-04-30
└─ Responsable:     María López
```

**Ejemplo:**
```
ACT-26-04: Entrega mensual de abril

Artículo 1: Cloro granulado
  • Cantidad: 20 kg
  • Unitario: $150.00
  • Total: $3,000.00

Artículo 2: Desinfectante
  • Cantidad: 10 LITRO
  • Unitario: $80.00
  • Total: $800.00

═══════════════════════════════════
Subtotal s/IVA:    $3,800.00
IVA 16%:           $608.00
TOTAL c/IVA:       $4,408.00
═══════════════════════════════════
```

---

### **3️⃣ CAJA CHICA (Gastos Menores)**

**Cuándo usar:**
- Compras menores a $1,000 c/u
- Múltiples proveedores pequeños
- Reporte mensual de gastos menores

**Campos a llenar:**
```
├─ Folio:     CAJA-26-04 (auto-generado)
├─ Mes:       Abril 2026
└─ Responsable: Gerente de Compras
```

**Ejemplo:**
```
CAJA-26-04: Abril 2026 - Gastos menores

Artículo 1: Pegamento industrial
  • Cantidad: 3 BOTE
  • Unitario: $250.00
  • Total: $750.00

Artículo 2: Escobas
  • Cantidad: 12 PIEZA
  • Unitario: $45.00
  • Total: $540.00

Artículo 3: Papel higiénico
  • Cantidad: 5 PAQUETE
  • Unitario: $120.00
  • Total: $600.00

═══════════════════════════════════
Subtotal s/IVA:    $1,890.00
IVA 16%:           $302.40
TOTAL c/IVA:       $2,192.40
═══════════════════════════════════

✓ Total caja chica <= límite mensual ($5,000)
```

---

### **4️⃣ SOLICITUD DE PEDIDO (Orden de Compra)**

**Cuándo usar:**
- Pedido que enviaste a un proveedor
- Aún no llega la factura (está pendiente)
- Se genera primero, factura viene después

**Campos a llenar:**
```
├─ Folio:              SOL-26-0147 (auto-generado)
├─ Número Solicitud:   SOL-2026-0147
├─ Nombre Proveedor:   Proveedor Z
├─ Fecha Solicitud:    2026-04-25
└─ Responsable:        Jefe de Almacén
```

**Ejemplo:**
```
SOL-26-0147: Solicitud a Proveedor Z

Artículo 1: Uniformes para personal
  • Cantidad: 50 PIEZA
  • Unitario: $320.00
  • Total: $16,000.00

Artículo 2: Botas de seguridad
  • Cantidad: 30 PAR
  • Unitario: $280.00
  • Total: $8,400.00

═══════════════════════════════════
Subtotal s/IVA:    $24,400.00
IVA 16%:           $3,904.00
TOTAL c/IVA:       $28,304.00
═══════════════════════════════════

Estado: Solicitada (pendiente llegada)
```

---

### **5️⃣ ACTA DE FALLO (Entregas Parciales)**

**Cuándo usar:**
- Contrato con entregas mensuales
- Ej: Uniformes por $36,000/año = 12 entregas de $3,000
- Se entrega parcialmente hasta completar el total
- Calendarizado al inicio del ejercicio

**Campos a llenar:**
```
├─ Folio:              FALLO-26-03 (auto-generado)
├─ Número Fallo:       FALLO-2026-03
├─ Número Contrato:    CONT-2025-0089
├─ Número Entrega:     3/12 (tercera de doce)
└─ Responsable:        Jefe de Almacén
```

**Ejemplo:**
```
FALLO-26-03: Entrega 3 de 12 - Contrato 2025-0089

Total contrato:        $36,000.00
Entregas anteriores:   $6,000.00 (2 × $3,000)
Esta entrega:          $3,000.00
Total hasta ahora:     $9,000.00
Pendiente:             $27,000.00 (9 entregas)

Artículo 1: Uniformes grises
  • Cantidad: 50 PIEZA (de 600 en total)
  • Unitario: $60.00
  • Total: $3,000.00

═══════════════════════════════════
Subtotal s/IVA:    $3,000.00
IVA 16%:           $480.00
TOTAL c/IVA:       $3,480.00
═══════════════════════════════════

Estado: Conforme (entrega 3/12)
```

---

## 📊 DASHBOARD - Interpretando la información

### **Tarjetas de resumen:**
```
┌─────────────┬─────────────┬─────────────┬──────────────┐
│ 47 Entradas │ 156 Artículos │ $73,450.00 │ 5 Tipos Doc │
└─────────────┴─────────────┴─────────────┴──────────────┘
```

- **47 Entradas** = Total de documentos registrados (sin importar tipo)
- **156 Artículos** = Total de líneas de artículos en todos los documentos
- **$73,450.00** = Valor total con IVA incluido
- **5 Tipos Doc** = Cantidad de tipos de documento soportados

### **Resumen por tipo de documento:**
```
📋 Facturas: 7 documentos
📑 Actas de Entrega: 4 documentos
💰 Caja Chica: 2 documentos
🛒 Solicitudes de Pedido: 3 documentos
📦 Actas de Fallo: 1 documento
```

---

## 📈 HISTORIAL - Agrupado por tipo

El historial automáticamente agrupa todos los documentos por tipo:

```
📋 FACTURAS (7 documentos)
├─ FAC-26-0045 | 3 artículos | $977.09 | 25/04/2026
├─ FAC-26-0046 | 5 artículos | $2,300.00 | 26/04/2026
└─ FAC-26-0047 | 2 artículos | $8,500.00 | 27/04/2026

📑 ACTAS DE ENTREGA (4 documentos)
├─ ACT-26-02 | 1 artículo | $1,200.00 | 28/02/2026
├─ ACT-26-03 | 1 artículo | $1,500.00 | 31/03/2026
└─ ACT-26-04 | 2 artículos | $4,408.00 | 30/04/2026

💰 CAJA CHICA (2 documentos)
├─ CAJA-26-03 | 8 artículos | $4,800.00 | 30/03/2026
└─ CAJA-26-04 | 5 artículos | $2,192.40 | 29/04/2026

🛒 SOLICITUDES (3 documentos)
├─ SOL-26-0145 | 2 artículos | $12,500.00 | 20/04/2026
├─ SOL-26-0146 | 3 artículos | $8,300.00 | 22/04/2026
└─ SOL-26-0147 | 2 artículos | $28,304.00 | 25/04/2026

📦 ACTAS DE FALLO (1 documento)
└─ FALLO-26-03 | 1 artículo | $3,480.00 | 30/04/2026
```

---

## ⚙️ CARACTERÍSTICAS TÉCNICAS

### **Folio automático**

El sistema **auto-genera** folios únicos:

```
Tipo              Formato         Ejemplo
Factura          FAC-YY-XXXX      FAC-26-0048
Acta Entrega     ACT-YY-XXXX      ACT-26-04
Caja Chica       CAJA-YY-XXXX     CAJA-26-04
Solicitud        SOL-YY-XXXX      SOL-26-0147
Acta Fallo       FALLO-YY-XXXX    FALLO-26-03

YY = Últimos 2 dígitos del año
XXXX = Número secuencial para el tipo
```

### **Cálculos automáticos**

- **Subtotal s/IVA** = Suma(cantidad × unitario)
- **IVA 16%** = Subtotal × 0.16
- **Total c/IVA** = Subtotal + IVA

Ejemplo:
```
Artículo 1:  10 × $55.58 = $555.80
Artículo 2:   5 × $33.64 = $168.20
Artículo 3:   3 × $39.44 = $118.32
              ─────────────────────
Subtotal:              $842.32
IVA (16%):             $134.77
              ─────────────────────
TOTAL:                 $977.09
```

### **Persistencia (Almacenamiento)**

- **Almacenamiento local** en el navegador (localStorage)
- **Automático** cuando guardas un documento
- **Recuperación** cada vez que cargas la página
- Los datos persisten indefinidamente (o hasta limpiar)

---

## 🔍 VALIDACIONES POR TIPO

### **FACTURA:**
- ✓ Número factura no vacío
- ✓ RFC válido (18 caracteres)
- ✓ Proveedor no vacío
- ✓ Mínimo 1 artículo

### **ACTA DE ENTREGA:**
- ✓ Número acta no vacío
- ✓ Mes no vacío
- ✓ Mínimo 1 artículo

### **CAJA CHICA:**
- ✓ Mes no vacío
- ✓ Mínimo 1 artículo
- ✓ (Opcional) Total <= $5,000

### **SOLICITUD DE PEDIDO:**
- ✓ Número solicitud no vacío
- ✓ Proveedor no vacío
- ✓ Mínimo 1 artículo

### **ACTA DE FALLO:**
- ✓ Número fallo no vacío
- ✓ Número contrato no vacío
- ✓ Número entrega no vacío (ej: 3/12)
- ✓ Mínimo 1 artículo

---

## 💡 MEJORES PRÁCTICAS

### **1. Organiza por documento**

❌ **Mal:** Crear 5 documentos por día sin agrupar
```
FAC-26-0001: 1 artículo
FAC-26-0002: 1 artículo
FAC-26-0003: 1 artículo
FAC-26-0004: 1 artículo
FAC-26-0005: 1 artículo
```

✅ **Bien:** Un documento por factura, varios artículos
```
FAC-26-0001: 
  ├─ Artículo A
  ├─ Artículo B
  ├─ Artículo C
  ├─ Artículo D
  └─ Artículo E
```

### **2. Usa el tipo correcto**

❌ **Mal:** Todo como "Factura"
```
FAC-26-0001: Material de limpieza (debe ser ACT)
FAC-26-0002: Gastos menores (debe ser CAJA)
FAC-26-0003: Orden pendiente (debe ser SOL)
```

✅ **Bien:** Usa el tipo exacto
```
ACT-26-04: Material de limpieza (abril)
CAJA-26-04: Gastos menores (abril)
SOL-26-0147: Orden a Proveedor X
```

### **3. Datos completos**

❌ **Incompleto:**
```
Folio:      ACT-26-04
Artículos:  [sin completar]
```

✅ **Completo:**
```
Folio:              ACT-26-04
Número Acta:        ACT-2026-04
Mes:                Abril 2026
Proveedor:          Contratista X
Fecha Entrega:      2026-04-30
Responsable:        María López
Artículos:          3 agregados
```

### **4. Verifica totales**

Siempre **verifica los totales antes de guardar**:
```
Subtotal s/IVA: $842.32
IVA 16%:        $134.77
─────────────────────────
TOTAL c/IVA:    $977.09 ✓
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### **"No aparece mi documento guardado"**

1. Comprueba que completaste **todos los campos obligatorios**
2. Verifica que haya al menos **1 artículo agregado**
3. Haz clic en **"✓ Guardar Documento"** (no solo rellenar campos)
4. Espera el mensaje: **"✓ Documento FAC-26-XXXX guardado"**

### **"Los números se multiplican o desaparecen"**

No refresques la página mientras escribes. El sistema guarda cada 2 segundos automáticamente.

### **"¿Cómo borro un documento?"**

En el historial, haz clic derecho en la fila y selecciona "Eliminar" (función en desarrollo).

Por ahora: Ve a Dashboard → [🗑️ Limpiar datos] si necesitas empezar de cero.

### **"¿Qué pasa si cierro la pestaña sin guardar?"**

Los datos **se guardan automáticamente cada 2 segundos**. No hay riesgo de pérdida.

---

## 📅 PRÓXIMAS CARACTERÍSTICAS (Roadmap)

**V3.1 (próximas 2 semanas):**
- ✓ Editar documentos guardados
- ✓ Eliminar documentos individuales
- ✓ Búsqueda y filtros avanzados
- ✓ Dark mode

**V3.2 (próximas 3 semanas):**
- ✓ Exportar a Excel/CSV
- ✓ Gráficos de tendencias
- ✓ Reportes por proveedor
- ✓ Integración con módulo de Stock

**V4.0 (este mes):**
- ✓ Backend con Node.js + Express + MySQL
- ✓ Multi-usuario con autenticación
- ✓ Sincronización en tiempo real
- ✓ API REST completa

---

## 📞 SOPORTE

Si tienes dudas o encuentras bugs:
1. Abre la **Consola** (F12)
2. Ve a **Consola** y busca el mensaje de error
3. Copia el error y comunícalo
4. Usa `APP.logger.getLogs()` para ver el historial

---

## ✅ CHECKLIST PARA EMPEZAR

- [ ] Abre `zoo11AM_v3.0_DOCUMENTOS_ENTRADA.html`
- [ ] Ve a tab **"📥 Entradas"**
- [ ] Elige un tipo de documento (ej: Factura)
- [ ] Completa los datos
- [ ] Agrega 3 artículos de prueba
- [ ] Verifica que el total esté correcto
- [ ] Haz clic en **"✓ Guardar Documento"**
- [ ] Mira el **Dashboard** - deberías ver los datos
- [ ] Revisa el **Historial** - tu documento debería estar ahí

¡**Listo para usar! 🚀**

---

## 📝 REGISTRO DE CAMBIOS

**V3.0** (30/05/2026)
- ✨ Sistema completo de Documentos de Entrada
- ✨ 5 tipos de documento (Factura, Acta, Caja Chica, Solicitud, Fallo)
- ✨ Agrupación por tipo en historial
- ✨ Cálculos automáticos de IVA
- ✨ Folio auto-generado
- ✨ Dashboard mejorado
- 🐛 Sistema redundante de almacenamiento
- 📊 Logger integrado

**V2.1** (30/05/2026)
- Entradas simples por factura
- Módulo de levantamiento
- Validaciones básicas

**V2.0** (Inicial)
- Sistema base

---

**Última actualización:** 30 de mayo de 2026  
**Sistema:** Zoo Tamatán - Tamaúlipas, México  
**Versión:** V3.0 - Documentos de Entrada Multi-tipo
