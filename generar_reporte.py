from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import date

OUTPUT = r"C:\Users\sauli\OneDrive\Documentos\REPOSITORIO\files\reporte_tecnico_zoo_inventario.pdf"

# ── Colores institucionales ──────────────────────────────────────────────────
AZUL      = colors.HexColor("#2b6cb0")
AZUL_CLARO= colors.HexColor("#ebf4ff")
VERDE     = colors.HexColor("#276749")
VERDE_CLR = colors.HexColor("#f0fff4")
ROJO      = colors.HexColor("#9b2c2c")
ROJO_CLR  = colors.HexColor("#fff5f5")
AMBAR     = colors.HexColor("#92400e")
AMBAR_CLR = colors.HexColor("#fffbeb")
GRIS      = colors.HexColor("#718096")
GRIS_CLR  = colors.HexColor("#f7fafc")
OSCURO    = colors.HexColor("#1a202c")

# ── Estilos ──────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def estilo(nombre, base="Normal", **kwargs):
    return ParagraphStyle(nombre, parent=styles[base], **kwargs)

titulo_doc  = estilo("TituloDoc",  "Title",   fontSize=22, textColor=AZUL,   spaceAfter=4,  alignment=TA_CENTER)
subtitulo   = estilo("Subtitulo",  "Normal",  fontSize=11, textColor=GRIS,   spaceAfter=16, alignment=TA_CENTER)
seccion     = estilo("Seccion",    "Heading1", fontSize=13, textColor=AZUL,   spaceBefore=18, spaceAfter=6, borderPad=4)
subseccion  = estilo("Subseccion", "Heading2", fontSize=11, textColor=OSCURO, spaceBefore=10, spaceAfter=4)
cuerpo      = estilo("Cuerpo",     "Normal",   fontSize=9,  textColor=OSCURO, spaceAfter=4,  leading=14)
cuerpo_pe   = estilo("CuerpoPe",  "Normal",   fontSize=8,  textColor=GRIS,   spaceAfter=3,  leading=12)
pie         = estilo("Pie",        "Normal",   fontSize=7,  textColor=GRIS,   alignment=TA_CENTER)
etiq_verde  = estilo("EtiqVerde",  "Normal",   fontSize=8,  textColor=VERDE,  fontName="Helvetica-Bold")
etiq_rojo   = estilo("EtiqRojo",   "Normal",   fontSize=8,  textColor=ROJO,   fontName="Helvetica-Bold")
etiq_ambar  = estilo("EtiqAmbar",  "Normal",   fontSize=8,  textColor=AMBAR,  fontName="Helvetica-Bold")
etiq_gris   = estilo("EtiqGris",   "Normal",   fontSize=8,  textColor=GRIS,   fontName="Helvetica-Bold")

# ── Helpers ──────────────────────────────────────────────────────────────────
def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=8, spaceBefore=4)

def sp(n=6):
    return Spacer(1, n)

def tabla(data, col_widths, style_extra=None):
    base = [
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("BACKGROUND",  (0,0), (-1,0),  AZUL),
        ("TEXTCOLOR",   (0,0), (-1,0),  colors.white),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, GRIS_CLR]),
        ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0), (-1,-1), 6),
    ]
    if style_extra:
        base += style_extra
    return Table(data, colWidths=col_widths, style=TableStyle(base), repeatRows=1)

def badge(texto, color):
    return Paragraph(f"<b>{texto}</b>", estilo(f"badge_{texto}", "Normal",
        fontSize=7, textColor=color, fontName="Helvetica-Bold"))

# ── Encabezado / Pie de página ────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = letter
    # Encabezado
    canvas.setFillColor(AZUL)
    canvas.rect(0, h-36, w, 36, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(0.4*inch, h-22, "Zoo Tamatán — Sistema de Inventario V3.0")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w-0.4*inch, h-22, f"Reporte Técnico | {date.today().strftime('%d/%m/%Y')}")
    # Pie
    canvas.setFillColor(GRIS)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(w/2, 0.3*inch, f"Página {doc.page}  |  Confidencial — Uso interno")
    canvas.restoreState()

# ── Contenido ─────────────────────────────────────────────────────────────────
story = []

# Portada
story += [
    sp(60),
    Paragraph("REPORTE TÉCNICO INSTITUCIONAL", titulo_doc),
    Paragraph("Sistema de Inventario de Entradas — Zoo Tamatán", subtitulo),
    sp(4),
    Paragraph(f"Versión 3.0  |  Fecha: {date.today().strftime('%d de %B de %Y')}  |  Tamaulipas, México", subtitulo),
    sp(24),
]

# Tabla resumen ejecutivo portada
resumen_data = [
    ["Componente", "Estado"],
    ["Aplicación web funcional", "Operando"],
    ["Control de versiones Git", "Configurado"],
    ["Repositorio GitHub", "Publicado y sincronizado"],
    ["Claude como asistente técnico", "Activo"],
    ["Flujo changes + commit + push", "Operando correctamente"],
    ["Nivel institucional completo", "En progreso — Fases 1, 3 y 5 avanzadas"],
]
story.append(tabla(resumen_data, [3.2*inch, 3.2*inch]))
story.append(PageBreak())

# ── 1. DESCRIPCIÓN GENERAL ────────────────────────────────────────────────────
story += [sp(8), Paragraph("1. Descripción General del Sistema", seccion), hr()]
story.append(Paragraph(
    "El Sistema de Inventario Zoo Tamatán V3.0 es una aplicación web de página única (SPA) "
    "desarrollada en HTML5, CSS3 y JavaScript vanilla, sin dependencias externas ni framework. "
    "Opera de forma completamente autónoma desde el navegador, almacenando todos los datos en "
    "<b>localStorage</b> del equipo local. Su propósito es gestionar los documentos de entrada "
    "de insumos y materiales al zoológico, garantizando trazabilidad operativa, folios únicos "
    "y consistencia en el historial de movimientos.", cuerpo))
story.append(sp(6))

stack_data = [
    ["Tecnología", "Versión/Tipo", "Uso en el sistema"],
    ["HTML5 + CSS3", "Estándar W3C", "Estructura y estilos de la interfaz"],
    ["JavaScript (ES6+)", "Vanilla, sin framework", "Lógica de negocio, estado y renderizado"],
    ["localStorage API", "Browser API nativa", "Persistencia de datos e inventario"],
    ["JSON", "RFC 8259", "Serialización de documentos y bitácora"],
    ["Python http.server", "Python 3.13", "Servidor de desarrollo local (puerto 3000)"],
    ["Git + GitHub", "2.x / saulmeza-cpbt", "Control de versiones y repositorio remoto"],
]
story.append(tabla(stack_data, [1.8*inch, 1.8*inch, 2.8*inch]))

# ── 2. FUNCIONES IMPLEMENTADAS ────────────────────────────────────────────────
story += [sp(14), Paragraph("2. Funciones Implementadas", seccion), hr()]

story.append(Paragraph("2.1 Módulo de Entradas (5 tipos de documento)", subseccion))
tipos_data = [
    ["Tipo", "Prefijo", "Campos clave", "Área"],
    ["Factura de Proveedor", "FAC", "N. Factura, RFC, Proveedor, Fecha", "Área Destino"],
    ["Acta de Entrega", "ACT", "N. Acta, Mes, Proveedor, Fecha Entrega", "Área Destino"],
    ["Caja Chica", "CAJA", "Mes, Responsable", "Área Destino"],
    ["Solicitud de Pedido", "SOL", "N. Solicitud, Proveedor, Fecha", "Área Requirente"],
    ["Acta de Fallo", "FALLO", "N. Fallo, Contrato, N. Entrega (X/Y)", "Área Destino"],
]
story.append(tabla(tipos_data, [1.6*inch, 0.7*inch, 2.7*inch, 1.4*inch]))
story.append(sp(6))
story.append(Paragraph(
    "Cada documento incluye adicionalmente: <b>Folio auto-generado</b> (formato TIPO-AA-NNNN), "
    "<b>Responsable</b>, <b>Motivo / Justificación</b> (obligatorio), y tabla de artículos "
    "con código de inventario, cantidad y precio unitario.", cuerpo))

story += [sp(10), Paragraph("2.2 Gestión de Artículos (Paso 3)", subseccion)]
story.append(Paragraph(
    "El formulario de artículos incluye un sistema de <b>autocompletado inteligente</b> que "
    "consulta el catálogo histórico de documentos previos. Al escribir en el campo Artículo, "
    "aparece un dropdown con coincidencias filtradas por nombre o código de inventario (INV-XXX), "
    "ordenadas por frecuencia de uso. Al seleccionar una sugerencia se auto-rellenan nombre, "
    "código y precio unitario. El cálculo de IVA (16%) es automático en tiempo real.", cuerpo))

story += [sp(10), Paragraph("2.3 Trazabilidad Institucional", subseccion)]
traza_data = [
    ["Campo", "Tipo", "Aplica a", "Obligatorio"],
    ["Folio", "Auto-generado", "Todos los tipos", "Si"],
    ["Area Destino / Requirente", "Select (16 areas)", "Todos los tipos", "Si"],
    ["Responsable", "Texto libre", "Todos los tipos", "Si"],
    ["Motivo / Justificacion", "Textarea", "Todos los tipos", "Si — bloquea guardado"],
    ["Codigo de Inventario", "Texto (INV-XXX)", "Por articulo", "No"],
    ["Timestamp ISO", "Auto (Date.now)", "Todos los tipos", "Auto"],
]
story.append(tabla(traza_data, [1.7*inch, 1.2*inch, 1.5*inch, 1.9*inch]))

story += [sp(10), Paragraph("2.4 Bitácora Institucional", subseccion)]
story.append(Paragraph(
    "La bitácora persiste en <b>localStorage</b> (clave <i>zoo_tamatán_bitacora_v3</i>), "
    "almacena hasta 200 eventos en orden LIFO (más reciente primero) y registra: nivel "
    "(INFO / WARN / ERROR), mensaje descriptivo, entidad afectada (folio), acción realizada "
    "y timestamp en formato ISO 8601. Es visible desde la pestaña dedicada con código de color "
    "por nivel y botón de limpieza con confirmación.", cuerpo))

bit_data = [
    ["Evento registrado", "Nivel", "Incluye"],
    ["Inicio de sesion (carga de la app)", "INFO", "Timestamp, version"],
    ["Carga de documentos desde storage", "INFO", "Cantidad de documentos"],
    ["Seleccion de tipo de documento", "INFO", "Tipo seleccionado"],
    ["Articulo agregado al documento", "INFO", "Nombre, codigo INV"],
    ["Documento guardado correctamente", "INFO", "Folio, area, articulos, motivo"],
    ["Error al guardar en localStorage", "ERROR", "Mensaje de error"],
    ["Datos del inventario eliminados", "INFO", "Accion del usuario"],
]
story.append(tabla(bit_data, [2.5*inch, 0.9*inch, 2.9*inch]))

story += [sp(10), Paragraph("2.5 Dashboard", subseccion)]
story.append(Paragraph(
    "Muestra 4 tarjetas de resumen: entradas registradas, total de artículos, valor total con IVA "
    "y tipos de documento soportados. Incluye desglose por tipo y sección de alertas (vacía cuando "
    "todo está en orden, orientativa cuando no hay documentos registrados).", cuerpo))

# ── 3. ALCANCE ACTUAL ────────────────────────────────────────────────────────
story += [sp(14), Paragraph("3. Alcance Actual — Fases del Roadmap", seccion), hr()]

fases_data = [
    ["Fase", "Objetivo", "Estado", "Entregables completados"],
    ["Fase 1\nEstabilizacion", "Base estable sin errores", "Completada",
     "Bug fixes Paso 3, guard null en renderArticulos, validaciones de formulario"],
    ["Fase 2\nRefactorizacion modular", "Separar HTML/CSS/JS", "Pendiente",
     "Sistema aun en archivo unico (29KB+). Requiere separacion en modulos"],
    ["Fase 3\nTrazabilidad institucional", "Control operativo completo", "Avanzada",
     "Campo Motivo obligatorio, Area Destino/Requirente, Responsable, Folios unicos, Historial agrupado"],
    ["Fase 4\nSeguridad y roles", "Operacion controlada", "Pendiente",
     "Sin autenticacion ni control de acceso por modulo o perfil"],
    ["Fase 5\nAuditoria y cumplimiento", "Acciones auditables", "Parcial",
     "Bitacora persistente con nivel, entidad, accion y timestamp ISO"],
    ["Fase 6\nBackend y base de datos", "Salir del localStorage", "Pendiente",
     "Sin backend. Datos en localStorage (~5-10MB limite, un solo equipo)"],
    ["Fase 7\nProfesionalizacion del repo", "Artefacto tecnico presentable", "Parcial",
     "Repo publicado en GitHub con PRs y commits estructurados. Falta README institucional"],
]
story.append(tabla(fases_data, [0.9*inch, 1.4*inch, 0.9*inch, 3.2*inch],
    style_extra=[
        ("BACKGROUND", (2,1), (2,1), VERDE_CLR),
        ("BACKGROUND", (2,3), (2,3), AMBAR_CLR),
        ("BACKGROUND", (2,5), (2,5), AMBAR_CLR),
        ("BACKGROUND", (2,7), (2,7), AMBAR_CLR),
        ("BACKGROUND", (2,2), (2,2), ROJO_CLR),
        ("BACKGROUND", (2,4), (2,4), ROJO_CLR),
        ("BACKGROUND", (2,6), (2,6), ROJO_CLR),
    ]))

# ── 4. LO QUE FALTA ──────────────────────────────────────────────────────────
story += [sp(14), Paragraph("4. Brechas Identificadas — Lo que Falta", seccion), hr()]

brechas_data = [
    ["Brecha", "Impacto", "Prioridad", "Fase"],
    ["Sin autenticacion ni login", "Cualquier persona con acceso al equipo puede ver y modificar datos", "Alta", "4"],
    ["Sin control de roles", "No se puede restringir quien guarda, edita o elimina documentos", "Alta", "4"],
    ["Sin edicion de documentos", "Un error en la captura no tiene correccion sin borrar todo", "Alta", "1/3"],
    ["Sin eliminacion individual", "Solo existe 'limpiar todo'; no se puede borrar un documento especifico", "Alta", "1"],
    ["Sin exportacion (Excel/CSV/PDF)", "Los datos no pueden salir del navegador ni presentarse formalmente", "Alta", "3/7"],
    ["Sin busqueda ni filtros", "Con muchos documentos el historial se vuelve ilegible", "Media", "3"],
    ["Sin backend ni base de datos", "Datos en un solo equipo, sin respaldo automatico ni multi-usuario", "Alta", "6"],
    ["Sin modulo de Salidas", "El inventario solo registra entradas; no hay control de consumo", "Alta", "Nuevo"],
    ["Sin modulo de Stock", "No hay saldo en tiempo real de existencias por articulo o area", "Alta", "Nuevo"],
    ["Sin reportes ni graficas", "No hay indicadores de consumo, proveedor o area para toma de decisiones", "Media", "3/7"],
    ["README institucional incompleto", "El repositorio no esta documentado para terceros ni para mantenimiento", "Media", "7"],
    ["Archivo HTML monolitico", "Todo el codigo en un solo archivo dificulta mantenimiento y pruebas", "Media", "2"],
    ["Sin pruebas automatizadas", "Las validaciones criticas (RFC, montos) no tienen tests unitarios", "Media", "1/2"],
    ["Bitacora sin usuario", "La auditoria registra acciones pero no sabe quien las hizo (sin login)", "Alta", "4/5"],
]
story.append(tabla(brechas_data, [2.0*inch, 2.4*inch, 0.8*inch, 0.6*inch],
    style_extra=[
        ("BACKGROUND", (2,1),  (2,1),  ROJO_CLR),
        ("BACKGROUND", (2,2),  (2,2),  ROJO_CLR),
        ("BACKGROUND", (2,3),  (2,3),  ROJO_CLR),
        ("BACKGROUND", (2,4),  (2,4),  ROJO_CLR),
        ("BACKGROUND", (2,5),  (2,5),  ROJO_CLR),
        ("BACKGROUND", (2,7),  (2,7),  ROJO_CLR),
        ("BACKGROUND", (2,8),  (2,8),  ROJO_CLR),
        ("BACKGROUND", (2,9),  (2,9),  ROJO_CLR),
        ("BACKGROUND", (2,13), (2,13), ROJO_CLR),
        ("BACKGROUND", (2,6),  (2,6),  AMBAR_CLR),
        ("BACKGROUND", (2,10), (2,10), AMBAR_CLR),
        ("BACKGROUND", (2,11), (2,11), AMBAR_CLR),
        ("BACKGROUND", (2,12), (2,12), AMBAR_CLR),
    ]))
story.append(PageBreak())

# ── 5. PERFILES DE USUARIO ────────────────────────────────────────────────────
story += [sp(8), Paragraph("5. Perfiles de Usuario Propuestos", seccion), hr()]
story.append(Paragraph(
    "El sistema actualmente no implementa autenticacion ni control de acceso. A continuacion se "
    "definen los perfiles recomendados para la Fase 4 del roadmap, con sus responsabilidades, "
    "acciones permitidas y restricciones.", cuerpo))
story.append(sp(6))

perfiles = [
    {
        "nombre": "ADMINISTRADOR DEL SISTEMA",
        "descripcion": "Responsable tecnico y operativo del sistema. Control total.",
        "acciones": [
            "Registrar, editar y eliminar cualquier documento",
            "Gestionar usuarios y asignar roles",
            "Ver y limpiar la bitacora institucional",
            "Exportar datos (Excel, CSV, PDF)",
            "Configurar areas del zoologico y catalogo de articulos",
            "Limpiar datos del inventario",
            "Ver todos los modulos: Dashboard, Entradas, Salidas, Stock, Reportes, Bitacora",
        ],
        "restricciones": ["Sin restricciones operativas"],
        "color": AZUL, "bg": AZUL_CLARO,
    },
    {
        "nombre": "CAPTURISTA / OPERADOR DE ALMACEN",
        "descripcion": "Personal de almacen responsable del registro diario de documentos.",
        "acciones": [
            "Registrar documentos de entrada (los 5 tipos)",
            "Agregar y quitar articulos del documento en curso",
            "Ver su propio historial de entradas del dia",
            "Consultar catalogo de articulos existentes (autocomplete)",
            "Ver Dashboard general",
        ],
        "restricciones": [
            "No puede editar ni eliminar documentos ya guardados",
            "No puede ver la bitacora completa",
            "No puede gestionar usuarios ni configuracion",
            "No puede exportar datos",
        ],
        "color": VERDE, "bg": VERDE_CLR,
    },
    {
        "nombre": "JEFE DE AREA / SUPERVISOR",
        "descripcion": "Responsable de un area del zoologico. Supervision y validacion.",
        "acciones": [
            "Ver todos los documentos de su area (Destino o Requirente)",
            "Validar/aprobar solicitudes de pedido generadas por su area",
            "Ver Dashboard filtrado por su area",
            "Consultar reportes de consumo de su area",
            "Exportar historial de su area",
        ],
        "restricciones": [
            "No puede ver documentos de otras areas",
            "No puede registrar documentos directamente",
            "No puede gestionar usuarios",
        ],
        "color": colors.HexColor("#6b21a8"), "bg": colors.HexColor("#f5f3ff"),
    },
    {
        "nombre": "DIRECTOR / AUDITOR",
        "descripcion": "Perfil de solo lectura con acceso total para auditoria y toma de decisiones.",
        "acciones": [
            "Ver Dashboard general y por area",
            "Consultar todos los documentos e historial completo",
            "Ver bitacora institucional completa",
            "Generar y exportar cualquier reporte",
            "Ver indicadores de consumo, proveedor y area",
        ],
        "restricciones": [
            "No puede registrar, editar ni eliminar documentos",
            "No puede gestionar usuarios",
            "No puede limpiar datos ni bitacora",
        ],
        "color": AMBAR, "bg": AMBAR_CLR,
    },
]

for p in perfiles:
    encab = [[Paragraph(p["nombre"], estilo("ph", "Normal",
        fontSize=10, textColor=colors.white, fontName="Helvetica-Bold"))]]
    t_enc = Table(encab, colWidths=[6.4*inch],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), p["color"]),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
        ]))
    story.append(t_enc)
    story.append(Paragraph(p["descripcion"],
        estilo("pdesc", "Normal", fontSize=9, textColor=OSCURO,
               backColor=p["bg"], leftIndent=10, rightIndent=10,
               spaceBefore=0, spaceAfter=0, borderPad=6, leading=14)))

    acciones_txt = "<br/>".join(f"&nbsp;&nbsp;+ {a}" for a in p["acciones"])
    restricc_txt = "<br/>".join(f"&nbsp;&nbsp;- {r}" for r in p["restricciones"])

    detalle = [[
        Paragraph(f"<b>Acciones permitidas:</b><br/>{acciones_txt}",
            estilo("pacc", "Normal", fontSize=8, textColor=OSCURO, leading=13)),
        Paragraph(f"<b>Restricciones:</b><br/>{restricc_txt}",
            estilo("pres", "Normal", fontSize=8, textColor=ROJO, leading=13)),
    ]]
    t_det = Table(detalle, colWidths=[3.2*inch, 3.2*inch],
        style=TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.white),
            ("GRID",       (0,0), (-1,-1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
    story.append(t_det)
    story.append(sp(10))

# ── 6. PRÓXIMOS PASOS PRIORIZADOS ────────────────────────────────────────────
story += [sp(6), Paragraph("6. Proximos Pasos Priorizados", seccion), hr()]

proximos_data = [
    ["#", "Accion", "Fase", "Impacto", "Esfuerzo"],
    ["1", "Agregar edicion y eliminacion individual de documentos", "1/3", "Alto", "Medio"],
    ["2", "Exportacion a Excel/CSV desde el historial", "3", "Alto", "Medio"],
    ["3", "Busqueda y filtros en historial (por tipo, area, fecha)", "3", "Alto", "Bajo"],
    ["4", "README institucional completo en GitHub", "7", "Alto", "Bajo"],
    ["5", "Diseno de login y perfiles (sin backend aun, localStorage)", "4", "Alto", "Alto"],
    ["6", "Modulo de Salidas (consumo de insumos por area)", "Nuevo", "Alto", "Alto"],
    ["7", "Separacion del archivo HTML en modulos (HTML/CSS/JS)", "2", "Medio", "Alto"],
    ["8", "Diseno del modelo de datos para migracion a MySQL", "6", "Alto", "Medio"],
    ["9", "Graficas de consumo por area y proveedor en Dashboard", "3/7", "Medio", "Medio"],
    ["10", "Tests unitarios para validaciones criticas (RFC, montos)", "1/2", "Medio", "Medio"],
]
story.append(tabla(proximos_data, [0.3*inch, 2.8*inch, 0.6*inch, 0.8*inch, 0.8*inch]))

# ── 7. MÉTRICAS DEL REPOSITORIO ──────────────────────────────────────────────
story += [sp(14), Paragraph("7. Estado del Repositorio GitHub", seccion), hr()]

repo_data = [
    ["Metrica", "Valor"],
    ["Repositorio", "github.com/saulmeza-cpbt/inventario-zoologico"],
    ["Rama principal", "main"],
    ["Commits registrados", "4 commits (sesion actual)"],
    ["Pull Requests abiertos", "3 PRs (fix/docs, feat/ux, feat/institucional)"],
    ["Convencion de commits", "fix/feat/style/chore + scope + descripcion"],
    ["Convencion de ramas", "feat/, fix/, style/ + descripcion-kebab-case"],
    ["Archivo principal", "zoo11AM_v3.0_DOCUMENTOS_ENTRADA.html (29KB+)"],
    ["Documentacion tecnica", "ESPECIFICACION_V3.md, GUIA_USO_V3.md, RESUMEN_EJECUTIVO.md"],
]
story.append(tabla(repo_data, [2.4*inch, 4.0*inch]))

# ── Cierre ─────────────────────────────────────────────────────────────────────
story += [
    sp(20), hr(),
    Paragraph(
        "Este reporte fue generado automaticamente a partir del estado actual del proyecto. "
        "Las brechas identificadas en la Seccion 4 constituyen la agenda tecnica inmediata "
        "para llevar el sistema al nivel institucional definido en el Roadmap Tecnico. "
        "Se recomienda priorizar autenticacion, exportacion de datos y modulo de Salidas "
        "como proximos entregables criticos.",
        estilo("cierre", "Normal", fontSize=8, textColor=GRIS, alignment=TA_CENTER, leading=13)
    ),
    sp(6),
    Paragraph(
        f"Zoo Tamatán | Sistema de Inventario V3.0 | Generado: {date.today().strftime('%d/%m/%Y')} | Confidencial",
        pie
    ),
]

# ── Build ──────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    leftMargin=0.6*inch, rightMargin=0.6*inch,
    topMargin=0.7*inch,  bottomMargin=0.6*inch,
)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generado: {OUTPUT}")
