# -*- coding: utf-8 -*-
"""
Informe Técnico de Evolución — Zoo Tamatán V3.0
Comisión de Parques y Biodiversidad de Tamaulipas (CPBT)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os

# ──────────────────────────────────────────────
# PALETA DE COLORES
# ──────────────────────────────────────────────
VERDE_OSCURO   = HexColor("#1B4332")
VERDE_MEDIO    = HexColor("#2D6A4F")
VERDE_CLARO    = HexColor("#52B788")
VERDE_SUAVE    = HexColor("#D8F3DC")
GRIS_OSCURO    = HexColor("#212529")
GRIS_MEDIO     = HexColor("#495057")
GRIS_CLARO     = HexColor("#F8F9FA")
GRIS_BORDE     = HexColor("#DEE2E6")
AMARILLO_WARN  = HexColor("#FFF3CD")
AMARILLO_BRD   = HexColor("#FFC107")
ROJO_ERR       = HexColor("#F8D7DA")
ROJO_BRD       = HexColor("#DC3545")
AZUL_INFO      = HexColor("#D1ECF1")
AZUL_BRD       = HexColor("#17A2B8")
BLANCO         = colors.white

OUTPUT_PATH = r"C:\Users\sauli\OneDrive\Documentos\REPOSITORIO\files\informe_tecnico_evolucion_zoo_tamatan_v3.pdf"

# ──────────────────────────────────────────────
# ESTILOS
# ──────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent="Normal", **kwargs):
    return ParagraphStyle(name, parent=styles[parent], **kwargs)

STYLE_COVER_TITLE = make_style("CoverTitle", "Title",
    fontSize=26, leading=32, textColor=BLANCO,
    fontName="Helvetica-Bold", alignment=TA_LEFT)

STYLE_COVER_SUB = make_style("CoverSub", "Normal",
    fontSize=13, leading=18, textColor=HexColor("#B7E4C7"),
    fontName="Helvetica", alignment=TA_LEFT)

STYLE_COVER_META = make_style("CoverMeta", "Normal",
    fontSize=10, leading=14, textColor=HexColor("#95D5B2"),
    fontName="Helvetica", alignment=TA_LEFT)

STYLE_H1 = make_style("H1", "Heading1",
    fontSize=14, leading=20, textColor=VERDE_OSCURO,
    fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=8,
    borderPad=0)

STYLE_H2 = make_style("H2", "Heading2",
    fontSize=11, leading=16, textColor=VERDE_MEDIO,
    fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=6)

STYLE_H3 = make_style("H3", "Heading3",
    fontSize=10, leading=14, textColor=GRIS_OSCURO,
    fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4)

STYLE_BODY = make_style("Body", "Normal",
    fontSize=9, leading=14, textColor=GRIS_OSCURO,
    fontName="Helvetica", spaceAfter=4, alignment=TA_JUSTIFY)

STYLE_BODY_LEFT = make_style("BodyLeft", "Normal",
    fontSize=9, leading=14, textColor=GRIS_OSCURO,
    fontName="Helvetica", spaceAfter=4, alignment=TA_LEFT)

STYLE_CODE = make_style("Code", "Code",
    fontSize=8, leading=12, textColor=HexColor("#C7253E"),
    fontName="Courier", backColor=HexColor("#F8F9FA"),
    borderPad=4, spaceAfter=4)

STYLE_CAPTION = make_style("Caption", "Normal",
    fontSize=8, leading=11, textColor=GRIS_MEDIO,
    fontName="Helvetica-Oblique", alignment=TA_CENTER)

STYLE_LABEL = make_style("Label", "Normal",
    fontSize=8, leading=11, textColor=BLANCO,
    fontName="Helvetica-Bold", alignment=TA_CENTER)

STYLE_METRIC_VAL = make_style("MetricVal", "Normal",
    fontSize=18, leading=22, textColor=VERDE_OSCURO,
    fontName="Helvetica-Bold", alignment=TA_CENTER)

STYLE_METRIC_LBL = make_style("MetricLbl", "Normal",
    fontSize=8, leading=11, textColor=GRIS_MEDIO,
    fontName="Helvetica", alignment=TA_CENTER)

STYLE_TOC_H1 = make_style("TOCH1", "Normal",
    fontSize=10, leading=15, textColor=GRIS_OSCURO,
    fontName="Helvetica-Bold")

STYLE_TOC_H2 = make_style("TOCH2", "Normal",
    fontSize=9, leading=14, textColor=GRIS_MEDIO,
    fontName="Helvetica", leftIndent=12)

STYLE_WARN = make_style("Warn", "Normal",
    fontSize=9, leading=13, textColor=HexColor("#856404"),
    fontName="Helvetica")

STYLE_ERR = make_style("Err", "Normal",
    fontSize=9, leading=13, textColor=HexColor("#721C24"),
    fontName="Helvetica")

STYLE_INFO = make_style("Info", "Normal",
    fontSize=9, leading=13, textColor=HexColor("#0C5460"),
    fontName="Helvetica")

# ──────────────────────────────────────────────
# HELPERS DE TABLAS
# ──────────────────────────────────────────────
def base_table_style(header_bg=VERDE_OSCURO, row_alt=VERDE_SUAVE):
    return TableStyle([
        # Encabezado
        ("BACKGROUND",    (0, 0), (-1, 0),  header_bg),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  7),
        ("TOPPADDING",    (0, 0), (-1, 0),  7),
        # Cuerpo
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("TEXTCOLOR",     (0, 1), (-1, -1), GRIS_OSCURO),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, row_alt]),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        # Bordes
        ("GRID",          (0, 0), (-1, -1), 0.4, GRIS_BORDE),
        ("BOX",           (0, 0), (-1, -1), 1,   VERDE_MEDIO),
        ("LINEBELOW",     (0, 0), (-1, 0),  1,   VERDE_MEDIO),
    ])

def info_box(text_paragraphs, bg=AZUL_INFO, border_color=AZUL_BRD):
    """Caja de información de ancho completo."""
    inner = [[p] for p in text_paragraphs]
    flat = [[p for p in text_paragraphs]]
    t = Table([[Paragraph("<br/>".join([
        p.text if hasattr(p, "text") else "" for p in text_paragraphs
    ]), STYLE_INFO)]], colWidths=[16.5*cm])
    # Mejor: una celda con todo el texto concatenado
    content = " ".join([
        para._cellvalues[0][0].getPlainText() if hasattr(para, "_cellvalues") else str(para)
        for para in text_paragraphs
    ]) if False else None

    rows = [[p] for p in text_paragraphs]
    col_w = [16.5*cm]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), bg),
        ("BOX",         (0, 0), (-1, -1), 1, border_color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",(0, 0), (-1, -1), 10),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0,0), (-1, -1), 6),
    ]))
    return t

# ──────────────────────────────────────────────
# FLOWABLE: LÍNEA SEPARADORA CON TÍTULO
# ──────────────────────────────────────────────
class SectionDivider(Flowable):
    def __init__(self, number, title, width=16.5*cm):
        super().__init__()
        self.number = number
        self.title = title
        self.width = width
        self.height = 28

    def draw(self):
        c = self.canv
        # Fondo verde
        c.setFillColor(VERDE_OSCURO)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        # Número en círculo
        c.setFillColor(VERDE_CLARO)
        c.circle(14, 14, 11, fill=1, stroke=0)
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(14, 10.5, str(self.number))
        # Título
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(32, 9, self.title)


class SubSectionDivider(Flowable):
    def __init__(self, title, width=16.5*cm):
        super().__init__()
        self.title = title
        self.width = width
        self.height = 20

    def draw(self):
        c = self.canv
        c.setFillColor(VERDE_SUAVE)
        c.roundRect(0, 0, self.width, self.height, 3, fill=1, stroke=0)
        c.setStrokeColor(VERDE_CLARO)
        c.setLineWidth(2)
        c.line(0, 0, 0, self.height)
        c.setFillColor(VERDE_OSCURO)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(8, 5.5, self.title)


class TimelineRow(Flowable):
    """Fila de timeline con punto, hora y descripción."""
    def __init__(self, time_str, commit, desc, is_pr=False, width=16.5*cm):
        super().__init__()
        self.time_str = time_str
        self.commit = commit
        self.desc = desc
        self.is_pr = is_pr
        self.width = width
        self.height = 22 if is_pr else 18

    def draw(self):
        c = self.canv
        dot_x = 35

        if self.is_pr:
            c.setFillColor(VERDE_CLARO)
            c.circle(dot_x, self.height/2, 7, fill=1, stroke=0)
            c.setFillColor(VERDE_OSCURO)
            c.setFont("Helvetica-Bold", 5)
            c.drawCentredString(dot_x, self.height/2 - 2.5, "PR")
            c.setFillColor(VERDE_OSCURO)
            c.setFont("Helvetica-Bold", 8.5)
        else:
            c.setFillColor(GRIS_BORDE)
            c.circle(dot_x, self.height/2, 4, fill=1, stroke=0)
            c.setFillColor(GRIS_MEDIO)
            c.setFont("Helvetica", 8)

        c.setFillColor(GRIS_MEDIO)
        c.setFont("Courier", 7.5)
        c.drawString(0, self.height/2 - 3.5, self.time_str)

        c.setFillColor(HexColor("#6C757D"))
        c.setFont("Courier", 7.5)
        c.drawString(48, self.height/2 - 3.5, self.commit)

        if self.is_pr:
            c.setFillColor(VERDE_OSCURO)
            c.setFont("Helvetica-Bold", 8.5)
        else:
            c.setFillColor(GRIS_OSCURO)
            c.setFont("Helvetica", 8.5)
        c.drawString(100, self.height/2 - 3.5, self.desc)

        # línea guía
        c.setStrokeColor(GRIS_BORDE)
        c.setLineWidth(0.5)
        c.line(35, 0, 35, self.height/2 - (7 if self.is_pr else 4))


class MetricsGrid(Flowable):
    """Grid de tarjetas de métricas 4x2."""
    def __init__(self, metrics, width=16.5*cm):
        super().__init__()
        self.metrics = metrics  # list of (value, label)
        self.width = width
        self.cols = 4
        self.card_w = width / self.cols
        self.card_h = 50
        rows = (len(metrics) + self.cols - 1) // self.cols
        self.height = rows * self.card_h

    def draw(self):
        c = self.canv
        for i, (val, lbl) in enumerate(self.metrics):
            col = i % self.cols
            row = i // self.cols
            x = col * self.card_w
            y = self.height - (row + 1) * self.card_h

            bg = VERDE_SUAVE if i % 2 == 0 else HexColor("#EDF6F9")
            c.setFillColor(bg)
            c.roundRect(x+2, y+2, self.card_w-4, self.card_h-4, 4, fill=1, stroke=0)
            c.setStrokeColor(GRIS_BORDE)
            c.setLineWidth(0.5)
            c.roundRect(x+2, y+2, self.card_w-4, self.card_h-4, 4, fill=0, stroke=1)

            c.setFillColor(VERDE_OSCURO)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(x + self.card_w/2, y + self.card_h/2 + 3, str(val))

            c.setFillColor(GRIS_MEDIO)
            c.setFont("Helvetica", 7)
            c.drawCentredString(x + self.card_w/2, y + self.card_h/2 - 10, lbl)


# ──────────────────────────────────────────────
# NUMERACIÓN DE PÁGINAS
# ──────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page_num = self._saved_page_states.index(dict(
            [(k, self.__dict__[k]) for k in self.__dict__ if k in self._saved_page_states[0]]
        )) + 1 if False else None

        # Footer bar
        self.setFillColor(VERDE_OSCURO)
        self.rect(0, 0, A4[0], 20*mm, fill=1, stroke=0)
        self.setFillColor(BLANCO)
        self.setFont("Helvetica", 7.5)
        self.drawString(1.5*cm, 8*mm, "Sistema de Inventario Zoo Tamatán V3.0 — CPBT Tamaulipas")
        self.setFont("Helvetica", 7.5)
        self.drawRightString(A4[0]-1.5*cm, 8*mm, "Informe Técnico de Evolución · 31 de mayo de 2026")

        # Línea accent
        self.setFillColor(VERDE_CLARO)
        self.rect(0, 20*mm, A4[0], 1.5*mm, fill=1, stroke=0)


def draw_cover(canv, W, H):
    """Dibuja la portada directamente en el canvas."""
    canv.saveState()
    canv.setFillColor(VERDE_OSCURO)
    canv.rect(0, 0, W, H, fill=1, stroke=0)

    canv.setFillColor(VERDE_MEDIO)
    p = canv.beginPath()
    p.moveTo(0, H * 0.35)
    p.lineTo(W * 0.6, H * 0.35)
    p.lineTo(W, H * 0.2)
    p.lineTo(W, 0)
    p.lineTo(0, 0)
    p.close()
    canv.drawPath(p, fill=1, stroke=0)

    canv.setFillColor(VERDE_CLARO)
    canv.rect(0, 0, W, 8*mm, fill=1, stroke=0)

    canv.setFillColor(BLANCO)
    canv.rect(1.5*cm, H - 2*cm, 5*cm, 3*mm, fill=1, stroke=0)

    canv.setFillColor(HexColor("#95D5B2"))
    canv.setFont("Helvetica", 9)
    canv.drawString(1.5*cm, H - 2.8*cm, "COMISION DE PARQUES Y BIODIVERSIDAD DE TAMAULIPAS")

    canv.setFillColor(BLANCO)
    canv.setFont("Helvetica-Bold", 28)
    canv.drawString(1.5*cm, H - 5.0*cm, "Sistema de")
    canv.drawString(1.5*cm, H - 6.2*cm, "Inventario")

    canv.setFillColor(VERDE_CLARO)
    canv.setFont("Helvetica-Bold", 28)
    canv.drawString(1.5*cm, H - 7.4*cm, "Zoo Tamatan")

    canv.setFillColor(BLANCO)
    canv.setFont("Helvetica-Bold", 20)
    canv.drawString(1.5*cm, H - 8.4*cm, "V3.0")

    canv.setFillColor(HexColor("#B7E4C7"))
    canv.setFont("Helvetica", 12)
    canv.drawString(1.5*cm, H - 9.6*cm, "Informe Tecnico de Evolucion y Estado del Proyecto")

    canv.setFillColor(VERDE_CLARO)
    canv.rect(1.5*cm, H - 10.4*cm, W - 3*cm, 1.5*mm, fill=1, stroke=0)

    metas = [
        ("FECHA DE CORTE", "31 de mayo de 2026"),
        ("VERSION", "3.0 (iteracion activa)"),
        ("SPRINT COMPLETADO", "~31 horas / 6 PRs mergeados"),
        ("URL PRODUCCION", "saulmeza-cpbt.github.io/inventario-zoologico"),
    ]
    y_start = H - 11.5*cm
    for label, value in metas:
        canv.setFillColor(HexColor("#95D5B2"))
        canv.setFont("Helvetica-Bold", 7)
        canv.drawString(1.5*cm, y_start, label)
        canv.setFillColor(BLANCO)
        canv.setFont("Helvetica", 9)
        canv.drawString(1.5*cm, y_start - 0.5*cm, value)
        y_start -= 1.3*cm

    metric_data = [
        ("20", "Commits"),
        ("6", "PRs mergeados"),
        ("5", "Modulos activos"),
        ("1,769", "Articulos catalogo"),
    ]
    box_w = (W - 3*cm) / 4
    box_h = 2.2*cm
    box_y = 3.5*cm
    for i, (val, lbl) in enumerate(metric_data):
        bx = 1.5*cm + i * box_w
        canv.setFillColor(HexColor("#2D6A4F"))
        canv.roundRect(bx + 2*mm, box_y, box_w - 4*mm, box_h, 4, fill=1, stroke=0)
        canv.setFillColor(VERDE_CLARO)
        canv.setFont("Helvetica-Bold", 18)
        canv.drawCentredString(bx + box_w/2, box_y + 1.2*cm, val)
        canv.setFillColor(HexColor("#95D5B2"))
        canv.setFont("Helvetica", 7)
        canv.drawCentredString(bx + box_w/2, box_y + 0.35*cm, lbl)

    canv.setFillColor(HexColor("#52B788"))
    canv.setFont("Helvetica-Oblique", 7)
    canv.drawCentredString(W/2, 1.5*cm, "Documento tecnico interno — Comision de Parques y Biodiversidad de Tamaulipas — 2026")
    canv.restoreState()


def on_first_page(canv, doc):
    W, H = A4
    draw_cover(canv, W, H)

def on_later_pages(canv, doc):
    canv.saveState()
    # Header bar
    canv.setFillColor(VERDE_OSCURO)
    canv.rect(0, A4[1] - 15*mm, A4[0], 15*mm, fill=1, stroke=0)
    canv.setFillColor(BLANCO)
    canv.setFont("Helvetica-Bold", 8)
    canv.drawString(1.5*cm, A4[1] - 9*mm, "INFORME TÉCNICO DE EVOLUCIÓN — ZOO TAMATÁN V3.0")
    canv.setFont("Helvetica", 8)
    canv.drawRightString(A4[0]-1.5*cm, A4[1] - 9*mm, "CPBT · Tamaulipas")
    canv.setFillColor(VERDE_CLARO)
    canv.rect(0, A4[1] - 16.5*mm, A4[0], 1.5*mm, fill=1, stroke=0)

    # Footer
    canv.setFillColor(VERDE_OSCURO)
    canv.rect(0, 0, A4[0], 16*mm, fill=1, stroke=0)
    canv.setFillColor(BLANCO)
    canv.setFont("Helvetica", 7.5)
    canv.drawString(1.5*cm, 6*mm, "Sistema de Inventario Zoo Tamatán V3.0 — CPBT Tamaulipas")
    canv.setFillColor(VERDE_CLARO)
    canv.rect(0, 16*mm, A4[0], 1.5*mm, fill=1, stroke=0)
    canv.restoreState()


# ──────────────────────────────────────────────
# PORTADA
# ──────────────────────────────────────────────
class CoverPage(Flowable):
    def __init__(self, width=A4[0], height=A4[1]):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        W, H = self.width, self.height

        # Fondo completo verde
        c.setFillColor(VERDE_OSCURO)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        # Banda diagonal decorativa
        c.setFillColor(VERDE_MEDIO)
        p = c.beginPath()
        p.moveTo(0, H * 0.35)
        p.lineTo(W * 0.6, H * 0.35)
        p.lineTo(W, H * 0.2)
        p.lineTo(W, 0)
        p.lineTo(0, 0)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

        # Acento inferior verde claro
        c.setFillColor(VERDE_CLARO)
        c.rect(0, 0, W, 8*mm, fill=1, stroke=0)

        # Línea blanca superior
        c.setFillColor(BLANCO)
        c.rect(1.5*cm, H - 2*cm, 5*cm, 3*mm, fill=1, stroke=0)

        # INSTITUCIÓN
        c.setFillColor(HexColor("#95D5B2"))
        c.setFont("Helvetica", 9)
        c.drawString(1.5*cm, H - 2.8*cm, "COMISIÓN DE PARQUES Y BIODIVERSIDAD DE TAMAULIPAS")

        # TÍTULO PRINCIPAL
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(1.5*cm, H - 5.0*cm, "Sistema de")
        c.drawString(1.5*cm, H - 6.2*cm, "Inventario")

        c.setFillColor(VERDE_CLARO)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(1.5*cm, H - 7.4*cm, "Zoo Tamatan")

        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(1.5*cm, H - 8.4*cm, "V3.0")

        # SUBTÍTULO
        c.setFillColor(HexColor("#B7E4C7"))
        c.setFont("Helvetica", 12)
        c.drawString(1.5*cm, H - 9.6*cm, "Informe Tecnico de Evolucion y Estado del Proyecto")

        # LÍNEA SEPARADORA
        c.setFillColor(VERDE_CLARO)
        c.rect(1.5*cm, H - 10.4*cm, W - 3*cm, 1.5*mm, fill=1, stroke=0)

        # METADATOS GRID
        metas = [
            ("FECHA DE CORTE", "31 de mayo de 2026"),
            ("VERSION", "3.0 (iteracion activa)"),
            ("SPRINT COMPLETADO", "~31 horas / 6 PRs mergeados"),
            ("URL PRODUCCION", "saulmeza-cpbt.github.io/inventario-zoologico"),
        ]
        y_start = H - 11.5*cm
        for label, value in metas:
            c.setFillColor(HexColor("#95D5B2"))
            c.setFont("Helvetica-Bold", 7)
            c.drawString(1.5*cm, y_start, label)
            c.setFillColor(BLANCO)
            c.setFont("Helvetica", 9)
            c.drawString(1.5*cm, y_start - 0.5*cm, value)
            y_start -= 1.3*cm

        # MÉTRICAS EN CELDAS
        metric_data = [
            ("20", "Commits"),
            ("6", "PRs mergeados"),
            ("5", "Modulos activos"),
            ("1,769", "Articulos catalogo"),
        ]
        box_w = (W - 3*cm) / 4
        box_h = 2.2*cm
        box_y = 3.5*cm
        for i, (val, lbl) in enumerate(metric_data):
            bx = 1.5*cm + i * box_w
            c.setFillColor(HexColor("#2D6A4F"))
            c.roundRect(bx + 2*mm, box_y, box_w - 4*mm, box_h, 4, fill=1, stroke=0)
            c.setFillColor(VERDE_CLARO)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(bx + box_w/2, box_y + 1.2*cm, val)
            c.setFillColor(HexColor("#95D5B2"))
            c.setFont("Helvetica", 7)
            c.drawCentredString(bx + box_w/2, box_y + 0.35*cm, lbl)

        # Nota de confidencialidad
        c.setFillColor(HexColor("#52B788"))
        c.setFont("Helvetica-Oblique", 7)
        c.drawCentredString(W/2, 1.5*cm, "Documento tecnico interno — Comision de Parques y Biodiversidad de Tamaulipas — 2026")


# ──────────────────────────────────────────────
# CONSTRUCCIÓN DEL DOCUMENTO
# ──────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2.2*cm,
        bottomMargin=2.2*cm,
        title="Informe Técnico de Evolución — Zoo Tamatán V3.0",
        author="Comisión de Parques y Biodiversidad de Tamaulipas",
        subject="Sistema de Inventario — Evolución y Estado del Proyecto",
    )

    story = []
    W = 16.5 * cm  # ancho útil

    # ── PORTADA ─────────────────────────────────
    # La portada se dibuja via on_first_page callback en el canvas completo
    story.append(PageBreak())

    # ── TABLA DE CONTENIDO ───────────────────────
    story.append(SectionDivider("", "TABLA DE CONTENIDO", width=W))
    story.append(Spacer(1, 10))

    toc_entries = [
        ("1", "Contexto y Objetivo Institucional", "3"),
        ("2", "Stack Tecnológico y Arquitectura", "3"),
        ("3", "Evolución Cronológica del Proyecto", "4"),
        ("",  "  3.1 Timeline Día 1 — Construcción Acelerada (30-may)", "4"),
        ("",  "  3.2 Timeline Día 2 — Consolidación y Despliegue (31-may)", "5"),
        ("4", "Módulos Implementados", "5"),
        ("",  "  4.1 Entradas | 4.2 Salidas | 4.3 Solicitudes", "5"),
        ("",  "  4.4 Levantamientos | 4.5 Bitácora | 4.6 Dashboard", "6"),
        ("5", "Gestión de Datos: Catálogos e Inventarios", "7"),
        ("",  "  5.1 Inventarios Excel (fuente primaria)", "7"),
        ("",  "  5.2 Catálogo Base Abril 2026 (PR #5)", "7"),
        ("",  "  5.3 Catálogo Maestro Enero–Abril (PR #6)", "8"),
        ("6", "Infraestructura de Despliegue", "9"),
        ("7", "Estructura de Archivos del Repositorio", "10"),
        ("8", "Bugs Conocidos y Deuda Técnica", "10"),
        ("9", "Roadmap V4.0 Aprobado", "11"),
        ("10","Métricas del Sprint", "12"),
    ]

    toc_rows = []
    for num, title, page in toc_entries:
        if num:
            label = Paragraph(f"{num}.&nbsp;&nbsp;{title}", STYLE_TOC_H1)
        else:
            label = Paragraph(title, STYLE_TOC_H2)
        pg = Paragraph(page, make_style("TOCP", "Normal",
            fontSize=9, fontName="Helvetica", alignment=TA_RIGHT,
            textColor=GRIS_MEDIO))
        toc_rows.append([label, pg])

    toc_table = Table(toc_rows, colWidths=[14.5*cm, 2*cm])
    toc_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("LINEBELOW", (0,0), (-1,-2), 0.3, GRIS_BORDE),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ── SECCIÓN 1: CONTEXTO ──────────────────────
    story.append(SectionDivider(1, "CONTEXTO Y OBJETIVO INSTITUCIONAL", width=W))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "El Zoo Tamatán, operado por la Comisión de Parques y Biodiversidad de Tamaulipas (CPBT), "
        "gestiona 5 áreas funcionales con necesidades heterogéneas de control de inventario físico: "
        "<b>Snack, Tienda de Recuerdos, Farmacia, Nutrición y Mantenimiento</b>. "
        "Previo al proyecto, el registro de entradas, salidas y existencias se realizaba de forma "
        "manual en hojas de cálculo Excel institucionales, sin trazabilidad de movimientos, "
        "sin flujo formal de aprobación y con alta probabilidad de inconsistencias entre áreas.",
        STYLE_BODY
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Objetivo central:</b>", STYLE_BODY_LEFT))
    story.append(Paragraph(
        "Digitalizar el ciclo completo de inventario —entradas, salidas, solicitudes de pedido y "
        "levantamientos físicos— con máximo rigor en trazabilidad del dato de origen y mínima "
        "fricción operativa para el personal de campo.",
        STYLE_BODY
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Restricciones de infraestructura:</b>", STYLE_BODY_LEFT))
    rest_data = [
        ["Restricción", "Impacto en diseño"],
        ["Sin servidor backend dedicado", "SPA con localStorage como persistencia"],
        ["Sin presupuesto para servicios cloud", "GitHub Pages (gratuito) como hosting"],
        ["Redes institucionales con acceso limitado", "Zero dependencias externas de runtime"],
        ["Necesidad de despliegue inmediato", "Monolito HTML + JS: deploy = un archivo"],
    ]
    rest_table = Table(rest_data, colWidths=[8*cm, 8.5*cm])
    rest_table.setStyle(base_table_style())
    story.append(rest_table)
    story.append(Spacer(1, 12))

    # ── SECCIÓN 2: STACK TECNOLÓGICO ────────────
    story.append(SectionDivider(2, "STACK TECNOLÓGICO Y ARQUITECTURA", width=W))
    story.append(Spacer(1, 8))

    stack_data = [
        ["Capa", "Tecnología", "Justificación técnica"],
        ["Frontend", "HTML5 + CSS3 Vanilla", "Sin dependencias, máxima portabilidad"],
        ["Lógica de negocio", "Vanilla JavaScript (ES6+)", "Sin frameworks, cero bundling, debug directo"],
        ["Persistencia", "localStorage del navegador", "Operación offline, sin backend, por dispositivo"],
        ["Hosting / CDN", "GitHub Pages (rama gh-pages)", "Gratuito, URL institucional pública, sin CI/CD"],
        ["Datos catálogo", "Archivos .js como módulos de datos", "Cargados como <script>, sin fetch/CORS"],
        ["Datos inventario", "JSON (873 KB) + JS (136 KB)", "Pre-procesados desde Excel, listos para consumo"],
        ["ETL / Procesamiento", "Python 3 + openpyxl + reportlab", "Scripts reproducibles fuera del repo HTML"],
    ]
    stack_table = Table(stack_data, colWidths=[4.0*cm, 4.5*cm, 8.0*cm])
    stack_table.setStyle(base_table_style())
    story.append(stack_table)
    story.append(Spacer(1, 10))

    story.append(SubSectionDivider("Arquitectura de la Aplicación", width=W))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "La aplicación es una <b>SPA monolítica de un único archivo HTML</b> "
        "(<i>zoo11AM_v3.0_DOCUMENTOS_ENTRADA.html</i>, 2,253 líneas, 94 KB). "
        "Toda la lógica de módulos reside en un objeto <b>APP</b> con submódulos namespaced:",
        STYLE_BODY
    ))

    arch_data = [
        ["Submódulo", "Responsabilidad"],
        ["APP.modEntradas", "Registro de entradas con 3 tipos de documento y autocomplete"],
        ["APP.modSalidas", "Registro de salidas y confronta teórica"],
        ["APP.modSolicitudes", "Solicitudes de pedido formato CPBT"],
        ["APP.modLevantamientos", "Levantamientos físicos en 2 pasos, precargan artículos por área"],
        ["APP.modBitacora", "Log de auditoría LIFO, 200 eventos, timestamps ISO 8601"],
        ["APP.dashboard", "Tarjetas resumen y tablas de inventario por área con buscador"],
    ]
    arch_table = Table(arch_data, colWidths=[5.0*cm, 11.5*cm])
    arch_table.setStyle(base_table_style())
    story.append(arch_table)

    story.append(Spacer(1, 8))
    story.append(SubSectionDivider("Fuentes de Verdad de Datos", width=W))
    story.append(Spacer(1, 6))
    truth_data = [
        ["Variable global", "Archivo fuente", "Peso", "Descripción"],
        ["window.CATALOGO_INVENTARIO", "inventarios/catalogo_articulos.js", "136 KB",
         "Catálogo base Abril 2026 — {c,n,u,p,e} por artículo"],
        ["(JSON inline)", "inventarios/inventario_abril_2026.json", "873 KB",
         "Datos completos: entradas, salidas, ajustes, físico, diferencias"],
        ["window.CATALOGO_ARTICULOS_POR_AREA", "data/catalogos/catalogo_articulos_por_area.js", "155 KB",
         "Catálogo maestro enero–abril consolidado por área"],
    ]
    truth_table = Table(truth_data, colWidths=[5.0*cm, 5.5*cm, 1.5*cm, 4.5*cm])
    truth_table.setStyle(base_table_style())
    story.append(truth_table)
    story.append(PageBreak())

    # ── SECCIÓN 3: EVOLUCIÓN CRONOLÓGICA ────────
    story.append(SectionDivider(3, "EVOLUCIÓN CRONOLÓGICA DEL PROYECTO", width=W))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "El proyecto fue construido en un sprint continuo de aproximadamente <b>31 horas</b> "
        "distribuidas en dos días (30 y 31 de mayo de 2026), con una cadencia de 20 commits "
        "funcionales y 6 Pull Requests completados bajo squash-merge.",
        STYLE_BODY
    ))
    story.append(Spacer(1, 10))

    story.append(SubSectionDivider("3.1  Día 1 — Construcción Acelerada (30 de mayo de 2026)", width=W))
    story.append(Spacer(1, 6))

    day1_events = [
        ("12:00", "59d714b", "Commit inicial: SPA V3.0 completa con documentación base", False),
        ("12:53", "90d926e", "Fix Paso 3 de Entradas + trazabilidad de área e inventario", False),
        ("16:44", "6c583fb", "Fix doc: línea duplicada y typo en resumen ejecutivo", False),
        ("16:47", "d947d23", "UX: cierre de dropdown autocomplete al hacer clic externo", False),
        ("16:58", "5cd101b", "PR #2 MERGEADO — feat/cerrar-sugerencias-click-fuera", True),
        ("17:22", "0c2126e", "Campo Motivo obligatorio + Bitácora institucional visible", False),
        ("17:43", "81c3acf", "Folio físico obligatorio, áreas operativas, autocomplete por área", False),
        ("17:59", "e38a700", "3 tipos de entrada, folio único, módulos Solicitudes y Levantamientos", False),
        ("18:06", "e21eb61", "Refactor Levantamientos: quitar Exist. Teórica, precargar artículos", False),
        ("18:23", "2be4fba", "Integrar catálogo oficial Abril 2026 al autocomplete y levantamientos", False),
        ("18:27", "0ecfae6", "Dashboard: inventarios 5 áreas con detalle y trazabilidad de origen", False),
    ]
    for ev in day1_events:
        story.append(TimelineRow(*ev, width=W))

    story.append(Spacer(1, 10))
    story.append(SubSectionDivider("3.2  Día 2 — Consolidación, Datos Reales y Despliegue (31 de mayo de 2026)", width=W))
    story.append(Spacer(1, 6))

    day2_events = [
        ("07:17", "81f703d", "Redirect index.html meta-refresh para GitHub Pages", False),
        ("10:40", "e2d2bc5", "Config preview (.claude/launch.json), script generar_reporte.py, PDF técnico v1", False),
        ("10:42", "31ec424", "PR #3 MERGEADO — Bitácora, Solicitudes, Levantamientos, Dashboard, catálogo Abril", True),
        ("14:08", "348e40f", "PR #4 MERGEADO — Módulo Salidas + confronta teórica en Levantamientos", True),
        ("17:15", "f6a7d46", "PR #5 MERGEADO — Catálogo base Abril regenerado con precio y existencia", True),
        ("18:52", "3f90a34", "PR #6 MERGEADO — Catálogo maestro enero–abril por área (squash)", True),
        ("19:10", "d57b658", "Deploy gh-pages: sincronización con main (PR #5 + #6), corrige 404 en prod", False),
    ]
    for ev in day2_events:
        story.append(TimelineRow(*ev, width=W))

    story.append(Spacer(1, 10))

    # Estadística de velocidad
    vel_data = [
        ["Duración sprint", "Commits totales", "PRs completados", "Módulos entregados"],
        ["~31 horas", "20 commits", "6 PRs (squash)", "5 módulos operativos"],
    ]
    vel_table = Table(vel_data, colWidths=[W/4]*4)
    vel_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), VERDE_CLARO),
        ("TEXTCOLOR",     (0,0), (-1,0), VERDE_OSCURO),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 8),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND",    (0,1), (-1,1), VERDE_OSCURO),
        ("TEXTCOLOR",     (0,1), (-1,1), BLANCO),
        ("FONTNAME",      (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,1), (-1,1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOX",           (0,0), (-1,-1), 1, VERDE_MEDIO),
        ("GRID",          (0,0), (-1,-1), 0.4, VERDE_CLARO),
    ]))
    story.append(vel_table)
    story.append(PageBreak())

    # ── SECCIÓN 4: MÓDULOS ──────────────────────
    story.append(SectionDivider(4, "MÓDULOS IMPLEMENTADOS", width=W))
    story.append(Spacer(1, 8))

    # 4.1 Entradas
    story.append(SubSectionDivider("4.1  Módulo ENTRADAS (pestaña Entradas)", width=W))
    story.append(Spacer(1, 6))

    entradas_data = [
        ["Atributo", "Especificación técnica"],
        ["Estado", "PRODUCCIÓN"],
        ["Tipos de documento", "1) Factura Proveedor  2) Factura Caja Chica  3) Acta de Entrega con N. Contrato"],
        ["Campo folioDocumento", "Obligatorio, único por transacción, validado antes de confirmar"],
        ["Autocomplete", "Filtrado por área seleccionada; fuente: CATALOGO_INVENTARIO + CATALOGO_ARTICULOS_POR_AREA"],
        ["Campo Motivo", "Obligatorio antes de confirmar cada artículo"],
        ["Trazabilidad", "Cada entrada dispara un evento en Bitácora con timestamp ISO 8601"],
        ["Persistencia", "localStorage (clave por sesión de área)"],
    ]
    ent_table = Table(entradas_data, colWidths=[4.5*cm, 12*cm])
    ent_table.setStyle(base_table_style())
    story.append(ent_table)
    story.append(Spacer(1, 8))

    # 4.2 Salidas
    story.append(SubSectionDivider("4.2  Módulo SALIDAS (entregado en PR #4)", width=W))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Estado:</b> Producción. <b>Flujo:</b> Selección de área → filtrado de catálogo → "
        "captura de cantidad y motivo → confirmación. Cada salida actualiza la confronta teórica "
        "en el módulo de Levantamientos para que la diferencia física/teórica sea siempre calculada "
        "con datos actuales.", STYLE_BODY
    ))
    story.append(Spacer(1, 8))

    # 4.3 Solicitudes
    story.append(SubSectionDivider("4.3  Módulo SOLICITUDES DE PEDIDO (pestaña Solicitudes)", width=W))
    story.append(Spacer(1, 6))
    sol_data = [
        ["Campo", "Tipo", "Obligatorio"],
        ["Folio", "Texto libre", "Sí"],
        ["Día / Mes / Año", "Numérico / Select / Numérico", "Sí"],
        ["Área requirente", "Select (5 áreas)", "Sí"],
        ["Proyecto", "Texto libre", "No"],
        ["Partida presupuestal", "Texto libre", "No"],
        ["Artículos solicitados", "Tabla dinámica", "Sí (mínimo 1)"],
        ["Justificación", "Textarea colapsable", "No"],
        ["Estado", "Select inline (Pendiente/Aprobada/Rechazada)", "—"],
    ]
    sol_table = Table(sol_data, colWidths=[5*cm, 7*cm, 4.5*cm])
    sol_table.setStyle(base_table_style())
    story.append(sol_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "localStorage key: <font name='Courier' size='8'>zoo_tamatan_solicitudes_v1</font>",
        STYLE_BODY_LEFT
    ))
    story.append(Spacer(1, 8))

    # 4.4 Levantamientos
    story.append(SubSectionDivider("4.4  Módulo LEVANTAMIENTOS FÍSICOS (pestaña Levantamientos)", width=W))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Flujo en 2 pasos:</b>", STYLE_BODY_LEFT
    ))
    lev_data = [
        ["Paso", "Acción del operador", "Acción del sistema"],
        ["Paso 1", "Selecciona área y semana de levantamiento", "Precarga lista de artículos de esa área desde catálogo"],
        ["Paso 2", "Captura existencia física por artículo (inline)", "Calcula y muestra diferencia: exist_fisica - exist_teorica"],
    ]
    lev_table = Table(lev_data, colWidths=[1.8*cm, 7.5*cm, 7.2*cm])
    lev_table.setStyle(base_table_style())
    story.append(lev_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "localStorage key: <font name='Courier' size='8'>zoo_tamatan_levantamientos_v1</font>. "
        "La existencia teórica la calcula el sistema automáticamente; el operador solo captura lo físico.",
        STYLE_BODY
    ))
    story.append(Spacer(1, 8))

    # 4.5 Bitácora
    story.append(SubSectionDivider("4.5  Módulo BITÁCORA (pestaña Bitácora)", width=W))
    story.append(Spacer(1, 6))
    bit_data = [
        ["Característica", "Especificación"],
        ["Estructura", "LIFO (Last In, First Out), capacidad 200 eventos"],
        ["Campos por evento", "nivel + entidad + acción + timestamp ISO 8601"],
        ["Eventos auditados", "TODAS las acciones en Entradas, Salidas, Solicitudes, Levantamientos"],
        ["localStorage key", "zoo_tamatan_bitacora_v3"],
    ]
    bit_table = Table(bit_data, colWidths=[4.5*cm, 12*cm])
    bit_table.setStyle(base_table_style())
    story.append(bit_table)
    story.append(Spacer(1, 8))

    # 4.6 Dashboard
    story.append(SubSectionDivider("4.6  DASHBOARD", width=W))
    story.append(Spacer(1, 6))
    dash_data = [
        ["Área", "Artículos catálogo base (Abril)", "Código prefijo"],
        ["Snack", "162", "S-"],
        ["Tienda de Recuerdos", "85", "T-"],
        ["Farmacia", "311", "F-"],
        ["Nutrición", "108", "2220"],
        ["Mantenimiento", "1,103", "M-"],
        ["TOTAL", "1,769", "—"],
    ]
    dash_table = Table(dash_data, colWidths=[6*cm, 6*cm, 4.5*cm])
    dash_table.setStyle(base_table_style())
    # Bold last row
    dash_table.setStyle(TableStyle([
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), VERDE_SUAVE),
    ]))
    story.append(dash_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Etiqueta de origen en UI: <i>\"Base: Inventario oficial Abril 2026\"</i>. "
        "Cada tarjeta de área es clicable y despliega tabla completa con buscador inline.",
        STYLE_BODY
    ))
    story.append(PageBreak())

    # ── SECCIÓN 5: GESTIÓN DE DATOS ─────────────
    story.append(SectionDivider(5, "GESTIÓN DE DATOS: CATÁLOGOS E INVENTARIOS", width=W))
    story.append(Spacer(1, 8))

    story.append(SubSectionDivider("5.1  Inventarios Excel — Fuente Primaria Institucional", width=W))
    story.append(Spacer(1, 6))

    inv_data = [
        ["Archivo Excel", "Área", "Tamaño"],
        ["04.ABRIL.2026.INVENTARIO.FARMACIA.FINAL.xlsx", "Farmacia", "490 KB"],
        ["04.ABRIL.2026.INVENTARIO.NUTRICION.FINAL+CIE.xlsx", "Nutrición", "728 KB"],
        ["04.ABRIL.2026.INVENTARIO.SNACK.FINAL.xlsx", "Snack", "293 KB"],
        ["04.ABRIL.2026.INVENTARIO.TIENDARECUERDOS.FINAL.xlsx", "Tienda", "171 KB"],
        ["04.ABRIL.2026.MANTENIMIENTO.FINAL.xlsx", "Mantenimiento", "1.3 MB"],
    ]
    inv_table = Table(inv_data, colWidths=[9.5*cm, 3.5*cm, 3.5*cm])
    inv_table.setStyle(base_table_style())
    story.append(inv_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Heurística de parsing implementada en Python/openpyxl:</b>", STYLE_BODY_LEFT))
    parse_data = [
        ["Regla de parsing", "Detalle"],
        ["Hoja objetivo", "INV. FINAL (nombre exacto en cada workbook)"],
        ["Detección de encabezado", "Buscar fila con columna 'CODIGO' + ('DESCRIPCION' o 'ARTICULO')"],
        ["Fin de tabla de datos", "Primera fila con celda 'TOTAL' en columna de cantidades"],
        ["Filas ignoradas post-TOTAL", "Firmas institucionales: ELABORÓ / C.P. / JEFE DE DEPARTAMENTO"],
    ]
    parse_table = Table(parse_data, colWidths=[5.5*cm, 11*cm])
    parse_table.setStyle(base_table_style())
    story.append(parse_table)
    story.append(Spacer(1, 10))

    story.append(SubSectionDivider("5.2  Catálogo Base Abril 2026 (PR #5)", width=W))
    story.append(Spacer(1, 6))

    cat_data = [
        ["Atributo", "Valor"],
        ["Archivo", "inventarios/catalogo_articulos.js"],
        ["Variable global", "window.CATALOGO_INVENTARIO"],
        ["Estructura interna", "Objeto por área → array de {c, n, u, p, e} (código, nombre, unidad, precio, existencia)"],
        ["Total artículos", "1,769 artículos únicos (suma de todas las áreas)"],
        ["Peso", "136 KB / 4 líneas JS"],
    ]
    cat_table = Table(cat_data, colWidths=[4.5*cm, 12*cm])
    cat_table.setStyle(base_table_style())
    story.append(cat_table)
    story.append(Spacer(1, 6))

    # Bug box
    bug_rows = [
        [Paragraph("<b>BUG-01 (Alta severidad) — Detectado post-PR #5, pendiente de fix/</b>", STYLE_ERR)],
        [Paragraph(
            "La clave interna del catálogo usa <font name='Courier'>'Nutricion'</font> (sin acento) "
            "mientras el &lt;select&gt;, el catálogo maestro y AREAS_INV usan "
            "<font name='Courier'>'Nutricion'</font> con tilde "
            "→ CATALOGO_INVENTARIO['Nutricion'] retorna undefined. "
            "Efecto: rompe autocomplete de Nutrición Y la valuación en Dashboard (muestra $0). "
            "Fix: 1 carácter en la clave del objeto. Separado en rama fix/ propia por afectar catálogo base + Dashboard.",
            STYLE_ERR
        )],
    ]
    bug_table = Table(bug_rows, colWidths=[W])
    bug_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), ROJO_ERR),
        ("BOX",          (0,0), (-1,-1), 1.5, ROJO_BRD),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0), (-1,-1), 7),
    ]))
    story.append(bug_table)
    story.append(Spacer(1, 10))

    story.append(SubSectionDivider("5.3  Catálogo Maestro Enero–Abril 2026 (PR #6)", width=W))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Objetivo: consolidar artículos que aparecen en <b>cualquier mes enero–abril</b> para ampliar "
        "la cobertura del autocomplete más allá del corte de Abril. Fuente: 20 archivos Excel "
        "institucionales (5 áreas × 4 meses), procesados con script Python reproducible "
        "(<i>generar_catalogo_maestro.py</i>, 13 KB).",
        STYLE_BODY
    ))
    story.append(Spacer(1, 6))

    maestro_data = [
        ["Área", "Artículos únicos (maestro)", "Base Abril", "Delta", "Prefijo"],
        ["Snack", "163", "162", "+1", "S-"],
        ["Tienda", "85", "85", "0", "T-"],
        ["Farmacia", "298", "311", "-13 *", "F-"],
        ["Nutrición", "108", "108", "0", "2220"],
        ["Mantenimiento", "1,106", "1,103", "+3", "M-"],
        ["TOTAL", "1,760", "1,769", "—", "—"],
    ]
    m_table = Table(maestro_data, colWidths=[4*cm, 4.5*cm, 3*cm, 2.5*cm, 2.5*cm])
    m_table.setStyle(base_table_style())
    m_table.setStyle(TableStyle([
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), VERDE_SUAVE),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "* Farmacia baja porque el maestro excluye artículos sin código válido que el base sí incluía.",
        STYLE_CAPTION
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Reglas de consolidación aplicadas:</b>", STYLE_BODY_LEFT))
    rules_data = [
        ["Regla", "Comportamiento", "Acción de reporte"],
        ["Nombre canónico", "Se usa el nombre de Abril (mes más reciente)", "—"],
        ["Mismo nombre / distinto código", "No se duplica el artículo", "Reportado en reporte_inconsistencias.json"],
        ["Nombre sin código", "Se excluye del catálogo final", "Reportado en reporte_inconsistencias.json"],
        ["Código fuera de prefijo esperado", "Se conserva en el catálogo", "Reportado en reporte_inconsistencias.json"],
    ]
    rules_table = Table(rules_data, colWidths=[4.5*cm, 6.5*cm, 5.5*cm])
    rules_table.setStyle(base_table_style())
    story.append(rules_table)
    story.append(Spacer(1, 8))

    # Pitfall técnico
    pit_rows = [
        [Paragraph("<b>PITFALL TÉCNICO CRÍTICO descubierto durante PR #6</b>", STYLE_WARN)],
        [Paragraph(
            "El uso de openpyxl en modo <font name='Courier'>read_only=True</font> con acceso aleatorio "
            "<font name='Courier'>ws.cell(row, col)</font> produce complejidad <b>O(n²)</b>: cada acceso "
            "itera el stream desde el inicio. En Excel de Mantenimiento (1.3 MB, >1,000 filas) el proceso "
            "se congela consumiendo CPU al 100%.<br/>"
            "<b>Solución adoptada:</b> usar <font name='Courier'>read_only=False</font> para archivos "
            "de tamaño manejable, o siempre iterar con <font name='Courier'>iter_rows()</font> "
            "para garantizar O(n).",
            STYLE_WARN
        )],
    ]
    pit_table = Table(pit_rows, colWidths=[W])
    pit_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), AMARILLO_WARN),
        ("BOX",          (0,0), (-1,-1), 1.5, AMARILLO_BRD),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0), (-1,-1), 7),
    ]))
    story.append(pit_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Archivos entregados en PR #6 (data/catalogos/):</b>", STYLE_BODY_LEFT))
    pr6_data = [
        ["Archivo", "Peso", "Descripción"],
        ["catalogo_articulos_por_area.js", "155 KB / 7,054 líneas", "Módulo JS consumible por la SPA"],
        ["catalogo_articulos_por_area.json", "155 KB", "Copia JSON para herramientas externas"],
        ["reporte_inconsistencias.json", "27 KB", "Auditoría de calidad: nombres dup., códigos fuera de prefijo"],
        ["generar_catalogo_maestro.py", "13 KB", "ETL Python reproducible — única fuente de verdad del catálogo"],
    ]
    pr6_table = Table(pr6_data, colWidths=[5.5*cm, 3.5*cm, 7.5*cm])
    pr6_table.setStyle(base_table_style())
    story.append(pr6_table)
    story.append(PageBreak())

    # ── SECCIÓN 6: INFRAESTRUCTURA ──────────────
    story.append(SectionDivider(6, "INFRAESTRUCTURA DE DESPLIEGUE", width=W))
    story.append(Spacer(1, 8))

    story.append(SubSectionDivider("6.1  GitHub Pages — Hosting de Producción", width=W))
    story.append(Spacer(1, 6))

    gh_data = [
        ["Parámetro", "Valor"],
        ["Organización GitHub", "saulmeza-cpbt"],
        ["Repositorio", "inventario-zoologico"],
        ["URL pública de producción", "https://saulmeza-cpbt.github.io/inventario-zoologico/"],
        ["Rama fuente de Pages", "gh-pages (modo legacy desde rama, sin GitHub Actions)"],
        ["Rama de desarrollo activo", "main"],
        ["Estrategia de deploy", "Sincronización manual main → gh-pages vía git checkout"],
    ]
    gh_table = Table(gh_data, colWidths=[5*cm, 11.5*cm])
    gh_table.setStyle(base_table_style())
    story.append(gh_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Proceso de deploy documentado y verificado:</b>", STYLE_BODY_LEFT))
    deploy_steps = [
        ["Paso", "Comando", "Notas"],
        ["1", "git checkout -b gh-pages origin/gh-pages", "Activa rama de producción"],
        ["2", "git checkout main -- .", "Sobrepone árbol de main sobre gh-pages"],
        ["3", "(index.html se preserva)", "El redirect index.html NO existe en main → se conserva automáticamente"],
        ["4", "git commit && git push", "Publica los cambios en GitHub Pages"],
        ["5", "gh api repos/.../pages/builds/latest --jq .status", "Esperar respuesta 'built'"],
        ["6", "curl -I [URL] → HTTP 200", "Confirmar que el sitio está activo"],
    ]
    dep_table = Table(deploy_steps, colWidths=[1.2*cm, 7*cm, 8.3*cm])
    dep_table.setStyle(base_table_style())
    story.append(dep_table)
    story.append(Spacer(1, 8))

    # Bug deploy resuelto
    depl_rows = [
        [Paragraph("<b>Bug de despliegue resuelto (commit d57b658, 31-may-2026 19:10 CDT)</b>", STYLE_INFO)],
        [Paragraph(
            "El directorio <font name='Courier'>inventarios/</font> no estaba incluido en gh-pages, "
            "causando que el catálogo base (catalogo_articulos.js) diera HTTP 404 en producción "
            "mientras funcionaba localmente. El deploy d57b658 lo corrigió al sincronizar main completo, "
            "incluyendo <font name='Courier'>inventarios/</font> y <font name='Courier'>data/catalogos/</font>. "
            "Sitio verificado operativo en vivo post-deploy.",
            STYLE_INFO
        )],
    ]
    depl_table = Table(depl_rows, colWidths=[W])
    depl_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), AZUL_INFO),
        ("BOX",          (0,0), (-1,-1), 1.5, AZUL_BRD),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0), (-1,-1), 7),
    ]))
    story.append(depl_table)
    story.append(Spacer(1, 10))

    story.append(SubSectionDivider("6.2  Entorno Local de Desarrollo", width=W))
    story.append(Spacer(1, 6))
    local_data = [
        ["Componente", "Configuración"],
        ["Servidor de preview", "python -m http.server (Puerto 3000)"],
        ["Archivo de config", ".claude/launch.json (integrado con Claude Code)"],
        ["gh CLI", "/c/Program Files/GitHub CLI/gh.exe (fuera de PATH — invocar con ruta completa)"],
    ]
    local_table = Table(local_data, colWidths=[4.5*cm, 12*cm])
    local_table.setStyle(base_table_style())
    story.append(local_table)
    story.append(PageBreak())

    # ── SECCIÓN 7: ESTRUCTURA DE ARCHIVOS ───────
    story.append(SectionDivider(7, "ESTRUCTURA DE ARCHIVOS DEL REPOSITORIO", width=W))
    story.append(Spacer(1, 8))

    tree_data = [
        ["Ruta", "Peso", "Descripción"],
        ["zoo11AM_v3.0_DOCUMENTOS_ENTRADA.html", "94 KB", "SPA principal — 2,253 líneas, todo el sistema"],
        ["inventarios/catalogo_articulos.js", "136 KB", "Catálogo base Abril 2026 (CATALOGO_INVENTARIO)"],
        ["inventarios/inventario_abril_2026.json", "873 KB", "Datos completos Abril con entradas/salidas/ajustes"],
        ["inventarios/*.xlsx (5 archivos)", "~3 MB", "Excel institucionales originales de cierre Abril 2026"],
        ["data/catalogos/catalogo_articulos_por_area.js", "155 KB", "Catálogo maestro ene–abr (7,054 líneas)"],
        ["data/catalogos/catalogo_articulos_por_area.json", "155 KB", "Copia JSON del maestro"],
        ["data/catalogos/reporte_inconsistencias.json", "27 KB", "Auditoría de calidad del catálogo maestro"],
        ["data/catalogos/generar_catalogo_maestro.py", "13 KB", "ETL reproducible — fuente del maestro"],
        ["generar_reporte.py", "25 KB", "Script Python/reportlab para generar PDFs técnicos"],
        ["RESUMEN_EJECUTIVO_V3.0.md", "9.8 KB", "Resumen ejecutivo para stakeholders"],
        ["ESPECIFICACION_DOCUMENTOS_ENTRADA_V3.md", "17 KB", "Especificación técnica funcional"],
        ["GUIA_USO_DOCUMENTOS_ENTRADA_V3.md", "17 KB", "Manual de usuario"],
        ["VALIDACION_CATALOGO.md", "8.8 KB", "Reporte de validación del catálogo base Abril"],
        [".claude/launch.json", "215 B", "Config servidor preview para Claude Code"],
    ]
    tree_table = Table(tree_data, colWidths=[7*cm, 1.8*cm, 7.7*cm])
    tree_table.setStyle(base_table_style())
    story.append(tree_table)
    story.append(PageBreak())

    # ── SECCIÓN 8: BUGS Y DEUDA ─────────────────
    story.append(SectionDivider(8, "BUGS CONOCIDOS Y DEUDA TÉCNICA", width=W))
    story.append(Spacer(1, 8))

    bugs_data = [
        ["ID", "Severidad", "Descripción", "Estado", "PR"],
        ["BUG-01", "ALTA",
         "Clave 'Nutricion' (sin acento) en catálogo base → CATALOGO_INVENTARIO['Nutricion'] = undefined. "
         "Rompe autocomplete de Nutrición y valuación en Dashboard (muestra $0). "
         "Fix: 1 carácter en clave del objeto.",
         "Pendiente", "fix/ (rama separada)"],
        ["DEBT-01", "MEDIA",
         "SPA monolítica de 2,253 líneas — todo CSS, HTML y JS en un solo archivo. "
         "Dificulta mantenimiento y colaboración a largo plazo.",
         "Roadmap", "PR #12"],
        ["DEBT-02", "BAJA",
         "Sin autenticación ni roles — cualquier usuario puede modificar cualquier área. "
         "Riesgo de modificaciones no autorizadas en producción.",
         "Roadmap", "PR #13"],
        ["DEBT-03", "BAJA",
         "Persistencia en localStorage: sin respaldo automático, limitado por dispositivo/navegador. "
         "Pérdida de datos si se limpia el almacenamiento.",
         "Roadmap", "PR #11"],
    ]
    bugs_table = Table(bugs_data, colWidths=[1.8*cm, 2*cm, 7.5*cm, 2.2*cm, 3*cm])
    bugs_table.setStyle(base_table_style())
    # Colorear severidades
    bugs_table.setStyle(TableStyle([
        ("BACKGROUND", (1, 1), (1, 1), ROJO_ERR),
        ("TEXTCOLOR",  (1, 1), (1, 1), HexColor("#721C24")),
        ("BACKGROUND", (1, 2), (1, 2), AMARILLO_WARN),
        ("TEXTCOLOR",  (1, 2), (1, 2), HexColor("#856404")),
        ("BACKGROUND", (1, 3), (1, 3), GRIS_CLARO),
        ("BACKGROUND", (1, 4), (1, 4), GRIS_CLARO),
    ]))
    story.append(bugs_table)
    story.append(PageBreak())

    # ── SECCIÓN 9: ROADMAP ──────────────────────
    story.append(SectionDivider(9, "ROADMAP V4.0 APROBADO", width=W))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "Secuencia de PRs pequeños bajo squash-merge. Principio rector: "
        "<b>un objetivo = una rama = un PR</b>. El usuario revisa cada PR en GitHub y confirma el merge.",
        STYLE_BODY
    ))
    story.append(Spacer(1, 8))

    road_data = [
        ["PR", "Rama", "Objetivo", "Estado"],
        ["#1", "—", "Documentación inicial del proyecto", "Completado"],
        ["#2", "feat/cerrar-sugerencias", "UX: cerrar dropdown al clic externo", "Completado"],
        ["#3", "feat/bitacora-institucional-y-motivo",
         "Bitácora, solicitudes, levantamientos, dashboard, catálogo Abril", "Completado"],
        ["#4", "—", "Módulo Salidas + confronta teórica en Levantamientos", "Completado"],
        ["#5", "—", "Catálogo base Abril con precio y existencia (regenerado)", "Completado"],
        ["#6", "feat/catalogo-maestro-enero-abril",
         "Catálogo maestro enero–abril consolidado por área", "Completado"],
        ["#7", "feat/autocomplete-catalogo-maestro",
         "Autocomplete con catálogo maestro (amplía Nutrición y Mantenimiento)", "En diseño"],
        ["#8", "feat/stock-base-abril",
         "Módulo Stock: corte base Abril, stock = exist_final + entradas - salidas", "Pendiente"],
        ["#9", "feat/validar-salidas-stock",
         "Validar salidas vs stock disponible (prevenir negativos)", "Pendiente"],
        ["#10", "feat/reportes",
         "Reportes por mes/área exportables (CSV primero)", "Pendiente"],
        ["#11", "feat/respaldo-json",
         "Respaldo JSON exportable desde localStorage (sin pérdida de datos)", "Pendiente"],
        ["#12", "feat/modularizar",
         "Modularizar HTML/CSS/JS — separar en archivos independientes", "Pendiente"],
        ["#13", "feat/roles-locales",
         "Roles locales por área (sin backend)", "Pendiente"],
        ["V4.0", "—", "Backend real — autenticación, base de datos, API REST", "Futuro"],
    ]
    road_table = Table(road_data, colWidths=[1.5*cm, 4.5*cm, 7.5*cm, 3*cm])
    road_table.setStyle(base_table_style())
    # Colorear estados
    status_colors = {
        "Completado":  (HexColor("#D4EDDA"), HexColor("#155724")),
        "En diseño":   (AZUL_INFO, HexColor("#0C5460")),
        "Pendiente":   (GRIS_CLARO, GRIS_MEDIO),
        "Futuro":      (AMARILLO_WARN, HexColor("#856404")),
    }
    for row_i, row in enumerate(road_data[1:], 1):
        estado = row[3]
        if estado in status_colors:
            bg, fg = status_colors[estado]
            road_table.setStyle(TableStyle([
                ("BACKGROUND", (3, row_i), (3, row_i), bg),
                ("TEXTCOLOR",  (3, row_i), (3, row_i), fg),
                ("FONTNAME",   (3, row_i), (3, row_i), "Helvetica-Bold"),
            ]))
    story.append(road_table)
    story.append(PageBreak())

    # ── SECCIÓN 10: MÉTRICAS ────────────────────
    story.append(SectionDivider(10, "MÉTRICAS DEL SPRINT", width=W))
    story.append(Spacer(1, 10))

    metrics_grid = MetricsGrid([
        ("20", "Commits funcionales"),
        ("6", "PRs mergeados"),
        ("~31h", "Duración del sprint"),
        ("5", "Módulos operativos"),
        ("1,769", "Artículos catálogo base"),
        ("1,760", "Artículos catálogo maestro"),
        ("873 KB", "JSON inventario procesado"),
        ("2,253", "Líneas de código (HTML)"),
    ], width=W)
    story.append(metrics_grid)
    story.append(Spacer(1, 16))

    full_metrics = [
        ["Métrica", "Valor detallado"],
        ["Duración total del sprint", "~31 horas (2026-05-30 12:00 CDT → 2026-05-31 19:10 CDT)"],
        ["Commits realizados", "20 commits funcionales (incluyendo fixes, features y deploys)"],
        ["Pull Requests completados", "6 PRs bajo estrategia squash-merge"],
        ["Líneas de código (SPA HTML)", "2,253 líneas (94 KB)"],
        ["Artículos en catálogo base", "1,769 artículos únicos en 5 áreas (Abril 2026)"],
        ["Artículos en catálogo maestro", "1,760 artículos únicos consolidados (Enero–Abril 2026)"],
        ["Datos de inventario procesados", "873 KB JSON desde 5 archivos Excel institucionales (~3 MB)"],
        ["Módulos operativos en producción", "5: Entradas, Salidas, Solicitudes, Levantamientos, Bitácora"],
        ["Áreas operativas cubiertas", "5: Snack, Tienda, Farmacia, Nutrición, Mantenimiento"],
        ["Bugs abiertos (conocidos)", "1 Alta severidad (BUG-01) + 3 ítems de deuda técnica"],
        ["URL de producción verificada", "https://saulmeza-cpbt.github.io/inventario-zoologico/"],
        ["Rama activa", "main (working tree limpio post-PR #6)"],
        ["Próximo PR en diseño", "PR #7 — autocomplete con catálogo maestro"],
        ["Peso total del repositorio", "~4.5 MB (dominado por Excel de fuente y JSON de inventario)"],
    ]
    full_table = Table(full_metrics, colWidths=[6.5*cm, 10*cm])
    full_table.setStyle(base_table_style())
    story.append(full_table)
    story.append(Spacer(1, 16))

    # Nota final
    final_rows = [
        [Paragraph(
            "<b>Estado del sistema al 31 de mayo de 2026:</b> "
            "El sistema se encuentra en producción activa con 6 PRs mergeados en main. "
            "GitHub Pages verificado y operativo. Working tree limpio. "
            "El siguiente hito es PR #7 (autocomplete con catálogo maestro) que amplía "
            "la cobertura de Nutrición (108 artículos) y Mantenimiento (+4 del maestro). "
            "El roadmap formal contempla 7 PRs adicionales antes de V4.0 con backend real.",
            STYLE_INFO
        )],
    ]
    final_table = Table(final_rows, colWidths=[W])
    final_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), VERDE_SUAVE),
        ("BOX",          (0,0), (-1,-1), 2, VERDE_MEDIO),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
    ]))
    story.append(final_table)

    # ── CONSTRUIR ────────────────────────────────
    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
    print(f"PDF generado: {OUTPUT_PATH}")
    size_kb = os.path.getsize(OUTPUT_PATH) // 1024
    print(f"Tamaño: {size_kb} KB")


if __name__ == "__main__":
    build_pdf()
