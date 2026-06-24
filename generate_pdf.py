import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

pdf_path = r"c:\Users\as\Downloads\Organizado\08_Proyectos_Web\capitalinvisible-web\pdf\Instrucciones_Acceso_Capital_Invisible.pdf"

# Make sure directory exists
os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                        rightMargin=54, leftMargin=54,
                        topMargin=54, bottomMargin=54)

story = []
styles = getSampleStyleSheet()

# Define luxury style colors (Dark luxury theme)
bg_color = colors.HexColor('#060608')
gold_color = colors.HexColor('#bf953f')
text_light = colors.HexColor('#ffffff')
text_muted = colors.HexColor('#a0a0ab')
border_color = colors.HexColor('#bf953f')

# Custom Styles
title_style = ParagraphStyle(
    'TitleStyle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=28,
    textColor=gold_color,
    alignment=1, # Center
    spaceAfter=10
)

subtitle_style = ParagraphStyle(
    'SubtitleStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=14,
    textColor=text_light,
    alignment=1, # Center
    spaceAfter=40
)

body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    textColor=text_light,
    alignment=1, # Center
    leading=18,
    spaceAfter=35
)

label_style = ParagraphStyle(
    'LabelStyle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=12,
    textColor=gold_color,
    alignment=0, # Left
)

value_style = ParagraphStyle(
    'ValueStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=12,
    textColor=text_light,
    alignment=0, # Left
)

# Header/Background Draw function
def draw_background(canvas, doc):
    canvas.saveState()
    # Fill background
    canvas.setFillColor(bg_color)
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=True, stroke=False)
    
    # Draw a thin gold border frame
    canvas.setStrokeColor(gold_color)
    canvas.setLineWidth(1)
    canvas.rect(20, 20, doc.pagesize[0] - 40, doc.pagesize[1] - 40, fill=False, stroke=True)
    
    # Draw elegant headers/footers
    canvas.setFillColor(gold_color)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(doc.pagesize[0] / 2.0, doc.pagesize[1] - 35, "DOCUMENTO DE ACCESO PRIVADO")
    canvas.drawCentredString(doc.pagesize[0] / 2.0, 30, "© 2026 CAPITAL INVISIBLE. TODOS LOS DERECHOS RESERVADOS.")
    canvas.restoreState()

# Add contents
story.append(Spacer(1, 45))
story.append(Paragraph("CAPITAL INVISIBLE", title_style))
story.append(Paragraph("PROTOCOLO DE ACCESO", subtitle_style))

intro_html = (
    "Has tomado posesión del manual de ingeniería financiera diseñado para quebrar la dependencia "
    "de la nómina y estructurar un motor de acumulación soberano. El material que vas a consumir "
    "no es educación financiera tradicional. Es un <font color='#bf953f'><b>sistema operativo patrimonial</b></font>."
)
story.append(Paragraph(intro_html, body_style))

# Add a styled table for the credentials
data = [
    [Paragraph("<b>Portal Seguro:</b>", label_style), Paragraph("<font color='#ffffff'><u>https://capitalinvisible.online/audiolibro-acceso.html</u></font>", value_style)],
    [Paragraph("<b>Clave Maestra:</b>", label_style), Paragraph("<font color='#bf953f'><b>AS-CAPITAL-2026</b></font>", value_style)]
]

t = Table(data, colWidths=[120, 320])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0d0d10')),
    ('BOX', (0,0), (-1,-1), 1, border_color),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ('TOPPADDING', (0,0), (-1,-1), 15),
    ('LEFTPADDING', (0,0), (-1,-1), 15),
    ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#1f1f24'))
]))

story.append(t)
story.append(Spacer(1, 45))

note_style = ParagraphStyle(
    'NoteStyle',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=9,
    textColor=colors.HexColor('#8e8e93'),
    alignment=1, # Center
    leading=14
)
story.append(Paragraph(
    "Este acceso es estrictamente personal, privado e intransferible. El lector registra y asocia tus "
    "credenciales a tu sesión de manera exclusiva. Cualquier intento de distribución, duplicación o "
    "transferencia de esta clave de acceso revocará de forma definitiva la licencia e invalidará el ingreso, "
    "activando los protocolos correspondientes de protección legal de propiedad intelectual.",
    note_style
))

doc.build(story, onFirstPage=draw_background)
print("PDF generated successfully.")
