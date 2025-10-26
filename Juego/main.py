import pygame
import json
import os
import sys
import random

# ---------------------------
# Configuración inicial (Sin cambios)
# ---------------------------
pygame.init()
ANCHO, ALTO = 900, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Akinator: Soda Stereo") # Título ajustado

# Colores Hex
def hex_a_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

COLOR_FONDO = hex_a_rgb("#BD8E34")  # Dorado/Arena (Mantenido)
GRIS_BOTON = hex_a_rgb("#707070")    # Gris oscuro
GRIS_BOTON_HOVER = hex_a_rgb("#4a4a4a")

# Colores Standard y Bandera de Palestina
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200)

# Colores Bandera Palestina
PAL_NEGRO = (0, 0, 0)
PAL_BLANCO = (255, 255, 255)
PAL_VERDE = (0, 158, 47)
PAL_ROJO = (238, 49, 36)

# Fuentes (Mantenidas)
FUENTE_PATH = "BBHSansBogle-Regular.ttf" 

# Tamaños basados en el ancho de la pantalla (proporcional)
TAM_TITULO_GRANDE = int(ANCHO * 0.15)
TAM_TITULO_SUB = int(ANCHO * 0.08)
TAM_TITULO_CANCION = int(ANCHO * 0.06)
TAM_MEDIANA = int(ANCHO * 0.04)
TAM_NORMAL = int(ANCHO * 0.030)
TAM_PEQUENO = int(ANCHO * 0.020)

try:
    fuente_titulo = pygame.font.Font(FUENTE_PATH, TAM_TITULO_GRANDE)
    fuente_sub = pygame.font.Font(FUENTE_PATH, TAM_TITULO_SUB)
    fuente = pygame.font.Font(FUENTE_PATH, TAM_NORMAL)
    fuente_mediana = pygame.font.Font(FUENTE_PATH, TAM_MEDIANA)
    fuente_titulo_cancion = pygame.font.Font(FUENTE_PATH, TAM_TITULO_CANCION)
    fuente_peq = pygame.font.Font(FUENTE_PATH, TAM_PEQUENO)
    print(f"DEBUG: Fuente '{FUENTE_PATH}' cargada exitosamente.")
except FileNotFoundError:
    print(f"ADVERTENCIA: Archivo de fuente '{FUENTE_PATH}' no encontrado. Usando Arial como fallback.")
    fuente_titulo = pygame.font.SysFont("Arial", TAM_TITULO_GRANDE, bold=True)
    fuente_sub = pygame.font.SysFont("Arial", TAM_TITULO_SUB, bold=True)
    fuente_mediana = pygame.font.SysFont("Arial", TAM_MEDIANA)
    fuente_titulo_cancion = pygame.font.SysFont("Arial", TAM_TITULO_CANCION, bold=True)
    fuente = pygame.font.SysFont("Arial", TAM_NORMAL,bold=True)
    fuente_peq = pygame.font.SysFont("Arial", TAM_PEQUENO)
except Exception as e:
    print(f"ERROR: No se pudo cargar la fuente '{FUENTE_PATH}': {e}. Usando Arial como fallback.")
    fuente_titulo = pygame.font.SysFont("Arial", TAM_TITULO_GRANDE, bold=True)
    fuente_sub = pygame.font.SysFont("Arial", TAM_TITULO_SUB, bold=True)
    fuente_mediana = pygame.font.SysFont("Arial", TAM_MEDIANA, bold=True)
    fuente_titulo_cancion = pygame.font.SysFont("Arial", TAM_TITULO_CANCION, bold=True)
    fuente = pygame.font.SysFont("Arial", TAM_NORMAL)
    fuente_peq = pygame.font.SysFont("Arial", TAM_PEQUENO)

# Rutas
JSON_PATH = "Juego/canciones.json"
CARPETA_PORTADAS = "Portadas"
IMAGEN_PERSONAJE = None
IMAGEN_PERSONAJE_ESCALADA = None 
RUTA_ABSOLUTA_IMAGEN = "Portadas/fondo_akinator.png" 

IMAGEN_FONDO_JUEGO = None 
RUTA_FONDO_JUEGO = "Portadas/fondo.jpg" 

# Opciones de respuesta y pesos (Mantenidos)
OPCIONES = ["Sí", "No", "Probablemente sí", "Probablemente no", "No lo sé"]
PESOS = {"Sí": 3.0, "Probablemente sí": 2.0, "No lo sé": 0.0, "Probablemente no": -2.0, "No": -3.0}

# Atributos generales fijos (Mantenidos)
ATRIBUTOS_GENERALES_FIJOS = [
    ("popularidad", "alta", "¿Es una canción de alta popularidad (un gran éxito)?"),
    ("es_bailable", True, "¿Es una canción bailable?"),
    ("guitarra_prominente", True, "¿La guitarra tiene un rol protagónico y riffs marcados?"),
    ("ritmo", "lento", "¿Es una balada o tema lento?"),
    ("anio_decada", 1980, "¿Fue lanzada en la década de 1980?"),
    ("anio_decada", 1990, "¿Fue lanzada en la década de 1990?"),
    ("anio_decada", 2000, "¿Fue lanzada en la década de 2000?"),
    ("album_en_vivo", True, "¿Es una versión grabada en vivo (Unplugged, Gira, etc.)?")
]
# Campos para los que se generarán preguntas específicas del JSON (Mantenidos)
CAMPOS_PREGUNTABLES = [
    ("album", "¿La canción pertenece al álbum {valor}?"),
    ("emocion", "¿La emoción principal de la canción es {valor}?"),
    ("tema", "¿El tema principal de la letra es {valor}?"),
    ("subgenero", "¿La canción tiene fuertes elementos de {valor}?"),
    ("ritmo", "¿La canción es de ritmo {valor}?"),
    ("instrumentacion", "¿Se caracteriza por el uso de {valor}?"),
    ("epoca", "¿La canción es de la época {valor}?"), 
    ("genero", "¿El género principal es {valor}?"),
    ("letra", "¿El estilo de la letra es {valor}?") 
]

# ---------------------------
# Helpers: Carga de Datos y Lógica de Coincidencia
# ---------------------------

def cargar_canciones(): 
    """Intenta cargar el JSON desde la ruta local o desde la carpeta superior."""
    # Rutas a probar (local y un nivel arriba)
    rutas_a_probar = [
        JSON_PATH, 
        os.path.join("..", JSON_PATH)
    ]
    
    for ruta in rutas_a_probar:
        try:
            ruta_absoluta = os.path.abspath(ruta)
            print(f"DEBUG: Intentando cargar JSON desde: {ruta_absoluta}")

            if os.path.exists(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    if not isinstance(datos, list):
                        if isinstance(datos, dict) and len(datos) == 0:
                            print("ADVERTENCIA: Archivo JSON inicia con objeto vacío, recargando.")
                            continue
                        raise json.JSONDecodeError("El contenido JSON no es una lista", doc="", pos=0)
                        
                    datos = [c for c in datos if isinstance(c, dict) and c.get("titulo")]
                    
                    for c in datos:
                        if "anio" not in c and "año" in c: c["anio"] = c.get("año")
                        if "portada" not in c and "imagen" in c: c["portada"] = c.get("imagen")
                    
                    print(f"DEBUG: JSON cargado exitosamente desde {ruta}. {len(datos)} canciones.")
                    return datos
            
        except FileNotFoundError:
            print(f"ADVERTENCIA: Archivo no encontrado en la ruta: {ruta}")
            continue
        except json.JSONDecodeError as e:
            print(f"ERROR: El archivo JSON ({ruta}) tiene un formato inválido. Detalle: {e}")
            continue
        except Exception as e:
            print(f"ERROR inesperado al cargar JSON desde {ruta}: {e}")
            continue
            
    print(f"ERROR FATAL: No se pudo cargar el archivo canciones.json en ninguna ruta. Devolviendo lista vacía.")
    return []
    
def save_canciones(lista): # Mantenido
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)

def verificar_y_preparar_json(): 
    canciones = cargar_canciones()
    
    # 🌟 FILTRO CLAVE: Solo usar canciones de Soda Stereo 
    canciones = [c for c in canciones if c.get("artista", "").lower() == "soda stereo"]

    if not canciones:
        print("⚠️ No hay canciones de Soda Stereo en el archivo JSON. Agrega al menos una para jugar.")
        return None, None

    preguntas = inicializar_preguntas_candidatas(canciones)

    if not preguntas:
        print("⚠️ No se pudieron generar preguntas. Revisa que las canciones tengan datos válidos.")
        return canciones, None

    print(f"✅ JSON verificado correctamente. {len(canciones)} canciones de Soda Stereo cargadas, {len(preguntas)} preguntas generadas.")
    return canciones, preguntas

def match_atributo(cancion, atributo, valor_esperado): 
    valor_real = cancion.get(atributo)
    valor_esperado_norm = str(valor_esperado).strip().lower()
    
    if valor_real is None: return False

    if atributo == "popularidad":
        vr_norm = str(valor_real).strip().lower()
        if valor_esperado_norm == "alta": 
            return vr_norm in ("alta", "muy alta", "legendaria")
        else:
            return valor_esperado_norm in vr_norm
            
    if atributo == "ritmo":
        vr_norm = str(valor_real).strip().lower()
        if valor_esperado_norm == "lento":
            return "lento" in vr_norm
        else:
            return valor_esperado_norm == vr_norm 

    if atributo in ("es_soda_stereo", "es_solista", "es_bailable", "guitarra_prominente", "album_en_vivo"):
        return bool(valor_real) == (valor_esperado_norm in ("true", "t", "sí", "si", "1"))
        
    if atributo == "anio_decada":
        try:
            anio = int(cancion.get("anio", 0) or 0)
            start = int(valor_esperado)
            return start <= anio <= (start + 9)
        except:
            return False
            
    if isinstance(valor_real, list):
        for item in valor_real:
            if str(item).strip().lower() == valor_esperado_norm: return True
        return False
        
    if isinstance(valor_real, (str, int, float)):
        vr_norm = str(valor_real).strip().lower()
        return valor_esperado_norm == vr_norm 
        
    return False

def cargar_imagen(portada_path, max_w=None, max_h=None): # Mantenida
    if not portada_path: return None
    ruta_absoluta = os.path.join(os.path.dirname(os.path.abspath(__file__)), portada_path)
    if not os.path.exists(ruta_absoluta): return None
    try:
        img = pygame.image.load(ruta_absoluta)
        w, h = img.get_size()
        
        if max_w is None and max_h is None:
            max_w = ANCHO * 0.35 
            max_h = ALTO * 0.5   

        scale_w, scale_h = 1.0, 1.0
        if max_w is not None and w > 0:
            scale_w = max_w / w
        if max_h is not None and h > 0:
            scale_h = max_h / h
        
        scale = min(scale_w, scale_h)
        
        new_size = (max(int(w * scale), 1), max(int(h * scale), 1))
        
        img = pygame.transform.smoothscale(img, new_size)
        return img
    except pygame.error as e:
        print(f"Error de Pygame al cargar la imagen de portada {ruta_absoluta}: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al cargar la imagen de portada {ruta_absoluta}: {e}")
        return None

def cargar_imagen_fondo_principal(ruta_imagen, ancho_pantalla, alto_pantalla): # Mantenida
    ruta_absoluta = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta_imagen))
    if not os.path.exists(ruta_absoluta):
        print(f"ERROR: Archivo de fondo principal no encontrado en: {ruta_absoluta}")
        return None
    try:
        img = pygame.image.load(ruta_absoluta).convert()
        img = pygame.transform.scale(img, (ancho_pantalla, alto_pantalla))
        print(f"DEBUG: Imagen de fondo principal cargada y escalada a {ancho_pantalla}x{alto_pantalla}.")
        return img
    except pygame.error as e:
        print(f"ERROR: Pygame no pudo cargar '{ruta_absoluta}' (Fondo principal): {e}")
        return None
    except Exception as e:
        print(f"ERROR inesperado al cargar '{ruta_absoluta}' (Fondo principal): {e}")
        return None


def cargar_imagen_fondo_akinator(ruta_imagen=None, max_w=550, max_h=700): # Mantenida
    global IMAGEN_PERSONAJE, IMAGEN_PERSONAJE_ESCALADA
    
    if not ruta_imagen:
        ruta_absoluta = os.path.join(os.path.dirname(os.path.abspath(__file__)), RUTA_ABSOLUTA_IMAGEN)
    else:
        ruta_absoluta = os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta_imagen)
    
    ruta_absoluta = os.path.abspath(ruta_absoluta)
    print(f"DEBUG: Intentando cargar imagen desde: {ruta_absoluta}")
    if not os.path.exists(ruta_absoluta):
        print(f"ERROR: Archivo no encontrado en: {ruta_absoluta}")
        IMAGEN_PERSONAJE = IMAGEN_PERSONAJE_ESCALADA = None
        return None

    try:
        img = pygame.image.load(ruta_absoluta).convert_alpha() 
        w, h = img.get_size()
        scale_w = max_w / w if w > 0 else 1.0
        scale_h = max_h / h if h > 0 else 1.0
        scale = min(scale_w, scale_h, 1.0)
        new_size = (max(int(w * scale), 1), max(int(h * scale), 1))
        
        IMAGEN_PERSONAJE = pygame.transform.smoothscale(img, new_size)
        IMAGEN_PERSONAJE_ESCALADA = None
        
        print(f"DEBUG: Imagen cargada exitosamente. Tamaño original: {w}x{h}, Tamaño escalado: {new_size}")
        return IMAGEN_PERSONAJE

    except pygame.error as e:
        print(f"ERROR: Pygame no pudo cargar '{ruta_absoluta}': {e}")
        IMAGEN_PERSONAJE = IMAGEN_PERSONAJE_ESCALADA = None
        return None
    except Exception as e:
        print(f"ERROR inesperado al cargar '{ruta_absoluta}': {e}")
        IMAGEN_PERSONAJE = IMAGEN_PERSONAJE_ESCALADA = None
        return None

def inicializar_preguntas_candidatas(canciones): # Mantenida
    preguntas = []

    # Agrega las preguntas generales/fijas
    for atributo, valor, texto in ATRIBUTOS_GENERALES_FIJOS:
        preguntas.append((texto, atributo, valor))

    # Agrega las preguntas DINÁMICAS basadas en el JSON
    for campo, plantilla_texto in CAMPOS_PREGUNTABLES:
        valores_unicos = set()
        for cancion in canciones:
            valor = cancion.get(campo)
            if valor:
                if isinstance(valor, str):
                    valores_unicos.add(valor.strip().lower())
                elif isinstance(valor, list):
                    for item in valor:
                        valores_unicos.add(item.strip().lower())

        valores_unicos = {v for v in valores_unicos if v}
        
        # Crea una pregunta para cada valor único encontrado en el JSON
        for valor in valores_unicos:
            texto_pregunta = plantilla_texto.format(valor=valor.capitalize())
            preguntas.append((texto_pregunta, campo, valor))
            
    return preguntas

def seleccionar_mejor_pregunta(candidatos, todas_las_preguntas, preguntas_usadas): # Mantenida
    mejor_pregunta = None
    max_power = -1

    preguntas_disponibles = [p for p in todas_las_preguntas if p not in preguntas_usadas]

    if not preguntas_disponibles:
        return None

    for texto, atributo, valor_esperado in preguntas_disponibles:

        candidatos_si = 0
        candidatos_no = 0
        total = len(candidatos)

        if total <= 1: return None 
        for cancion in candidatos:
            if match_atributo(cancion, atributo, valor_esperado):
                candidatos_si += 1
            else:
                candidatos_no += 1

        power = total - abs(candidatos_si - candidatos_no)

        if candidatos_si == 0 or candidatos_no == 0:
             power = -1

        if power > max_power:
            max_power = power
            mejor_pregunta = (texto, atributo, valor_esperado)

    return mejor_pregunta


# ---------------------------
# Lógica del Juego
# ---------------------------

def jugar_tema():
    clock = pygame.time.Clock()
    
    # Ahora solo se cargan canciones de Soda Stereo (verificar_y_preparar_json() filtrará)
    canciones, todas_las_preguntas = verificar_y_preparar_json()

    if not canciones or not todas_las_preguntas:
        mostrar_no_encontrado("las canciones o preguntas")
        return

    candidatos = canciones
    for c in candidatos:
        c["__score__"] = 0.0 # Inicializar scores
    preguntas_usadas = []
    
    umbral_confianza = 5.0 

    # 🌟 ELIMINACIÓN DE LA PREGUNTA INICIAL DE ARTISTA
    # Se inicia el bucle principal de preguntas dinámicas directamente,
    # ya que se asume que la canción es de Soda Stereo.
    
    # --- Bucle Principal de Preguntas Dinámicas ---
    while len(candidatos) > 1 and len(preguntas_usadas) <= 25:
        
        # -----------------------------------------------------------------
        # LÓGICA DE VICTORIA POR MARGEN: Comprobar si se puede adivinar
        # -----------------------------------------------------------------
        candidatos_sorted = sorted(candidatos, key=lambda x: x.get("__score__", 0), reverse=True)
        
        if len(candidatos_sorted) > 1:
            best_score = candidatos_sorted[0].get("__score__", 0)
            second_best_score = candidatos_sorted[1].get("__score__", 0)
            
            if best_score - second_best_score > umbral_confianza:
                mostrar_resultado(candidatos_sorted[0], candidatos_sorted[0]["artista"])
                return
        elif len(candidatos_sorted) == 1:
            mostrar_resultado(candidatos_sorted[0], candidatos_sorted[0]["artista"])
            return

        # -----------------------------------------------------------------
        
        pregunta = seleccionar_mejor_pregunta(candidatos, todas_las_preguntas, preguntas_usadas)

        if not pregunta:
            break 
            
        preguntas_usadas.append(pregunta)
        texto, atributo, valor_esperado = pregunta
        respuesta = mostrar_pregunta(texto, len(preguntas_usadas))

        if respuesta == "No lo sé":
            continue

        peso = PESOS.get(respuesta, 0.0)

        for c in candidatos:
            try:
                coincide = match_atributo(c, atributo, valor_esperado)
                
                if (coincide and peso >= 0) or (not coincide and peso < 0):
                    c["__score__"] += abs(peso) 
                else:
                    c["__score__"] -= abs(peso) 
            except Exception:
                pass 

        clock.tick(30)

    # Si se acaban las preguntas (bucle termina)
    if candidatos:
        candidato_final = sorted(candidatos, key=lambda x: x.get("__score__", 0), reverse=True)[0]
        if candidato_final.get("__score__", 0) < 8.0: 
             mostrar_no_encontrado("la canción")
        else:
             mostrar_resultado(candidato_final, candidato_final["artista"])
    else:
        mostrar_no_encontrado("la canción")


# ---------------------------
# Funciones de Interfaz (UI)
# ---------------------------

def dibujar_texto(texto, fuente_obj, color, x, y, max_width=None, align="center"): # Mantenida
    if max_width:
        words = texto.split()
        lines = []
        current_line = []
        current_length = 0
        
        space_width = fuente_obj.size(" ")[0]

        for word in words:
            word_width = fuente_obj.size(word)[0]
            if not current_line or current_length + space_width + word_width <= max_width:
                current_line.append(word)
                current_length += word_width + space_width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_width + space_width
        if current_line:
            lines.append(" ".join(current_line))
        
        for i, line in enumerate(lines):
            surf = fuente_obj.render(line, True, color)
            line_y = y + i * fuente_obj.get_linesize()
            if align == "center":
                rect = surf.get_rect(center=(x, line_y))
            elif align == "left":
                rect = surf.get_rect(topleft=(x, line_y))
            pantalla.blit(surf, rect)
    else:
        surf = fuente_obj.render(texto, True, color)
        if align == "center":
            rect = surf.get_rect(center=(x, y))
        elif align == "left":
            rect = surf.get_rect(topleft=(x, y))
        pantalla.blit(surf, rect)


def dibujar_boton(rect, texto, hover): # Mantenida
    color = GRIS_BOTON_HOVER if hover else GRIS_BOTON
    pygame.draw.rect(pantalla, color, rect, border_radius=8)
    dibujar_texto(texto, fuente, BLANCO, rect.centerx, rect.centery, align="center") 

def confirmar_salida(): # Mantenida
    running = True
    while running:
        if IMAGEN_FONDO_JUEGO:
            pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO) 
            
        s = pygame.Surface((ANCHO * 0.8, ALTO * 0.6), pygame.SRCALPHA)
        s.fill((255, 255, 255, 180)) 
        pantalla.blit(s, (ANCHO * 0.1, ALTO * 0.2))

        dibujar_texto("¿Deseas salir del juego?", fuente, NEGRO, ANCHO//2, ALTO//2 - 50)
        rect_si = pygame.Rect(ANCHO//2 - 140, ALTO//2, 120, 50)
        rect_no = pygame.Rect(ANCHO//2 + 20, ALTO//2, 120, 50)
        mouse = pygame.mouse.get_pos()
        dibujar_boton(rect_si, "Sí", rect_si.collidepoint(mouse))
        dibujar_boton(rect_no, "No", rect_no.collidepoint(mouse))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q: return True
                if e.key == pygame.K_ESCAPE: return False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if rect_si.collidepoint(e.pos): return True
                if rect_no.collidepoint(e.pos): return False

def dibujar_titulo_pantalla_inicio(x, y): 
    titulo_akinator = "Akinator"
    # CAMBIO 1: Usar NEGRO estándar para el título principal
    surf_akinator = fuente_titulo.render(titulo_akinator, True, NEGRO)
    rect_akinator = surf_akinator.get_rect(center=(x, y - 60))
    pantalla.blit(surf_akinator, rect_akinator)
    
    # 🌟 Ajuste: Solo mostrar "Soda Stereo"
    subtitulo_artistas = "Soda Stereo" 
    palabras_sub = subtitulo_artistas.split()
    # CAMBIO 2: La lista de colores ahora solo contiene NEGRO.
    # Antes: colores_sub = [PAL_ROJO, PAL_BLANCO, PAL_VERDE, PAL_NEGRO]
    colores_sub = [NEGRO]

    current_x = x - fuente_sub.size(subtitulo_artistas)[0] / 2
    for i, palabra in enumerate(palabras_sub):
        # La línea de código mantiene su lógica de iteración, pero siempre usa NEGRO
        color = colores_sub[i % len(colores_sub)] 
        surf_palabra = fuente_sub.render(palabra, True, color)
        pantalla.blit(surf_palabra, (current_x, y + 20))
        current_x += surf_palabra.get_width() + fuente_sub.size(" ")[0]

def pantalla_inicio(): # Lógica de inicio modificada
    clock = pygame.time.Clock()
    running = True
    start_rect = pygame.Rect(ANCHO//2 - 150, ALTO//2 + 50, 300, 80) 
    while running:
        
        if IMAGEN_FONDO_JUEGO:
            pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO) 
        
        # El título ya no muestra a Cerati
        dibujar_titulo_pantalla_inicio(ANCHO // 2, ALTO // 2 - 120)

        mouse = pygame.mouse.get_pos()
        dibujar_boton(start_rect, "EMPEZAR", start_rect.collidepoint(mouse))
        dibujar_texto("Presiona Q para salir", fuente_peq, NEGRO, ANCHO - 150, ALTO - 30, max_width=250)

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if confirmar_salida(): pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    if confirmar_salida(): pygame.quit(); sys.exit()
                if e.key == pygame.K_RETURN: return # Inicia el juego
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if start_rect.collidepoint(e.pos): return # Inicia el juego
        clock.tick(30)

def mostrar_pregunta(texto, num_pregunta): # Mantenida
    clock = pygame.time.Clock()
    espera = True
    global IMAGEN_PERSONAJE
    while espera:
        
        if IMAGEN_FONDO_JUEGO:
            pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO) 
            
        AREA_IZQUIERDA_X = ANCHO * 0.05
        AREA_IZQUIERDA_W = ANCHO * 0.45
        s = pygame.Surface((int(AREA_IZQUIERDA_W) + 20, ALTO * 0.9), pygame.SRCALPHA)
        s.fill((255, 255, 255, 180)) 
        pantalla.blit(s, (AREA_IZQUIERDA_X - 10, ALTO * 0.05))

        if IMAGEN_PERSONAJE:
            img_x = ANCHO - IMAGEN_PERSONAJE.get_width() - 1
            img_y = ALTO // 2 - IMAGEN_PERSONAJE.get_height() // 2 
            pantalla.blit(IMAGEN_PERSONAJE, (img_x, img_y))

        
        btn_center_x = int(AREA_IZQUIERDA_X + AREA_IZQUIERDA_W/2)
        
        dibujar_texto(f"Pregunta {num_pregunta} / 25", fuente_peq, NEGRO, btn_center_x, 80)
        dibujar_texto(texto, fuente, NEGRO, btn_center_x, 160, max_width=int(AREA_IZQUIERDA_W))
        
        botones = []
        btn_w, btn_h = 350, 54
        start_y = 240
        mouse = pygame.mouse.get_pos()
        
        for i, op in enumerate(OPCIONES):
            rect = pygame.Rect(btn_center_x - btn_w // 2, start_y + i*(btn_h+10), btn_w, btn_h)
            dibujar_boton(rect, op, rect.collidepoint(mouse))
            botones.append((rect, op))

        rect_salir = pygame.Rect(ANCHO - 140, 20, 100, 40)
        dibujar_boton(rect_salir, "Salir (Q)", rect_salir.collidepoint(mouse))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if confirmar_salida(): pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_q:
                    if confirmar_salida(): pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if rect_salir.collidepoint(e.pos):
                    if confirmar_salida(): pygame.quit(); sys.exit()
                    else: continue
                for rect, opcion in botones:
                    if rect.collidepoint(e.pos): return opcion
        clock.tick(60)

def mostrar_resultado(cancion, artista): # Mantenida
    clock = pygame.time.Clock()
    
    mostrando = True
    while mostrando:
        
        if IMAGEN_FONDO_JUEGO:
            pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO) 

        s = pygame.Surface((ANCHO * 0.9, ALTO * 0.8), pygame.SRCALPHA)
        s.fill((255, 255, 255, 180)) 
        pantalla.blit(s, (ANCHO * 0.05, ALTO * 0.05))

        SIDE_MARGIN = ANCHO * 0.05
        TOP_MARGIN = ALTO * 0.08 
        LINE_SPACING = 32 
        
        COL_WIDTH = (ANCHO - SIDE_MARGIN * 2) // 2 
        
        LEFT_HALF_CENTER_X = (ANCHO // 4) + 80
        ESTIMATED_TEXT_BLOCK_WIDTH = COL_WIDTH * 0.9 
        TEXT_COL_START_X = LEFT_HALF_CENTER_X - (ESTIMATED_TEXT_BLOCK_WIDTH // 2)
        
        titulo_y = TOP_MARGIN + 40 
        dibujar_texto("Creo que la canción es:", fuente, NEGRO, LEFT_HALF_CENTER_X, titulo_y, align="center")
        
        titulo_cancion_y = titulo_y + fuente.get_linesize() + 40 
    
        dibujar_texto(cancion.get("titulo", "Desconocida"), fuente_titulo_cancion, PAL_ROJO, LEFT_HALF_CENTER_X, titulo_cancion_y, max_width=ESTIMATED_TEXT_BLOCK_WIDTH, align="center") 

        info_lines = [
    f"Artista: {cancion.get('artista','')}",
    f"Álbum: {cancion.get('album','')}",
    f"Año: {cancion.get('anio','')}",
    f"Género: {cancion.get('genero','')}",
    f"Época: {cancion.get('epoca','')}",
    f"Duración: {cancion.get('duracion','')}",
]

        
        y_info_start = titulo_cancion_y + fuente_sub.get_linesize() + 10 

        for i, line in enumerate(info_lines):
              dibujar_texto(line, fuente, NEGRO, TEXT_COL_START_X, y_info_start + i * LINE_SPACING, max_width=ESTIMATED_TEXT_BLOCK_WIDTH, align="left")
        
        
        altura_portada_deseada = 300
        ancho_max_portada = COL_WIDTH * 0.99
        
        portada = cargar_imagen(cancion.get("portada") or "", max_w=ancho_max_portada, max_h=altura_portada_deseada)
        
        if portada:
            RIGHT_HALF_CENTER_X = ANCHO * 3 // 4 
            portada_x = RIGHT_HALF_CENTER_X - (portada.get_width() // 2)
            portada_y = y_info_start - 80
            
            pantalla.blit(portada, (portada_x, portada_y)) 
        else:
            RIGHT_HALF_CENTER_X = ANCHO * 3 // 4 
            dibujar_texto("[Portada no encontrada]", fuente, PAL_ROJO, RIGHT_HALF_CENTER_X, y_info_start + altura_portada_deseada / 2, align="center") 
            
        mouse = pygame.mouse.get_pos()
        BUTTON_Y_POS = ALTO - (ALTO * 0.12) + 20 
        btn_w = 200 
        btn_gap = 40
        
        rect_si = pygame.Rect(ANCHO//2 - btn_w - btn_gap//2, BUTTON_Y_POS, btn_w, 60) 
        rect_no = pygame.Rect(ANCHO//2 + btn_gap//2, BUTTON_Y_POS, btn_w, 60) 
        
        dibujar_boton(rect_si, "¡Sí! Correcta", rect_si.collidepoint(mouse))
        dibujar_boton(rect_no, "No, no es", rect_no.collidepoint(mouse))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if confirmar_salida(): pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if rect_si.collidepoint(e.pos):
                    if IMAGEN_FONDO_JUEGO:
                        pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
                        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
                        s.fill((255, 255, 255, 100)) 
                        pantalla.blit(s, (0, 0))
                    else:
                        pantalla.fill(COLOR_FONDO) 
                    dibujar_texto("¡Genial! He adivinado la canción 🎉", fuente, PAL_VERDE, ANCHO//2, ALTO//2)
                    pygame.display.flip()
                    pygame.time.wait(1500)
                    return
                if rect_no.collidepoint(e.pos):
                    preguntar_agregar_cancion(artista)
                    return
        clock.tick(60)

def mostrar_no_encontrado(tema_nombre): 
    if IMAGEN_FONDO_JUEGO:
        pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
    else:
        pantalla.fill(COLOR_FONDO) 

    s = pygame.Surface((ANCHO * 0.8, ALTO * 0.6), pygame.SRCALPHA)
    s.fill((255, 255, 255, 180)) 
    pantalla.blit(s, (ANCHO * 0.1, ALTO * 0.2))

    dibujar_texto(f"No pude determinar {tema_nombre} con certeza.", fuente, PAL_ROJO, ANCHO//2, ALTO//2 - 40)
    dibujar_texto("¿Deseas agregar la canción que pensabas para que aprenda?", fuente, NEGRO, ANCHO//2, ALTO//2 + 10)
    rect_si = pygame.Rect(ANCHO//2 - 120, ALTO//2 + 60, 110, 45)
    rect_no = pygame.Rect(ANCHO//2 + 20, ALTO//2 + 60, 110, 45)
    mouse = pygame.mouse.get_pos()
    dibujar_boton(rect_si, "Sí", rect_si.collidepoint(mouse))
    dibujar_boton(rect_no, "No", rect_no.collidepoint(mouse))
    pygame.display.flip()
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if confirmar_salida(): pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if rect_si.collidepoint(e.pos):
                    # 🌟 Ajuste: Artista siempre es Soda Stereo
                    preguntar_agregar_cancion("Soda Stereo")
                    return
                if rect_no.collidepoint(e.pos): return

def preguntar_agregar_cancion(artista_predeterminado): 
    clock = pygame.time.Clock()
    campos = {
        "titulo": "", "album": "", "anio": "", "emocion": "", "tema": "", "portada": "",
        "subgenero": "", "ritmo": "", "instrumentacion": "", "letra": "",
        "descripcion_portada": "", "es_bailable": False,
    }
    campo_keys = list(campos.keys())
    paso = 0 # El paso 0 antes era para elegir artista. Ahora es solo una etapa de transición.

    # 🌟 Ajuste: Artista es SIEMPRE Soda Stereo, eliminando la elección
    artista = "Soda Stereo" 
    es_soda = True

    campo_actual_key = campo_keys[paso - 1] if paso > 0 else None
    input_text = ""

    def get_info_msg(key):
        msgs = {
            "titulo": "Ingresa el Título de la canción:",
            "album": "Ingresa el Álbum:", "anio": "Ingresa el Año (solo números):",
            "emocion": "Ingresa la Emoción principal (ej: melancólica):",
            "tema": "Ingresa el Tema principal (ej: soledad):",
            "subgenero": "Ingresa el Subgénero (ej: rock alternativo):",
            "ritmo": "Ingresa el Ritmo (ej: lento, medio, rápido):",
            "instrumentacion": "Instrumento clave (ej: sintetizador):",
            "portada": "Ruta de la Portada (ej: Portadas/Signos.jpg):",
            "letra": "Pega un fragmento de la Letra (opcional):",
            "descripcion_portada": "Describe la Portada (opcional):",
            "es_bailable": "¿Es una canción bailable? (Sí/No)",
        }
        return msgs.get(key, f"Ingresa {key}:")

    running = True
    # Iniciar directamente desde el paso 1 (primer campo de la canción)
    if paso == 0:
        paso = 1 
        if campo_keys:
             input_text = campos.get(campo_keys[0], "")

    while running:
        if IMAGEN_FONDO_JUEGO:
            pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
        else:
            pantalla.fill(COLOR_FONDO) 

        s = pygame.Surface((ANCHO * 0.9, ALTO * 0.9), pygame.SRCALPHA)
        s.fill((255, 255, 255, 180)) 
        pantalla.blit(s, (ANCHO * 0.05, ALTO * 0.05))
        
        center_x = ANCHO // 2
        
        dibujar_texto("¡Ayúdame a aprender!", fuente_mediana, NEGRO, center_x, 80)
        
        mouse = pygame.mouse.get_pos()
        rect_siguiente = pygame.Rect(center_x + 10, ALTO - 100, 180, 50)
        rect_anterior = pygame.Rect(center_x - 190, ALTO - 100, 180, 50)
        
        # 🌟 ELIMINACIÓN DE LA PANTALLA DE SELECCIÓN DE ARTISTA (paso 0)
        
        campo_actual_key = campo_keys[paso - 1]
        mensaje_info = get_info_msg(campo_actual_key)
        
        dibujar_texto(f"Paso {paso} / {len(campo_keys)}", fuente_peq, NEGRO, center_x, 130)
        dibujar_texto(mensaje_info, fuente, NEGRO, center_x, 170, max_width=ANCHO * 0.8)

        if campo_actual_key == "es_bailable":
            rect_bool_si = pygame.Rect(center_x - 130, 250, 120, 50)
            rect_bool_no = pygame.Rect(center_x + 10, 250, 120, 50)
            
            es_bailable_actual = campos[campo_actual_key]
            dibujar_boton(rect_bool_si, "Sí", rect_bool_si.collidepoint(mouse) or es_bailable_actual)
            dibujar_boton(rect_bool_no, "No", rect_bool_no.collidepoint(mouse) or not es_bailable_actual)
        
        else:
            input_rect = pygame.Rect(center_x - 250, 250, 500, 50)
            pygame.draw.rect(pantalla, BLANCO, input_rect)
            pygame.draw.rect(pantalla, NEGRO, input_rect, 2)
            dibujar_texto(input_text, fuente, NEGRO, input_rect.x + 10, input_rect.centery, max_width=input_rect.width - 20, align="left")

        dibujar_boton(rect_anterior, "Anterior", rect_anterior.collidepoint(mouse))
        if paso == len(campo_keys):
            dibujar_boton(rect_siguiente, "GUARDAR", rect_siguiente.collidepoint(mouse))
        else:
            dibujar_boton(rect_siguiente, "Siguiente", rect_siguiente.collidepoint(mouse))


        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if confirmar_salida(): pygame.quit(); sys.exit()
                
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                
                if rect_anterior.collidepoint(e.pos):
                    # Guarda el texto actual antes de retroceder
                    if campo_actual_key != "es_bailable":
                        campos[campo_actual_key] = input_text
                    
                    if paso > 1: # No retrocede a paso 0
                        paso -= 1
                        # Carga el texto del campo anterior
                        input_text = campos.get(campo_keys[paso - 1], "")
                    
                elif rect_siguiente.collidepoint(e.pos):
                    # Guarda el texto actual antes de avanzar/guardar
                    if campo_actual_key != "es_bailable":
                        campos[campo_actual_key] = input_text

                    if paso == len(campo_keys):
                        # Lógica de GUARDAR
                        nueva_cancion = {"artista": artista, "es_soda_stereo": es_soda}
                        for key, val in campos.items():
                            if key == "anio" and isinstance(val, str) and val.isdigit():
                                nueva_cancion[key] = int(val)
                            else:
                                nueva_cancion[key] = val
                        
                        lista_canciones = cargar_canciones()
                        lista_canciones.append(nueva_cancion)
                        save_canciones(lista_canciones)
                        
                        print(f"✅ Canción '{nueva_cancion['titulo']}' guardada en {JSON_PATH}")
                        
                        if IMAGEN_FONDO_JUEGO: pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
                        else: pantalla.fill(COLOR_FONDO)
                        s_final = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA); s_final.fill((255, 255, 255, 100)); pantalla.blit(s_final, (0, 0))
                        dibujar_texto("¡Canción guardada! Gracias por enseñar.", fuente, PAL_VERDE, ANCHO//2, ALTO//2)
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        return 
                    
                    else: 
                        paso += 1
                        # Carga el texto del campo siguiente
                        input_text = campos.get(campo_keys[paso - 1], "")
                
                if campo_actual_key == "es_bailable":
                    if rect_bool_si.collidepoint(e.pos):
                        campos[campo_actual_key] = True
                    if rect_bool_no.collidepoint(e.pos):
                        campos[campo_actual_key] = False

            if e.type == pygame.KEYDOWN and paso > 0 and campo_actual_key != "es_bailable":
                if e.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif e.key == pygame.K_RETURN:
                    # Guardar el texto actual antes de avanzar/guardar
                    campos[campo_actual_key] = input_text

                    if paso < len(campo_keys):
                         paso += 1
                         input_text = campos.get(campo_keys[paso - 1], "")
                    elif paso == len(campo_keys):
                         # Lógica de guardar
                         nueva_cancion = {"artista": artista, "es_soda_stereo": es_soda}
                         for key, val in campos.items():
                             if key == "anio" and isinstance(val, str) and val.isdigit():
                                 nueva_cancion[key] = int(val)
                             else:
                                 nueva_cancion[key] = val
                         lista_canciones = cargar_canciones()
                         lista_canciones.append(nueva_cancion)
                         save_canciones(lista_canciones)
                         
                         print(f"✅ Canción '{nueva_cancion['titulo']}' guardada en {JSON_PATH}")
                         
                         if IMAGEN_FONDO_JUEGO: pantalla.blit(IMAGEN_FONDO_JUEGO, (0, 0))
                         else: pantalla.fill(COLOR_FONDO)
                         s_final = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA); s_final.fill((255, 255, 255, 100)); pantalla.blit(s_final, (0, 0))
                         dibujar_texto("¡Canción guardada! Gracias por enseñar.", fuente, PAL_VERDE, ANCHO//2, ALTO//2)
                         pygame.display.flip()
                         pygame.time.wait(2000)
                         return
                else:
                    input_text += e.unicode
                
                # Guardar el texto actual en el diccionario 'campos'
                campos[campo_actual_key] = input_text


        pygame.display.flip()
        clock.tick(30)


# ---------------------------
# Bucle Principal
# ---------------------------
def main(): 
    global IMAGEN_FONDO_JUEGO, IMAGEN_PERSONAJE
    
    IMAGEN_FONDO_JUEGO = cargar_imagen_fondo_principal(RUTA_FONDO_JUEGO, ANCHO, ALTO)
    IMAGEN_PERSONAJE = cargar_imagen_fondo_akinator(RUTA_ABSOLUTA_IMAGEN, max_w=ANCHO*0.45, max_h=ALTO*0.9)

    while True:
        pantalla_inicio()
        jugar_tema() 

if __name__ == "__main__":
    main()