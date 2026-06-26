"""
🌙 EL RITO DEL AZAR
Menú principal del sistema ritual.

Refactorizado pero preservando la magia original.
"""

import pygame
import sys
import math

# Importar núcleo
from core import Colors, Scale, Timing, RitualEngine

# Importar modos
from modes import el_rito, fructis_noctis, multiverso, revelatio


def main():
    """Punto de entrada del ritual"""
    
    # ================= INIT =================
    pygame.init()
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    BASE = min(WIDTH, HEIGHT)
    
    # Pantalla completa
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("EL RITO DEL AZAR")
    clock = pygame.time.Clock()
    
    # Motor ritual
    engine = RitualEngine(screen)
    
    # ================= FUENTES =================
    font_title = pygame.font.SysFont("arial", int(BASE * Scale.TITLE_FONT), bold=True)
    font_btn = pygame.font.SysFont("arial", int(BASE * Scale.BUTTON_FONT), bold=True)
    
    # ================= BOTONES =================
    bw = BASE * Scale.BUTTON_WIDTH
    bh = BASE * Scale.BUTTON_HEIGHT
    spacing = bh + (BASE * Scale.BUTTON_SPACING)
    start_y = HEIGHT * 0.35
    
    buttons = [
        pygame.Rect(WIDTH//2 - bw//2, start_y, bw, bh),
        pygame.Rect(WIDTH//2 - bw//2, start_y + spacing, bw, bh),
        pygame.Rect(WIDTH//2 - bw//2, start_y + spacing * 2, bw, bh),
        pygame.Rect(WIDTH//2 - bw//2, start_y + spacing * 3, bw, bh),
    ]
    
    button_data = [
        ("El Rito", Colors.PURPLE, el_rito.run),
        ("Fructis Noctis", Colors.GOLD, fructis_noctis.run),
        ("Multiverso", Colors.ACCENT, multiverso.run),
        ("Revelatio", Colors.CYAN, revelatio.run),
    ]
    
    # ================= MENU LOOP =================
    while True:
        mx, my = pygame.mouse.get_pos()
        engine.draw_stars()
        
        # Input
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                for i, (rect, (_, _, callback)) in enumerate(zip(buttons, button_data)):
                    if rect.collidepoint(e.pos) and callback:
                        pygame.event.clear()
                        callback(screen, clock)
        
        # ================= TÍTULO FLOTANTE =================
        t_str = "EL RITO DEL AZAR"
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 8
        
        # Sombra
        t_glow = font_title.render(t_str, True, (40, 10, 20))
        screen.blit(
            t_glow,
            t_glow.get_rect(center=(WIDTH//2 + 3, HEIGHT*0.18 + 3 + pulse))
        )
        
        # Texto principal
        t_surf = font_title.render(t_str, True, Colors.WHITE)
        screen.blit(
            t_surf,
            t_surf.get_rect(center=(WIDTH//2, HEIGHT*0.18 + pulse))
        )
        
        # ================= BOTONES =================
        for rect, (label, color, _) in zip(buttons, button_data):
            engine.draw_styled_button(
                rect,
                label,
                font_btn,
                color,
                hover=rect.collidepoint(mx, my)
            )
        
        pygame.display.flip()
        clock.tick(Timing.FPS)


if __name__ == "__main__":
    main()
