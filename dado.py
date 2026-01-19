import pygame, random, math, sys
from modos import simple, cartas, poly, revelatio 

# ================= INIT =================
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
BASE = min(WIDTH, HEIGHT)

# Pantalla completa
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("EL RITO DEL AZAR")
clock = pygame.time.Clock()

# ================= COLORES =================
BLACK   = (5, 5, 10)
WHITE   = (240, 240, 240)
GOLD    = (255, 215, 0)
PURPLE  = (180, 120, 255)
ACCENT  = (255, 35, 80)
CYAN    = (50, 210, 210)

# ================= FUENTES =================
font_title = pygame.font.SysFont("arial", int(BASE * 0.1), bold=True)
font_btn   = pygame.font.SysFont("arial", int(BASE * 0.05), bold=True) # Fuente un poco más grande

# ================= EFECTOS DE FONDO =================
bg_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(2, 6), random.randint(1, 3)] for _ in range(120)]

def draw_ritual_bg():
    screen.fill(BLACK)
    for s in bg_stars:
        s[1] -= s[2]  
        if s[1] < 0: 
            s[1] = HEIGHT
            s[0] = random.randint(0, WIDTH)
        pygame.draw.line(screen, (70, 70, 120), (s[0], s[1]), (s[0], s[1] + 10), 1)
        pygame.draw.circle(screen, (150, 150, 200), (int(s[0]), int(s[1])), s[3])

# ================= UI =================
def draw_styled_button(rect, text, color, hover=False):
    if hover:
        glow_rect = rect.inflate(15, 15) # Brillo más grande para móvil
        pygame.draw.rect(screen, color, glow_rect, border_radius=30, width=2)
    
    main_col = color if hover else (15, 15, 25)
    pygame.draw.rect(screen, main_col, rect, border_radius=26)
    pygame.draw.rect(screen, color, rect, 4, border_radius=26) # Borde más grueso
    
    txt_col = WHITE if hover else color
    t = font_btn.render(text, True, txt_col)
    screen.blit(t, t.get_rect(center=rect.center))

# ================= BOTONES (OPTIMIZADOS PARA MÓVIL) =================
# Aumentamos el ancho (bw) al 70% de la base y el alto (bh) al 13% para que sean fáciles de tocar
bw, bh = BASE * 0.5, BASE * 0.13
spacing = bh + (BASE * 0.05) # El espacio entre botones ahora es proporcional a su tamaño

# Bajamos un poco el punto de inicio para dar espacio al título
start_y = HEIGHT * 0.35
b1 = pygame.Rect(WIDTH//2 - bw//2, start_y, bw, bh)
b2 = pygame.Rect(WIDTH//2 - bw//2, start_y + spacing, bw, bh)
b3 = pygame.Rect(WIDTH//2 - bw//2, start_y + spacing * 2, bw, bh)
b4 = pygame.Rect(WIDTH//2 - bw//2, start_y + spacing * 3, bw, bh)

# ================= MENU =================
def menu():
    while True:
        mx, my = pygame.mouse.get_pos()
        draw_ritual_bg()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b1.collidepoint(e.pos):
                    pygame.event.clear(); simple.run(screen, clock)
                elif b2.collidepoint(e.pos):
                    pygame.event.clear(); cartas.run(screen, clock)
                elif b3.collidepoint(e.pos):
                    pygame.event.clear(); poly.run(screen, clock)
                elif b4.collidepoint(e.pos):
                    pygame.event.clear(); revelatio.run(screen, clock)

        # TÍTULO FLOTANTE
        t_str = "EL RITO DEL AZAR"
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 8
        
        t_glow = font_title.render(t_str, True, (40, 10, 20))
        screen.blit(t_glow, t_glow.get_rect(center=(WIDTH//2 + 3, HEIGHT*0.18 + 3 + pulse)))
        
        t_surf = font_title.render(t_str, True, WHITE)
        screen.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, HEIGHT*0.18 + pulse)))

        # BOTONES GRANDES
        draw_styled_button(b1, "El Rito", PURPLE, b1.collidepoint(mx, my))
        draw_styled_button(b2, "Fructis Noctis", GOLD, b2.collidepoint(mx, my))
        draw_styled_button(b3, "Multiverso", ACCENT, b3.collidepoint(mx, my))
        draw_styled_button(b4, "Revelatio", CYAN, b4.collidepoint(mx, my))

        pygame.display.flip()
        clock.tick(120)

if __name__ == "__main__":
    menu()
