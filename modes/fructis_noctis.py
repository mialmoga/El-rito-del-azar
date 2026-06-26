"""
🍎 FRUCTIS NOCTIS - Modo de Cartas con Frutas
Versión refactorizada manteniendo todos los momentos especiales.
"""

import pygame
import random
import time
import os

import sys
sys.path.insert(0, '/home/claude/ritual_refactor')

from core import (
    Colors, Physics, Timing, Scale, ModeConfig,
    RitualEngine, CARD_PALETTE, VALUE_TO_FILE
)


def run(screen, clock):
    """Ejecuta el ritual de las cartas frutales"""
    
    # ================= SETUP =================
    engine = RitualEngine(screen)
    
    # Configuración específica
    FORCE_SUDDEN_DEATH = ModeConfig.CARDS_SUDDEN_DEATH
    FORBIDDEN_FRUIT_ENABLED = ModeConfig.CARDS_FORBIDDEN_FRUIT_ENABLED
    
    # Fuentes
    font_big = pygame.font.SysFont("arial", int(engine.BASE * Scale.BIG_FONT), bold=True)
    font_mid = pygame.font.SysFont("arial", int(engine.BASE * Scale.MID_FONT), bold=True)
    font_small = pygame.font.SysFont("arial", int(engine.BASE * Scale.SMALL_FONT))
    font_joker = pygame.font.SysFont("georgia", int(engine.BASE * 0.050), italic=True, bold=True)
    
    # ================= MUNDO 3D =================
    cells = engine.create_cells()
    
    # ================= CARTAS =================
    card_images = {}
    art_path = os.path.join(os.path.dirname(__file__), "..", "assets", "art")
    C_WIDTH = int(engine.BASE * 0.45)
    C_HEIGHT = int((engine.BASE * 0.45) * (1306 / 825))
    RADIUS = int(C_WIDTH * 0.1)
    
    def load_art():
        """Carga las imágenes de frutas"""
        for v in list(range(1, 14)) + [20]:  # 1-13 + Joker
            name = VALUE_TO_FILE.get(v, str(v))
            path = os.path.join(art_path, f"{name}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (C_WIDTH, C_HEIGHT))
                
                # Esquinas redondeadas
                mask = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255), mask.get_rect(), border_radius=RADIUS)
                img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                
                card_images[v] = img
            except Exception as e:
                # Fallback: rectángulo simple
                f = pygame.Surface((C_WIDTH, C_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(f, (30, 30, 40), f.get_rect(), border_radius=RADIUS)
                card_images[v] = f
    
    load_art()
    
    def draw_styled_button(rect, text, color, hover=False):
        """Dibuja botón estilizado"""
        main_col = color if hover else (20, 20, 30)
        pygame.draw.rect(screen, main_col, rect, border_radius=18)
        pygame.draw.rect(screen, color, rect, 3, border_radius=18)
        t = font_mid.render(text, True, Colors.WHITE if hover else color)
        screen.blit(t, t.get_rect(center=rect.center))
    
    # ================= ESTADOS DEL JUEGO =================
    SELECT_PLAYERS, SELECT_ROUNDS, IDLE, SPIN, COLLAPSE, REVEAL, END = range(7)
    state = SELECT_PLAYERS
    
    # Estado del juego
    players = []  # Lista de (nombre, color)
    scores = {}
    current_player = 0
    current_round = 1
    rounds_total = 3
    result_value = None
    sudden_death = False
    winner_override = None
    t0 = 0
    
    # ================= LOOP PRINCIPAL =================
    while True:
        mx, my = pygame.mouse.get_pos()
        
        # ================= FONDO =================
        is_joker = (state == REVEAL and result_value == 20)
        speed_mult = 2.5 if state == SPIN else 1.0
        star_color = Colors.GOLD if is_joker else None
        engine.draw_stars(speed_mult=speed_mult, color_override=star_color)
        
        # ================= ROTACIÓN =================
        if sudden_death:
            rot_speed = Physics.ROTATE_SUDDEN_DEATH
        elif state == SPIN:
            rot_speed = Physics.ROTATE_SPIN
        else:
            rot_speed = Physics.ROTATE_BASE
        engine.rotate_cells(cells, rot_speed)
        
        # ================= COLOR DE JUGADOR ACTUAL =================
        if players and current_player < len(players):
            p_col = players[current_player][1]
            p_name = players[current_player][0]
        else:
            p_col = Colors.WHITE
            p_name = ""
        
        # ================= DIBUJAR CÉLULAS =================
        for c in cells:
            # Colapso hacia centro
            if state == COLLAPSE:
                f_abs = max(0.01, 1.0 - (time.time() - t0) * 2)
            else:
                f_abs = 1.0
            
            sx, sy = engine.project(c[0] * f_abs, c[1] * f_abs, c[2] * f_abs)
            
            # Color según estado
            if state in (SPIN, COLLAPSE, REVEAL):
                c_col = p_col
            else:
                c_col = (100, 100, 150)
            
            if sudden_death:
                c_col = Colors.RED
            
            pygame.draw.circle(screen, c_col, (sx, sy), 3)
        
        # ================= INPUT =================
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                # Botón volver
                if engine.draw_back_arrow().collidepoint(e.pos):
                    return
                
                # ===== SELECCIÓN DE JUGADORES =====
                if state == SELECT_PLAYERS:
                    for i in range(7):
                        r_area = pygame.Rect(
                            engine.WIDTH//2 - engine.BASE*0.3,
                            engine.HEIGHT*0.35 + i*engine.BASE*0.08,
                            engine.BASE*0.6,
                            engine.BASE*0.07
                        )
                        if r_area.collidepoint(e.pos):
                            players = [
                                (f"P{j+1}", CARD_PALETTE[j])
                                for j in range(i + 1)
                            ]
                            scores = {p[0]: 0 for p in players}
                            current_player = 0
                            state = SELECT_ROUNDS
                
                # ===== SELECCIÓN DE RONDAS =====
                elif state == SELECT_ROUNDS:
                    for i in range(1, 6):
                        r = pygame.Rect(
                            engine.WIDTH//2 - engine.BASE*0.2,
                            engine.HEIGHT*0.35 + (i-1)*engine.BASE*0.1,
                            engine.BASE*0.4,
                            engine.BASE*0.08
                        )
                        if r.collidepoint(e.pos):
                            rounds_total = i
                            state = IDLE
                
                # ===== INICIAR SPIN =====
                elif state == IDLE:
                    t0 = time.time()
                    state = SPIN
                
                # ===== CONTINUAR DESDE REVEAL =====
                elif state == REVEAL:
                    # Si es Joker, esperar animación
                    if result_value != 20 or (time.time() - t0 > 1.2):
                        current_player += 1
                        
                        # Fin de ronda
                        if current_player >= len(players) or winner_override:
                            if winner_override:
                                state = END
                            elif sudden_death:
                                # Filtrar ganadores de muerte súbita
                                current_player = 0
                                mx_s = max(scores.values())
                                winners = [p for p, s in scores.items() if s == mx_s]
                                
                                if len(winners) == 1:
                                    state = END
                                else:
                                    # Empate, otra ronda
                                    players = [p for p in players if p[0] in winners]
                                    scores = {p[0]: 0 for p in players}
                                    state = IDLE
                            
                            elif current_round >= rounds_total or FORCE_SUDDEN_DEATH:
                                # Determinar ganadores
                                mx_s = max(scores.values())
                                winners = [p for p, s in scores.items() if s == mx_s]
                                
                                if FORCE_SUDDEN_DEATH:
                                    winners_f = [p for p in players]
                                else:
                                    winners_f = [p for p in players if p[0] in winners]
                                
                                if len(winners_f) > 1:
                                    # MUERTE SÚBITA
                                    players = winners_f
                                    scores = {p[0]: 0 for p in players}
                                    current_player = 0
                                    sudden_death = True
                                    state = IDLE
                                else:
                                    state = END
                            else:
                                # Siguiente ronda
                                current_player = 0
                                current_round += 1
                                state = IDLE
                        else:
                            # Siguiente jugador
                            state = IDLE
                
                # ===== PANTALLA DE FIN =====
                elif state == END:
                    r_again = pygame.Rect(
                        engine.WIDTH//2 - engine.BASE*0.25,
                        engine.HEIGHT*0.82,
                        engine.BASE*0.23,
                        engine.BASE*0.1
                    )
                    r_back = pygame.Rect(
                        engine.WIDTH//2 + engine.BASE*0.02,
                        engine.HEIGHT*0.82,
                        engine.BASE*0.23,
                        engine.BASE*0.1
                    )
                    
                    if r_again.collidepoint(e.pos):
                        # Reiniciar
                        scores = {p[0]: 0 for p in players}
                        current_player = 0
                        current_round = 1
                        sudden_death = False
                        winner_override = None
                        state = IDLE
                    elif r_back.collidepoint(e.pos):
                        return
        
        # ================= RENDER =================
        
        # ===== SELECCIÓN DE JUGADORES =====
        if state == SELECT_PLAYERS:
            txt = font_big.render("¿CUÁNTOS?", True, Colors.WHITE)
            screen.blit(txt, (
                engine.WIDTH//2 - txt.get_width()//2,
                engine.HEIGHT*0.2
            ))
            
            for i in range(7):
                r_area = pygame.Rect(
                    engine.WIDTH//2 - engine.BASE*0.3,
                    engine.HEIGHT*0.35 + i*engine.BASE*0.08,
                    engine.BASE*0.6,
                    engine.BASE*0.07
                )
                hover = r_area.collidepoint(mx, my)
                
                # Dibujar círculos de colores
                for j in range(i + 1):
                    off_x = (j - i/2) * (engine.BASE*0.06)
                    radius = int(engine.BASE*0.025 if hover else engine.BASE*0.015)
                    pygame.draw.circle(
                        screen,
                        CARD_PALETTE[j],
                        (
                            int(engine.WIDTH//2 + off_x),
                            int(engine.HEIGHT*0.35 + i*engine.BASE*0.08 + engine.BASE*0.035)
                        ),
                        radius
                    )
        
        # ===== SELECCIÓN DE RONDAS =====
        elif state == SELECT_ROUNDS:
            txt = font_big.render("RONDAS", True, Colors.WHITE)
            screen.blit(txt, (
                engine.WIDTH//2 - txt.get_width()//2,
                engine.HEIGHT*0.2
            ))
            
            for i in range(1, 6):
                r = pygame.Rect(
                    engine.WIDTH//2 - engine.BASE*0.2,
                    engine.HEIGHT*0.35 + (i-1)*engine.BASE*0.1,
                    engine.BASE*0.4,
                    engine.BASE*0.08
                )
                draw_styled_button(
                    r,
                    f"{i} Rondas",
                    (255, 180, 50),
                    r.collidepoint(mx, my)
                )
        
        # ===== JUEGO EN PROGRESO =====
        elif state in (IDLE, SPIN, COLLAPSE, REVEAL):
            # Puntaje esquina superior derecha
            score_box = pygame.Rect(
                engine.WIDTH - engine.BASE*0.25,
                engine.BASE*0.03,
                engine.BASE*0.22,
                engine.BASE*0.08
            )
            pygame.draw.rect(screen, (20, 20, 30), score_box, border_radius=10)
            pygame.draw.rect(screen, p_col, score_box, 2, border_radius=10)
            s_txt = font_small.render(f"{scores.get(p_name, 0)} pts", True, Colors.WHITE)
            screen.blit(s_txt, s_txt.get_rect(center=score_box.center))
            
            # Indicador de jugador actual (círculo arriba)
            pygame.draw.circle(
                screen,
                p_col,
                (engine.WIDTH//2, int(engine.HEIGHT*0.07)),
                int(engine.BASE*0.03)
            )
            pygame.draw.circle(
                screen,
                Colors.WHITE,
                (engine.WIDTH//2, int(engine.HEIGHT*0.07)),
                int(engine.BASE*0.035),
                2
            )
            
            # Indicador de ronda o muerte súbita
            if not sudden_death:
                txt_round = font_small.render(
                    f"Ronda {current_round} / {rounds_total}",
                    True,
                    (200, 200, 200)
                )
                screen.blit(txt_round, (
                    engine.WIDTH//2 - txt_round.get_width()//2,
                    engine.HEIGHT*0.12
                ))
            else:
                lbl = font_mid.render("MUERTE SÚBITA", True, Colors.RED)
                screen.blit(lbl, (
                    engine.WIDTH//2 - lbl.get_width()//2,
                    engine.HEIGHT*0.13
                ))
            
            # ===== TRANSICIONES DE ESTADO =====
            if state == SPIN and time.time() - t0 > Timing.SPIN_DURATION_CARDS:
                t0 = time.time()
                state = COLLAPSE
            
            if state == COLLAPSE and time.time() - t0 > 0.5:
                # Determinar carta
                if FORBIDDEN_FRUIT_ENABLED and random.random() < 0.08:
                    result_value = 20  # Joker
                else:
                    result_value = random.randint(1, 13)
                
                # Puntaje
                score_to_add = 14 if result_value == 1 else result_value
                
                # Joker en muerte súbita = victoria instantánea
                if sudden_death and result_value == 20:
                    winner_override = players[current_player][0]
                
                scores[p_name] += score_to_add
                t0 = time.time()
                state = REVEAL
            
            # ===== MOSTRAR CARTA =====
            if state == REVEAL:
                is_joker = (result_value == 20)
                
                # Shake effect
                shk = 0
                if is_joker and (time.time() - t0 < 1.2):
                    shk = 15  # Shake intenso para Joker
                elif sudden_death:
                    shk = 8
                
                # Posición de carta
                x = engine.WIDTH//2 - C_WIDTH//2
                y = engine.HEIGHT//2 - C_HEIGHT//2
                
                # Borde dorado para Joker
                border_col = Colors.GOLD if is_joker else p_col
                pygame.draw.rect(
                    screen,
                    border_col,
                    (x-8, y-8, C_WIDTH+16, C_HEIGHT+16),
                    width=5,
                    border_radius=RADIUS+8
                )
                
                # Carta con shake
                screen.blit(
                    card_images[result_value],
                    (
                        x + random.randint(-shk, shk),
                        y + random.randint(-shk, shk)
                    )
                )
                
                # Texto especial para Joker
                if is_joker:
                    tj = font_joker.render("FORBIDDEN FRUIT", True, Colors.GOLD)
                    screen.blit(tj, tj.get_rect(center=(
                        engine.WIDTH//2,
                        y + C_HEIGHT + engine.BASE*0.08
                    )))
                
                # Prompt para continuar
                prompt_txt = ""
                if not is_joker or time.time() - t0 > 1.2:
                    prompt_txt = "Toca para continuar..."
                
                if prompt_txt:
                    tp = font_small.render(prompt_txt, True, (150, 150, 150))
                    screen.blit(tp, (
                        engine.WIDTH//2 - tp.get_width()//2,
                        engine.HEIGHT * 0.9
                    ))
        
        # ===== PANTALLA DE FIN =====
        elif state == END:
            # Determinar ganador
            win_n = winner_override if winner_override else max(scores, key=scores.get)
            win_col = next(p[1] for p in players if p[0] == win_n)
            
            # Círculo grande de victoria
            pygame.draw.circle(
                screen,
                win_col,
                (engine.WIDTH//2, int(engine.HEIGHT*0.40)),
                int(engine.BASE*0.12)
            )
            pygame.draw.circle(
                screen,
                Colors.GOLD,
                (engine.WIDTH//2, int(engine.HEIGHT*0.40)),
                int(engine.BASE*0.13),
                4
            )
            
            # Título
            txt_w = font_big.render("¡VICTORIA!", True, Colors.GOLD)
            screen.blit(txt_w, (
                engine.WIDTH//2 - txt_w.get_width()//2,
                engine.HEIGHT*0.20
            ))
            
            # Leaderboard
            leaderboard = []
            for p_name, p_color in players:
                leaderboard.append((p_name, p_color, scores[p_name]))
            leaderboard.sort(key=lambda x: x[2], reverse=True)
            
            start_y = engine.HEIGHT * 0.55
            for i, (p_name, p_color, p_score) in enumerate(leaderboard):
                curr_y = start_y + (i * engine.BASE * 0.04)
                dot_x = engine.WIDTH // 2 - engine.BASE * 0.12
                
                # Dot de color
                pygame.draw.circle(
                    screen,
                    p_color,
                    (int(dot_x), int(curr_y)),
                    int(engine.BASE * 0.01)
                )
                
                # Texto
                t_col = Colors.GOLD if p_name == win_n else (220, 220, 220)
                txt_line = font_small.render(f"{p_name}: {p_score} pts", True, t_col)
                screen.blit(txt_line, (
                    dot_x + engine.BASE * 0.03,
                    curr_y - txt_line.get_height()//2
                ))
            
            # Botones
            r_again = pygame.Rect(
                engine.WIDTH//2 - engine.BASE*0.25,
                engine.HEIGHT*0.82,
                engine.BASE*0.23,
                engine.BASE*0.1
            )
            r_back = pygame.Rect(
                engine.WIDTH//2 + engine.BASE*0.02,
                engine.HEIGHT*0.82,
                engine.BASE*0.23,
                engine.BASE*0.1
            )
            draw_styled_button(r_again, "¿OTRA?", (46, 204, 113), r_again.collidepoint(mx, my))
            draw_styled_button(r_back, "SALIR", (231, 76, 60), r_back.collidepoint(mx, my))
        
        # Flecha de retorno siempre visible
        engine.draw_back_arrow()
        
        pygame.display.flip()
        clock.tick(Timing.FPS)
