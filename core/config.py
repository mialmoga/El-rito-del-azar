"""
🌙 CONFIGURACIÓN DEL RITO DEL AZAR
Valores sagrados que no deben ser profanados... 
...excepto cuando necesitamos ajustar la magia.
"""

# ================= COLORES RITUALES =================
class Colors:
    # Base
    BLACK = (5, 5, 10)
    BG_DARK = (5, 5, 12)
    WHITE = (240, 240, 240)
    
    # Acentos místicos
    GOLD = (255, 215, 0)
    PURPLE = (180, 120, 255)
    ACCENT = (255, 35, 80)
    CYAN = (50, 210, 210)
    
    # Efectos
    ORANGE = (255, 160, 90)
    RED = (220, 60, 60)
    
    # Estrellas
    STAR_CORE = (150, 150, 200)
    STAR_TRAIL = (70, 70, 120)


# ================= FÍSICA DEL RITUAL =================
class Physics:
    # Rotación
    ROTATE_BASE = 0.02
    ROTATE_SPIN = 0.12
    ROTATE_SUDDEN_DEATH = 0.35
    
    # Partículas
    PARTICLE_SPEED = 0.03
    ABSORB_SPEED = 0.08
    
    # Dimensiones
    CELL_COUNT = 900
    STAR_COUNT = 120


# ================= TIEMPOS SAGRADOS =================
class Timing:
    FPS = 120
    SPIN_DURATION = 1.3
    COLLAPSE_DURATION = 0.35
    SPIN_DURATION_CARDS = 1.4


# ================= CONFIGURACIÓN DE MODOS =================
class ModeConfig:
    """Configuración específica por modo"""
    
    # El Rito (dados)
    DICE_SUDDEN_DEATH = False  # Cambiar a True para testing
    
    # Fructis Noctis (cartas)
    CARDS_SUDDEN_DEATH = False  # Cambiar a True para forzar muerte súbita
    CARDS_FORBIDDEN_FRUIT_ENABLED = True  # Momentos especiales
    
    # Multiverso
    POLY_SUDDEN_DEATH = False
    
    # Revelatio
    REVELATIO_SUDDEN_DEATH = False


# ================= TAMAÑOS Y ESCALAS =================
class Scale:
    # Proporciones basadas en BASE (min(WIDTH, HEIGHT))
    WORLD_SCALE = 0.7
    TITLE_FONT = 0.1
    BUTTON_FONT = 0.05
    BIG_FONT = 0.07
    MID_FONT = 0.045
    SMALL_FONT = 0.035
    
    # Tamaños de partículas
    PARTICLE_BG = 2
    PARTICLE_SPIN = 3
    
    # Botones
    BUTTON_WIDTH = 0.5
    BUTTON_HEIGHT = 0.13
    BUTTON_SPACING = 0.05
    
    # Flecha de retorno
    BACK_ARROW_SIZE = 0.05
    BACK_ARROW_MARGIN = 0.05


# ================= PALETA DE CARTAS =================
CARD_PALETTE = [
    (210, 30, 90),   # Rosa intenso
    (255, 100, 10),  # Naranja fuego
    (255, 180, 50),  # Amarillo dorado
    (50, 210, 110),  # Verde esmeralda
    (90, 210, 210),  # Cyan brillante
    (30, 160, 240),  # Azul eléctrico
    (160, 50, 210)   # Púrpura profundo
]


# ================= MAPEO DE VALORES =================
VALUE_TO_FILE = {
    1: "as",
    11: "j",
    12: "q", 
    13: "k",
    20: "jk"  # Joker
}
