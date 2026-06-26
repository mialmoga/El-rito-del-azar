"""
🎲 EL RITO - Modo de Dados
Versión refactorizada manteniendo la experiencia exacta.
"""

import pygame
import random
import math
import time
import colorsys

import sys
sys.path.insert(0, '/home/claude/ritual_refactor')

from core import (
    Colors, Physics, Timing, Scale, ModeConfig,
    RitualEngine, ParticleSystem
)


def run(screen, clock):
    """Ejecuta el ritual de los dados"""
    
    # ================= SETUP =================
    engine = RitualEngine(screen)
    particles = ParticleSystem()
    
    # Configuración específica del modo
    FORCE_SUDDEN_DEATH = ModeConfig.DICE_SUDDEN_DEATH
    
    # Fuentes
    font_big = pygame.font.SysFont("arial", int(engine.BASE * Scale.BIG_FONT), bold=True)
    font_mid = pygame.font.SysFont("arial", int(engine.BASE * Scale.MID_FONT), bold=True)
    
    # ================= MUNDO 3D =================
    cells = engine.create_cells(with_color=True)
    
    spin_phase = 0.0
    color_locked = False
    collapse_start = None
    
    def update_colors(spinning=False, collapsing=False):
        """Actualiza colores de células según estado del ritual"""
        nonlocal spin_phase, color_locked
        
        if collapsing:
            color_locked = True
            
        if color_locked:
            for c in cells:
                c[3] = Colors.RED
            return
            
        if spinning:
            spin_phase += 0.01
            
        for c in cells:
            hue = c[4]
            if spinning:
                hue = (hue + spin_phase) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1)
            c[3] = [int(r * 255), int(g * 255), int(b * 255)]
    
    def draw_world(dim=False):
        """Dibuja el universo ritual"""
        # Fondo
        speed_mult = 2.5 if state == SPIN else 1.0
        engine.draw_stars(speed_mult=speed_mult)
        
        # Células del fondo
        for c in cells:
            sx, sy = engine.project(c[0], c[1], c[2])
            col = [max(0, val - 100) for val in c[3]] if dim else c[3]
            pygame.draw.circle(screen, col, (sx, sy), Scale.PARTICLE_BG)
        
        # Partículas del spin
        particles.draw(engine, size=Scale.PARTICLE_SPIN)
    
    def draw_die_face(value, center_x):
        """Dibuja cara de dado con valor dado"""
        SIZE = int(engine.BASE * 0.28)
        x = center_x - SIZE // 2
        y = engine.HEIGHT // 2 - SIZE // 2
        
        # Fondo del dado
        pygame.draw.rect(
            screen,
            (15, 15, 25),
            (x, y, SIZE, SIZE),
            border_radius=22
        )
        pygame.draw.rect(
            screen,
            Colors.GOLD,
            (x, y, SIZE, SIZE),
            4,
            border_radius=22
        )
        
        # Puntos
        o = SIZE // 4
        positions = {
            1: [(0, 0)],
            2: [(-o, -o), (o, o)],
            3: [(-o, -o), (0, 0), (o, o)],
            4: [(-o, -o), (o, -o), (-o, o), (o, o)],
            5: [(-o, -o), (o, -o), (0, 0), (-o, o), (o, o)],
            6: [(-o, -o), (o, -o), (-o, 0), (o, 0), (-o, o), (o, o)],
        }
        
        for dx, dy in positions[value]:
            pygame.draw.circle(
                screen,
                Colors.WHITE,
                (center_x + dx, engine.HEIGHT // 2 + dy),
                SIZE // 18
            )
    
    # ================= ESTADOS DEL RITUAL =================
    SELECT_COUNT, IDLE, SPIN, COLLAPSE, REVEAL = range(5)
    state = SELECT_COUNT
    dice_count = None
    results = []
    t0 = 0
    
    # ================= LOOP PRINCIPAL =================
    while True:
        mx, my = pygame.mouse.get_pos()
        
        # Input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                # Botón volver
                if engine.draw_back_arrow().collidepoint(mx, my):
                    return
                
                # Selección de cantidad de dados
                if state == SELECT_COUNT:
                    b1 = pygame.Rect(
                        engine.WIDTH * 0.2,
                        engine.HEIGHT * 0.45,
                        engine.BASE * 0.25,
                        engine.BASE * 0.12
                    )
                    b2 = pygame.Rect(
                        engine.WIDTH * 0.55,
                        engine.HEIGHT * 0.45,
                        engine.BASE * 0.25,
                        engine.BASE * 0.12
                    )
                    
                    if b1.collidepoint(mx, my):
                        dice_count = 1
                        state = IDLE
                    elif b2.collidepoint(mx, my):
                        dice_count = 2
                        state = IDLE
                
                # Iniciar spin
                elif state == IDLE:
                    particles.spawn(40, Colors.ORANGE)
                    t0 = time.time()
                    state = SPIN
                
                # Reiniciar desde resultado
                elif state == REVEAL:
                    color_locked = False
                    state = IDLE
        
        # ================= RENDER =================
        if state == SELECT_COUNT:
            engine.draw_stars()
            
            # Título
            txt = font_big.render("¿Cuántos dados?", True, Colors.WHITE)
            screen.blit(txt, (
                engine.WIDTH // 2 - txt.get_width() // 2,
                engine.HEIGHT * 0.33
            ))
            
            # Botones
            b1 = pygame.Rect(
                engine.WIDTH * 0.2,
                engine.HEIGHT * 0.45,
                engine.BASE * 0.25,
                engine.BASE * 0.12
            )
            b2 = pygame.Rect(
                engine.WIDTH * 0.55,
                engine.HEIGHT * 0.45,
                engine.BASE * 0.25,
                engine.BASE * 0.12
            )
            
            for b, txt in [(b1, "1"), (b2, "2")]:
                h = b.collidepoint(mx, my)
                pygame.draw.rect(
                    screen,
                    (30, 30, 50) if h else (15, 15, 30),
                    b,
                    border_radius=20
                )
                pygame.draw.rect(
                    screen,
                    Colors.GOLD if h else Colors.WHITE,
                    b,
                    2,
                    border_radius=20
                )
                t_surf = font_mid.render(txt, True, Colors.WHITE)
                screen.blit(t_surf, t_surf.get_rect(center=b.center))
        
        elif state == IDLE:
            engine.rotate_cells(cells, Physics.ROTATE_BASE)
            update_colors()
            particles.update()
            draw_world()
        
        elif state == SPIN:
            engine.rotate_cells(cells, Physics.ROTATE_SPIN)
            update_colors(spinning=True)
            particles.update()
            draw_world()
            
            if time.time() - t0 > Timing.SPIN_DURATION:
                collapse_start = time.time()
                state = COLLAPSE
        
        elif state == COLLAPSE:
            update_colors(collapsing=True)
            particles.update(absorb=True)
            draw_world(dim=True)
            
            if time.time() - collapse_start > Timing.COLLAPSE_DURATION:
                results = [random.randint(1, 6) for _ in range(dice_count)]
                state = REVEAL
        
        elif state == REVEAL:
            engine.rotate_cells(cells, Physics.ROTATE_BASE)
            update_colors()
            particles.update()
            draw_world(dim=True)
            
            # Dibujar dados
            if dice_count == 1:
                draw_die_face(results[0], engine.WIDTH // 2)
            else:
                offset = int(engine.BASE * 0.18)
                draw_die_face(results[0], engine.WIDTH // 2 - offset)
                draw_die_face(results[1], engine.WIDTH // 2 + offset)
        
        # Flecha de retorno siempre visible
        engine.draw_back_arrow()
        
        pygame.display.flip()
        clock.tick(Timing.FPS)
