import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

pdf_path = r"c:\Users\as\Downloads\Organizado\08_Proyectos_Web\capitalinvisible-web\pdf\Instrucciones_Acceso_Comprar_Pedir_Prestado_Morir.pdf"

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

# Gold gradient colors for liquid gold text effect
g1 = colors.HexColor('#BF953F') # Oro base
g2 = colors.HexColor('#FCF6BA') # Reflejo de luz blanca/amarilla
g3 = colors.HexColor('#B38728') # Sombra del oro
g4 = colors.HexColor('#FBF5B7') # Brillo sutil
g5 = colors.HexColor('#AA771C') # Oro profundo
gold_gradient = (g1, g2, g3, g4, g5)

# Custom Styles
body_style = ParagraphStyle(
    'BodyStyle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    textColor=colors.HexColor('#A0A0AB'), # Gris Perla (#A0A0AB)
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
    canvas.drawCentredString(doc.pagesize[0] / 2.0, 30, "© 2026 COMPRAR, PEDIR PRESTADO, MORIR. TODOS LOS DERECHOS RESERVADOS.")
    
    # Draw Title: "COMPRAR, PEDIR PRESTADO, MORIR" with drop shadow and gold gradient
    title_text = "COMPRAR, PEDIR PRESTADO, MORIR"
    title_width = canvas.stringWidth(title_text, "Times-Bold", 20)
    title_x = doc.pagesize[0] / 2.0 - (title_width / 2.0)
    title_y = 670
    
    # Title Shadow (Drop Shadow)
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#000000'))
    canvas.setFont("Times-Bold", 20)
    canvas.drawString(title_x + 1.5, title_y - 1.5, title_text)
    canvas.restoreState()
    
    # Title Gradient Text
    canvas.saveState()
    t_title = canvas.beginText(title_x, title_y)
    t_title.setFont("Times-Bold", 20)
    t_title.setTextRenderMode(4)
    t_title.textLine(title_text)
    canvas.drawText(t_title)
    canvas.linearGradient(title_x, title_y + 18, title_x + title_width, title_y - 4, gold_gradient, extend=True)
    canvas.restoreState()
    
    # Draw Subtitle: "PROTOCOLO DE ACCESO" with drop shadow and gold gradient
    sub_text = "PROTOCOLO DE ACCESO"
    sub_width = canvas.stringWidth(sub_text, "Helvetica-Bold", 14)
    sub_x = doc.pagesize[0] / 2.0 - (sub_width / 2.0)
    sub_y = 625
    
    # Subtitle Shadow
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#000000'))
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(sub_x + 1.0, sub_y - 1.0, sub_text)
    canvas.restoreState()
    
    # Subtitle Gradient Text
    canvas.saveState()
    t_sub = canvas.beginText(sub_x, sub_y)
    t_sub.setFont("Helvetica-Bold", 14)
    t_sub.setTextRenderMode(4)
    t_sub.textLine(sub_text)
    canvas.drawText(t_sub)
    canvas.linearGradient(sub_x, sub_y + 12, sub_x + sub_width, sub_y - 3, gold_gradient, extend=True)
    canvas.restoreState()
    
    canvas.restoreState()

# Add contents
story.append(Spacer(1, 150)) # Leaves room for Title and Subtitle drawn on canvas

intro_html = (
    "Has adquirido el manual de ingeniería financiera y planificación fiscal de los grandes patrimonios. "
    "Este sistema detalla la estrategia de acumulación de activos, el apalancamiento estratégico y la "
    "optimización de herencias. El material que vas a consumir no es información financiera tradicional. "
    "Es un <font color='#bf953f'><b>sistema operativo patrimonial</b></font>."
)
story.append(Paragraph(intro_html, body_style))

# Add a styled table for the credentials
data = [
    [Paragraph("<b>Portal Seguro:</b>", label_style), Paragraph("<font color='#ffffff'><u>https://pub-b479c6d5dd794530a6d617e092b04899.r2.dev/cpm/index.html</u></font>", value_style)],
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
    textColor=colors.HexColor('#A0A0AB'), # Gris Perla (#A0A0AB)
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
