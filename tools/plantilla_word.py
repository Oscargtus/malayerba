"""Genera la plantilla Word para que el alumnado proponga artículos a Plantopia."""
import copy
import sys
from io import BytesIO

from docx import Document
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

LOGO, SALIDA = sys.argv[1], sys.argv[2]

VERDE = RGBColor(0x27, 0xAE, 0x60)
OSCURO = RGBColor(0x2A, 0x2D, 0x34)
GRIS = RGBColor(0x6B, 0x70, 0x78)
FONDO_CAMPO = "F2F8F4"
BORDE_CAMPO = "27AE60"
FUENTE = "Arial"
ANCHO = Cm(17)  # A4 con márgenes de 2 cm

doc = Document()

# ---------- página y estilos ----------
for s in doc.sections:
    s.page_height, s.page_width = Cm(29.7), Cm(21)
    s.top_margin = s.bottom_margin = Cm(1.8)
    s.left_margin = s.right_margin = Cm(2)
    s.header_distance = Cm(0.9)

st = doc.styles["Normal"]
st.font.name = FUENTE
st.font.size = Pt(10.5)
st.font.color.rgb = OSCURO
st.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
st.paragraph_format.space_after = Pt(4)
st.paragraph_format.line_spacing = 1.15


def estilo_titulo(nombre, tam, color, antes, despues):
    s = doc.styles[nombre]
    s.font.name = FUENTE
    rf = s.element.get_or_add_rPr().get_or_add_rFonts()
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), FUENTE)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    s.font.size = Pt(tam)
    s.font.bold = True
    s.font.italic = False
    s.font.color.rgb = color
    pf = s.paragraph_format
    pf.space_before, pf.space_after, pf.keep_with_next = Pt(antes), Pt(despues), True


estilo_titulo("Title", 22, OSCURO, 0, 2)
estilo_titulo("Heading 1", 13, VERDE, 16, 4)
estilo_titulo("Heading 2", 11, OSCURO, 10, 2)
# El estilo Title trae un borde inferior: se quita
tpPr = doc.styles["Title"].element.get_or_add_pPr()
for b in tpPr.findall(qn("w:pBdr")):
    tpPr.remove(b)


# ---------- utilidades ----------
def run(p, texto, *, bold=False, italic=False, color=None, size=None):
    r = p.add_run(texto)
    r.bold, r.italic = bold, italic
    if color is not None:
        r.font.color.rgb = color
    if size:
        r.font.size = Pt(size)
    return r


def ayuda(texto, despues=3):
    """Texto de instrucciones en gris (fuera de los recuadros)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(despues)
    p.paragraph_format.keep_with_next = True
    run(p, texto, italic=True, color=GRIS, size=9)
    return p


def borde_celda(celda, color=BORDE_CAMPO, grosor=6):
    tcPr = celda._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(grosor))
        e.set(qn("w:color"), color)
        b.append(e)
    tcPr.append(b)


def fondo_celda(celda, color):
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), color)
    celda._tc.get_or_add_tcPr().append(sh)


def margenes_celda(celda, mm=2):
    tcPr = celda._tc.get_or_add_tcPr()
    m = OxmlElement("w:tcMar")
    for lado in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:w"), str(int(mm * 56.7)))
        e.set(qn("w:type"), "dxa")
        m.append(e)
    tcPr.append(m)


def sin_bordes_tabla(tabla):
    tblPr = tabla._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "nil")
        b.append(e)
    tblPr.append(b)


def ancho_fijo(tabla, anchos_cm):
    tabla.autofit = False
    tblPr = tabla._tbl.tblPr
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    tw = OxmlElement("w:tblW")
    tw.set(qn("w:w"), str(int(sum(anchos_cm) * 567)))
    tw.set(qn("w:type"), "dxa")
    tblPr.append(tw)
    for fila in tabla.rows:
        for c, w in zip(fila.cells, anchos_cm):
            c.width = Cm(w)
    grid = tabla._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), anchos_cm):
        gc.set(qn("w:w"), str(int(w * 567)))


def preparar_campo(celda, alto_cm):
    fondo_celda(celda, FONDO_CAMPO)
    borde_celda(celda)
    margenes_celda(celda)
    p = celda.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)


def campo(etiqueta, alto_cm=1.0, pista=None, unir=False):
    """Etiqueta en negrita + recuadro de color para escribir (crece al escribir)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run(p, etiqueta, bold=True)
    if pista:
        run(p, "  " + pista, italic=True, color=GRIS, size=9)
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    ancho_fijo(t, [17])
    fila = t.rows[0]
    fila.height, fila.height_rule = Cm(alto_cm), WD_ROW_HEIGHT_RULE.AT_LEAST
    preparar_campo(fila.cells[0], alto_cm)
    if unir:
        fila.cells[0].paragraphs[0].paragraph_format.keep_with_next = True
    return t


def tabla_datos(filas, ancho_etq=5.2, alto_cm=0.8):
    """Tabla de dos columnas: etiqueta | recuadro para escribir."""
    t = doc.add_table(rows=len(filas), cols=2)
    sin_bordes_tabla(t)
    separar_celdas(t)
    ancho_fijo(t, [ancho_etq, 17 - ancho_etq])
    for fila, (etq, pista) in zip(t.rows, filas):
        fila.height, fila.height_rule = Cm(alto_cm), WD_ROW_HEIGHT_RULE.AT_LEAST
        a, b = fila.cells
        margenes_celda(a, 1.5)
        pa = a.paragraphs[0]
        pa.paragraph_format.space_after = Pt(0)
        run(pa, etq, bold=True)
        if pista:
            pb = a.add_paragraph()
            pb.paragraph_format.space_after = Pt(0)
            run(pb, pista, italic=True, color=GRIS, size=8.5)
        preparar_campo(b, alto_cm)
        espaciado_fila(fila)
    return t


def espaciado_fila(fila):
    pass


def separar_celdas(tabla, mm=1.2):
    """Deja un pequeño hueco entre las celdas para que los recuadros no se toquen."""
    e = OxmlElement("w:tblCellSpacing")
    e.set(qn("w:w"), str(int(mm * 56.7)))
    e.set(qn("w:type"), "dxa")
    tabla._tbl.tblPr.append(e)


def casilla(p, texto, descripcion=None):
    """Casilla de verificación de Word (se marca con un clic) seguida de texto."""
    sdt = OxmlElement("w:sdt")
    pr = OxmlElement("w:sdtPr")
    rpr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    rf.set(qn("w:ascii"), "MS Gothic")
    rf.set(qn("w:hAnsi"), "MS Gothic")
    rf.set(qn("w:eastAsia"), "MS Gothic")
    rpr.append(rf)
    col = OxmlElement("w:color")
    col.set(qn("w:val"), "27AE60")
    rpr.append(col)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "24")
    rpr.append(sz)
    pr.append(rpr)
    cb = OxmlElement("w14:checkbox")
    ch = OxmlElement("w14:checked")
    ch.set(qn("w14:val"), "0")
    cb.append(ch)
    for tag, val in (("w14:checkedState", "2612"), ("w14:uncheckedState", "2610")):
        e = OxmlElement(tag)
        e.set(qn("w14:val"), val)
        e.set(qn("w14:font"), "MS Gothic")
        cb.append(e)
    pr.append(cb)
    sdt.append(pr)
    content = OxmlElement("w:sdtContent")
    r = OxmlElement("w:r")
    r.append(copy.deepcopy(rpr))
    t = OxmlElement("w:t")
    t.text = "☐"
    r.append(t)
    content.append(r)
    sdt.append(content)
    p._p.append(sdt)
    run(p, "  " + texto, bold=descripcion is not None)
    if descripcion:
        run(p, " — " + descripcion, color=GRIS, size=9.5)


def linea_separadora():
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    pPr = p._p.get_or_add_pPr()
    bd = OxmlElement("w:pBdr")
    e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), "8")
    e.set(qn("w:color"), "27AE60")
    e.set(qn("w:space"), "1")
    bd.append(e)
    pPr.append(bd)


def lista(items, numerada=False):
    for it in items:
        p = doc.add_paragraph(style="List Number" if numerada else "List Bullet")
        p.paragraph_format.space_after = Pt(2)
        if isinstance(it, tuple):
            run(p, it[0], bold=True)
            run(p, it[1])
        else:
            run(p, it)


# ---------- cabecera ----------
img = Image.open(LOGO).convert("RGBA")
fondo = Image.new("RGB", img.size, "white")
fondo.paste(img, mask=img.split()[3])
fondo.thumbnail((300, 300))
buf = BytesIO()
fondo.save(buf, "PNG")
buf.seek(0)

hdr = doc.sections[0].header
ht = hdr.add_table(rows=1, cols=2, width=ANCHO)
sin_bordes_tabla(ht)
ancho_fijo(ht, [1.3, 15.7])
c0, c1 = ht.rows[0].cells
c0.paragraphs[0].add_run().add_picture(buf, height=Cm(1.5))
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
c1.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
p = c1.paragraphs[0]
p.paragraph_format.space_after = Pt(0)
run(p, "PLANTOPIA", bold=True, color=OSCURO, size=12)
run(p, "  ·  Revista digital", color=GRIS, size=9.5)
p = c1.add_paragraph()
p.paragraph_format.space_after = Pt(0)
run(p, "CES Jaume I de Picassent  ·  2026-2027", bold=True, color=VERDE, size=9)
hdr.paragraphs[0].paragraph_format.space_after = Pt(0)

# pie con número de página
fp = doc.sections[0].footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run(fp, "Plantilla de artículo · Plantopia · página ", color=GRIS, size=8)
r = fp.add_run()
r.font.size, r.font.color.rgb = Pt(8), GRIS
for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
    if tag:
        e = OxmlElement("w:fldChar")
        e.set(qn("w:fldCharType"), tag)
    else:
        e = OxmlElement("w:instrText")
        e.set(qn("xml:space"), "preserve")
        e.text = txt
    r._r.append(e)

# ---------- portada / instrucciones ----------
doc.add_paragraph("Propuesta de artículo", style="Title")
p = doc.add_paragraph()
run(p, "Escribe tu artículo para Plantopia rellenando los recuadros verdes. ", color=OSCURO)
run(p, "No te preocupes por el diseño: nosotros nos encargamos de la edición y de publicarlo en la web.", color=GRIS)
linea_separadora()

doc.add_paragraph("Cómo rellenar esta plantilla", style="Heading 2")
lista([
    ("Escribe dentro de los recuadros verdes. ", "Crecen solos a medida que escribes."),
    ("Las casillas ☐ se marcan con un clic. ", "Si no se marcan, borra la casilla y escribe una X."),
    ("Los textos en gris son ayudas: ", "no hace falta borrarlos."),
    ("No pegues las fotos en este documento. ", "Entrégalas aparte, como archivos de imagen (JPG o PNG), y anota sus nombres en el apartado 5."),
    ("Al terminar, ", "guarda el documento con tu nombre (por ejemplo: articulo-ana-garcia.docx) y entrégalo junto con las fotos."),
])

# ---------- 1. autor ----------
doc.add_paragraph("1. Sobre ti", style="Heading 1")
tabla_datos([
    ("Nombre y apellidos", None),
    ("Ciclo formativo y curso", "Ej.: 1.º de Grado Medio en…"),
    ("Correo de contacto", "Para consultarte dudas sobre el texto"),
    ("Fecha de entrega", None),
])
p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(8)
run(p, "¿Cómo quieres que aparezca tu nombre en la revista?", bold=True)
for opcion in ("Nombre y apellidos", "Solo el nombre", "Solo las iniciales"):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.4)
    p.paragraph_format.space_after = Pt(1)
    casilla(p, opcion)

# ---------- 2. sección ----------
doc.add_paragraph("2. Sección de la revista", style="Heading 1")
ayuda("Marca la sección en la que encaja mejor tu artículo. Si no lo tienes claro, márcala igualmente y la revisaremos juntos.")
for nombre, desc in (
    ("Editorial", "presentaciones y reflexiones sobre la educación."),
    ("La Noticia", "novedades y actualidad de la Formación Profesional."),
    ("La Entrevista", "conversaciones con personas que hacen la FP."),
    ("Investigación", "oficios, técnicas y saberes explorados a fondo."),
):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.4)
    p.paragraph_format.space_after = Pt(1)
    casilla(p, nombre, desc)

# ---------- 3. presentación ----------
doc.add_paragraph("3. Presentación del artículo", style="Heading 1")
campo("Título", 0.9, "Corto y atractivo: no más de 10 palabras.")
campo("Resumen", 1.6, "Una o dos frases que cuenten de qué trata el artículo. Aparece en la portada.")
campo("Palabras clave", 0.9, "Entre 2 y 4, separadas por comas. Ej.: Olivo, Fermentación, Aprender haciendo")

# ---------- 4. texto ----------
doc.add_paragraph("4. El artículo", style="Heading 1")
ayuda("Extensión recomendada: entre 400 y 900 palabras. Escribe con tus palabras y en párrafos cortos. "
      "Si es una entrevista, escribe cada pregunta en negrita y la respuesta debajo.")

# Recuadro explicativo: cómo se organiza el artículo
nota = doc.add_table(rows=1, cols=1)
nota.alignment = WD_TABLE_ALIGNMENT.CENTER
ancho_fijo(nota, [17])
cn = nota.rows[0].cells[0]
fondo_celda(cn, "F4F5F6")
tcPr = cn._tc.get_or_add_tcPr()
bn = OxmlElement("w:tcBorders")
for lado, val, sz, color in (("top", "nil", 0, None), ("left", "single", 24, "27AE60"),
                             ("bottom", "nil", 0, None), ("right", "nil", 0, None)):
    e = OxmlElement(f"w:{lado}")
    e.set(qn("w:val"), val)
    if color:
        e.set(qn("w:sz"), str(sz))
        e.set(qn("w:color"), color)
    bn.append(e)
tcPr.append(bn)
margenes_celda(cn, 2.5)
pn = cn.paragraphs[0]
pn.paragraph_format.space_after = Pt(4)
run(pn, "¿Cómo se organiza el artículo?", bold=True)
for etq, txt in (
    ("Entrada: ", "un primer párrafo que presenta el tema."),
    ("Apartados: ", "el cuerpo del artículo dividido en partes. Cada apartado trata una idea o un momento "
                    "distinto del tema y lleva su propio subtítulo, que en la web aparece como un título pequeño."),
    ("Cierre: ", "un último párrafo para terminar."),
):
    pp = cn.add_paragraph()
    pp.paragraph_format.space_after = Pt(2)
    pp.paragraph_format.left_indent = Cm(0.3)
    run(pp, "•  " + etq, bold=True, size=9.5)
    run(pp, txt, size=9.5)
pp = cn.add_paragraph()
pp.paragraph_format.space_before = Pt(4)
pp.paragraph_format.space_after = Pt(0)
run(pp, "Ejemplo: ", bold=True, color=VERDE, size=9.5)
run(pp, "en un artículo sobre cómo curamos aceitunas en clase, los apartados podrían ser: "
        "1) «La cosecha: una a una», 2) «Sosa, agua y paciencia» y 3) «El último paso: envasar».",
    italic=True, size=9.5)

campo("Entrada", 2.6, "El primer párrafo: presenta el tema y engancha al lector. Responde a qué, quién, dónde y cuándo.")
nombres = {1: "primera parte del tema", 2: "segunda parte del tema", 3: "tercera parte del tema (opcional)"}
for i in (1, 2, 3):
    doc.add_paragraph(f"Apartado {i}  ·  {nombres[i]}", style="Heading 2")
    campo("Subtítulo", 0.9, "Un título corto para esta parte. Ej.: La cosecha: una a una", unir=True)
    campo("Texto", 4.2 if i < 3 else 3.2, "Lo que quieres contar en esta parte: uno o varios párrafos.")
ayuda("¿Necesitas más apartados? Copia el último apartado (subtítulo y texto) y pégalo debajo. "
      "¿Tu artículo es corto? Deja vacío el apartado 3.", 6)
campo("Cita destacada (opcional)", 1.4, "Una frase importante del artículo o de una persona entrevistada. Indica quién la dice.")
campo("Cierre", 2.2, "El último párrafo: una conclusión, una reflexión o una invitación al lector.")

# ---------- 5. imágenes ----------
doc.add_paragraph("5. Fotos e imágenes", style="Heading 1")
ayuda("La foto principal debe ser horizontal y de buena calidad (mínimo 1200 × 800 píxeles). "
      "Entrega los archivos aparte; aquí solo anota sus datos.")
cols = [3.3, 4.1, 6.1, 3.5]
t = doc.add_table(rows=4, cols=4)
sin_bordes_tabla(t)
separar_celdas(t)
ancho_fijo(t, cols)
for c, txt in zip(t.rows[0].cells, ("", "Nombre del archivo", "¿Qué se ve en la foto?", "Autor/a de la foto")):
    margenes_celda(c, 1.2)
    pp = c.paragraphs[0]
    pp.paragraph_format.space_after = Pt(0)
    pp.paragraph_format.keep_with_next = True
    run(pp, txt, bold=True, size=9.5)
for fila, etq in zip(t.rows[1:], ("Foto principal", "Foto 2 (opcional)", "Foto 3 (opcional)")):
    fila.height, fila.height_rule = Cm(1.2), WD_ROW_HEIGHT_RULE.AT_LEAST
    a = fila.cells[0]
    margenes_celda(a, 1.2)
    pa = a.paragraphs[0]
    pa.paragraph_format.space_after = Pt(0)
    run(pa, etq, bold=True, size=9.5)
    for c in fila.cells[1:]:
        preparar_campo(c, 1.2)
    espaciado_fila(fila)

p = doc.add_paragraph()
p.paragraph_format.space_before = Pt(8)
casilla(p, "Las personas que aparecen en las fotos han dado su permiso para publicarlas.")
ayuda("Si aparecen menores de edad, hace falta además el permiso de su familia. Consulta con tu profesor/a.")

# ---------- 6. vídeo y fuentes ----------
doc.add_paragraph("6. Vídeo y fuentes", style="Heading 1")
campo("Enlace a un vídeo (opcional)", 0.9, "Por ejemplo, un vídeo de YouTube relacionado con el artículo.")
campo("Fuentes consultadas", 1.8, "Libros, webs o personas de las que has sacado información. Si es una web, copia el enlace.")

# ---------- 7. antes de entregar ----------
doc.add_paragraph("7. Antes de entregar", style="Heading 1")
for txt in (
    "El texto es mío y lo he escrito con mis propias palabras.",
    "He indicado las fuentes de la información que no es mía.",
    "He revisado la ortografía y he leído el texto en voz alta una vez.",
    "Entrego las fotos aparte y he anotado sus nombres en el apartado 5.",
    "Acepto que el equipo de Plantopia edite el texto (corrección, títulos, extensión) antes de publicarlo.",
):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.4)
    p.paragraph_format.space_after = Pt(2)
    casilla(p, txt)

linea_separadora()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run(p, "¡Gracias por escribir para Plantopia!", bold=True, color=VERDE, size=11)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run(p, "Cada proyecto es una semilla: la innovación crece en el aula.", italic=True, color=GRIS, size=9.5)

# estilos de lista con la fuente correcta
for n in ("List Bullet", "List Number"):
    s = doc.styles[n]
    s.font.name = FUENTE
    s.font.size = Pt(10)


# ---------- orden de los elementos según el esquema de Word ----------
ORDEN_TBLPR = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize",
               "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook"]
ORDEN_TCPR = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
              "textDirection", "tcFitText", "vAlign", "hideMark"]


ORDEN_PPR = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid",
             "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]


def ordenar(elem, orden):
    hijos = list(elem)
    vistos = {}
    for h in hijos:
        nombre = h.tag.split("}")[1]
        vistos[nombre] = h  # si hay duplicados, se queda el último
        elem.remove(h)
    for nombre in orden:
        if nombre in vistos:
            elem.append(vistos.pop(nombre))
    for h in vistos.values():
        elem.append(h)


def normalizar(raiz):
    for e in raiz.iter(qn("w:tblPr")):
        ordenar(e, ORDEN_TBLPR)
    for e in raiz.iter(qn("w:tcPr")):
        ordenar(e, ORDEN_TCPR)
    for e in raiz.iter(qn("w:pPr")):
        ordenar(e, ORDEN_PPR)


normalizar(doc.element)
normalizar(doc.sections[0].header._element)
normalizar(doc.sections[0].footer._element)
zoom = doc.settings.element.find(qn("w:zoom"))
if zoom is not None:
    zoom.set(qn("w:percent"), "100")

doc.core_properties.title = "Plantopia – Propuesta de artículo"
doc.core_properties.author = "Plantopia"
doc.save(SALIDA)
print("ok", SALIDA)
