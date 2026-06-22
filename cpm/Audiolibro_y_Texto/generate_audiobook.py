import asyncio
import edge_tts
import os
import re
import sys

# Mapeo exacto de los encabezados del libro a los nombres de archivo MP3 correspondientes
CHAPTER_MAP = [
    {
        "header_prefix": "# PRÓLOGO",
        "filename": "01_Prologo.mp3",
        "title": "Prólogo e Introducción"
    },
    {
        "header_prefix": "# LECCIÓN I: Los ricos no trabajan por una nómina",
        "filename": "02_Leccion_I_Los_ricos_no_trabajan_por_una_nomina.mp3",
        "title": "Lección I: Los ricos no trabajan por una nómina"
    },
    {
        "header_prefix": "# LECCIÓN II: Comprar: Posee activos, nunca vendas",
        "filename": "03_Leccion_II_Comprar_Posee_activos_nunca_vendas.mp3",
        "title": "Lección II: Comprar: Posee activos, nunca vendas"
    },
    {
        "header_prefix": "# LECCIÓN III: Pedir Prestado: La deuda es la máquina de la riqueza",
        "filename": "04_Leccion_III_Pedir_Prestado_La_deuda_es_la_maquina_de_la_riqueza.mp3",
        "title": "Lección III: Pedir Prestado: La deuda es la máquina de la riqueza"
    },
    {
        "header_prefix": "# LECCIÓN IV: Morir: El último truco fiscal y el legado familiar",
        "filename": "05_Leccion_IV_Morir_El_ultimo_truco_fiscal_y_el_legado_familiar.mp3",
        "title": "Lección IV: Morir: El último truco fiscal y el legado familiar"
    },
    {
        "header_prefix": "# LECCIÓN V: Rediseña tu tablero",
        "filename": "06_Leccion_V_Redisena_tu_tablero.mp3",
        "title": "Lección V: Rediseña tu tablero"
    },
    {
        "header_prefix": "# EPÍLOGO",
        "filename": "07_Epilogo.mp3",
        "title": "Epílogo"
    },
    {
        "header_prefix": "# CONCLUSIÓN: EL MANIFIESTO DEL ARQUITECTO",
        "filename": "08_Conclusion_El_Manifiesto_del_Arquitecto.mp3",
        "title": "Conclusión: El Manifiesto del Arquitecto"
    },
    {
        "header_prefix": "# NOTA DEL AUTOR",
        "filename": "09_Nota_del_Autor.mp3",
        "title": "Nota del Autor"
    },
    {
        "header_prefix": "# APÉNDICE I: TABLA COMPARATIVA",
        "filename": "10_Apendice_I_Tabla_Comparativa.mp3",
        "title": "Apéndice I: Tabla Comparativa"
    },
    {
        "header_prefix": "# APÉNDICE II: GLOSARIO ENCICLOPÉDICO",
        "filename": "11_Apendice_II_Glosario_Enciclopedico.mp3",
        "title": "Apéndice II: Glosario Enciclopédico del Arquitecto Financiero"
    }
]

def clean_markdown(text):
    """
    Limpia el texto markdown quitando etiquetas, enlaces de imágenes, negritas,
    y normalizando separadores para que el lector de voz no deletree caracteres raros.
    """
    # Eliminar enlaces de imágenes: ![Texto](ruta)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Reemplazar enlaces markdown por el texto del enlace: [texto](url) -> texto
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    # Quitar marcadores de negrita y cursiva: **, *, __, _
    text = re.sub(r'\*\*|__|\*|_', '', text)
    # Quitar líneas divisorias (ej. ---, ───, ════)
    text = re.sub(r'[-─═\*_]{3,}', ' ', text)
    # Eliminar comentarios HTML si existieran
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Procesar línea por línea para limpiar almohadillas de encabezados
    cleaned_lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            # Quitar las almohadillas del inicio y dejar el título limpio
            cleaned_line = stripped.lstrip('#').strip()
            cleaned_lines.append(cleaned_line)
        else:
            cleaned_lines.append(line)
            
    text = '\n'.join(cleaned_lines)
    # Normalizar múltiples saltos de línea para mantener pausas naturales de 1 salto
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def split_into_chunks(text, max_chars=4000):
    """
    Divide un texto largo en fragmentos de tamaño máximo seguro sin cortar palabras
    ni oraciones. Intenta dividir primero por párrafos y luego por frases si es necesario.
    """
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for p in paragraphs:
        # Si agregar el párrafo excede el límite
        if current_length + len(p) + 1 > max_chars:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            # Si el párrafo por sí mismo supera el máximo, lo dividimos en oraciones
            if len(p) > max_chars:
                # Divide por punto, signo de exclamación o interrogación seguidos de espacio
                sentences = re.split(r'(?<=[.!?])\s+', p)
                for s in sentences:
                    if current_length + len(s) + 1 > max_chars:
                        if current_chunk:
                            chunks.append('\n'.join(current_chunk))
                            current_chunk = []
                            current_length = 0
                        chunks.append(s)
                    else:
                        current_chunk.append(s)
                        current_length += len(s) + 1
            else:
                current_chunk.append(p)
                current_length += len(p) + 1
        else:
            current_chunk.append(p)
            current_length += len(p) + 1
            
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
        
    return chunks

async def generate_chapter(text, filename, title, voice, output_dir):
    """
    Genera un archivo MP3 para un capítulo, dividiéndolo en fragmentos
    y concatenando los streams binarios del TTS.
    """
    output_path = os.path.join(output_dir, filename)
    print(f"\n[Procesando] {title}")
    
    cleaned_text = clean_markdown(text)
    # Aplicar la sustitución obligatoria: cambiar "Barcelona" por "Ginebra, Suiza"
    cleaned_text = re.sub(r'\bBarcelona\b', 'Ginebra, Suiza', cleaned_text)
    chunks = split_into_chunks(cleaned_text, max_chars=4000)
    num_chunks = len(chunks)
    
    print(f"  - Caracteres: {len(cleaned_text)} (limpios)")
    print(f"  - Fragmentos para generar: {num_chunks}")
    
    # Escribir en el archivo MP3 final directamente
    with open(output_path, "wb") as out_file:
        for idx, chunk in enumerate(chunks, 1):
            print(f"    -> Generando parte {idx}/{num_chunks}... ", end="", flush=True)
            
            # Reintentar hasta 3 veces por si hay microcortes de red
            success = False
            for attempt in range(3):
                try:
                    communicate = edge_tts.Communicate(chunk, voice)
                    async for packet in communicate.stream():
                        if packet["type"] == "audio":
                            out_file.write(packet["data"])
                    success = True
                    break
                except Exception as e:
                    print(f"\n      [Advertencia] Error en intento {attempt+1}: {e}. Reintentando...", flush=True)
                    await asyncio.sleep(2)
            
            if success:
                print("OK")
            else:
                print("FALLÓ")
                raise Exception(f"No se pudo generar la parte {idx} de {title} tras 3 intentos.")
                
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  - [Completado] Guardado en: {filename} ({file_size_mb:.2f} MB)")

async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    book_path = os.path.join(script_dir, "LIBRO_FINAL_MAQUETADO.md")
    output_dir = script_dir
    voice = "es-ES-AlvaroNeural"
    
    if not os.path.exists(book_path):
        print(f"Error: No se encontró el libro en {book_path}")
        sys.exit(1)
        
    print("==================================================")
    print("INICIANDO CONVERSIÓN DE LIBRO A AUDIOLIBRO")
    print(f"Libro origen: {book_path}")
    print(f"Voz seleccionada: {voice} (Voz humana masculina premium)")
    print("==================================================")
    
    # 1. Leer el libro completo
    with open(book_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 2. Encontrar las posiciones de los encabezados principales
    # Para que coincida de forma flexible con los prefijos definidos en CHAPTER_MAP
    positions = []
    matched_headers = []
    
    # Buscamos todas las líneas que empiezan con #
    lines = content.split('\n')
    char_index = 0
    
    # Construimos un listado de posiciones
    for line in lines:
        if line.strip().startswith('# '):
            # Encontrar el índice de caracteres en content
            # Buscamos a partir de char_index para evitar colisiones
            pos = content.find(line, char_index)
            if pos != -1:
                positions.append((line.strip(), pos))
                char_index = pos + len(line)
                
    print(f"Encabezados de nivel 1 detectados en el markdown: {len(positions)}")
    for h, p in positions:
        print(f"  - {h} (posición: {p})")
        
    # Separar la Introducción general (todo antes de # PRÓLOGO)
    intro_text = ""
    prologue_index = -1
    for idx, (header, pos) in enumerate(positions):
        if "PRÓLOGO" in header.upper():
            prologue_index = idx
            intro_text = content[:pos]
            break
            
    if prologue_index == -1:
        print("Error: No se pudo localizar la sección '# PRÓLOGO' en el libro.")
        sys.exit(1)
        
    print(f"\nIntroducción inicial extraída (~{len(intro_text)} caracteres). Se unirá al Prólogo.")
    
    # 3. Generar cada capítulo
    for ch_idx, chapter in enumerate(CHAPTER_MAP):
        prefix = chapter["header_prefix"].upper()
        
        # Encontrar la sección correspondiente en las posiciones
        section_idx = -1
        for idx, (header, pos) in enumerate(positions):
            # Limpiar acentos y comparar prefijo
            clean_header = header.upper().replace('Ó', 'O').replace('É', 'E').replace('Í', 'I').replace('Á', 'A').replace('Ú', 'U')
            clean_prefix = prefix.replace('Ó', 'O').replace('É', 'E').replace('Í', 'I').replace('Á', 'A').replace('Ú', 'U')
            if clean_header.startswith(clean_prefix):
                section_idx = idx
                break
                
        if section_idx == -1:
            print(f"\nAdvertencia: No se encontró sección que coincida con '{chapter['header_prefix']}'")
            continue
            
        # Determinar el rango de texto para esta sección
        start_pos = positions[section_idx][1]
        if section_idx + 1 < len(positions):
            end_pos = positions[section_idx + 1][1]
        else:
            end_pos = len(content)
            
        chapter_text = content[start_pos:end_pos]
        
        # Si es el prólogo, le añadimos la introducción
        if ch_idx == 0:
            chapter_text = intro_text + "\n\n" + chapter_text
            
        # Generar audio
        await generate_chapter(
            text=chapter_text,
            filename=chapter["filename"],
            title=chapter["title"],
            voice=voice,
            output_dir=output_dir
        )
        
    print("\n==================================================")
    print("PROCESO DE GENERACIÓN DE AUDIOLIBRO COMPLETADO CON ÉXITO")
    print("==================================================")

if __name__ == '__main__':
    # Para entornos Windows con problemas de loop asíncrono
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
