"""🔮 MULTIVERSO - Dados Poliédricos"""
import pygame, random, time, math, sys
sys.path.insert(0, '/home/claude/ritual_refactor')
from core import Colors, Physics, Timing, Scale, ModeConfig, RitualEngine, ParticleSystem, CARD_PALETTE

DICE_FACES = [4, 6, 8, 10, 12, 20]
ROUND_OPTIONS = list(range(1, 11))

def run(screen, clock):
    engine = RitualEngine(screen)
    particles = ParticleSystem()
    font_big = pygame.font.SysFont("arial", int(engine.BASE * Scale.BIG_FONT), bold=True)
    font_mid = pygame.font.SysFont("arial", int(engine.BASE * Scale.MID_FONT), bold=True)
    font_small = pygame.font.SysFont("arial", int(engine.BASE * Scale.SMALL_FONT))
    cells = engine.create_cells()
    
    def draw_styled_button(rect, text, color, hover=False):
        main_col = color if hover else (20, 20, 30)
        pygame.draw.rect(screen, main_col, rect, border_radius=18)
        pygame.draw.rect(screen, color, rect, 3, border_radius=18)
        t = font_mid.render(text, True, Colors.WHITE if hover else color)
        screen.blit(t, t.get_rect(center=rect.center))
    
    def draw_poly_dice(value, color, shake=0):
        SIZE = int(engine.BASE * 0.4)
        sx, sy = random.randint(-shake, shake), random.randint(-shake, shake)
        cx, cy = engine.WIDTH//2 + sx, engine.HEIGHT//2 + sy
        t = time.time()
        ring_radius = SIZE * 0.75
        for i in range(12):
            angle = t * 1.5 + (i * (math.pi * 2 / 12))
            rx, ry = cx + math.cos(angle)*ring_radius, cy + math.sin(angle)*ring_radius
            pygame.draw.circle(screen, color, (int(rx), int(ry)), 3)
        pygame.draw.circle(screen, color, (cx, cy), int(ring_radius), 1)
        glow_size = int(SIZE * 0.55 + math.sin(t * 8) * 8)
        glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 40), (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (cx - glow_size, cy - glow_size), special_flags=pygame.BLEND_ADD)
        faint = [max(50, c // 2) for c in color]
        h_pts = [(cx + (SIZE//2)*math.cos(math.radians(60*i-90)), cy + (SIZE//2)*math.sin(math.radians(60*i-90))) for i in range(6)]
        t_pts = [(cx + (SIZE//2.2)*math.cos(math.radians(120*i-90)), cy + (SIZE//2.2)*math.sin(math.radians(120*i-90))) for i in range(3)]
        pygame.draw.polygon(screen, (10, 10, 15), h_pts)
        pygame.draw.polygon(screen, faint, t_pts, 2)
        pygame.draw.line(screen, faint, t_pts[0], h_pts[0], 2); pygame.draw.line(screen, faint, t_pts[0], h_pts[1], 1); pygame.draw.line(screen, faint, t_pts[0], h_pts[5], 1)
        pygame.draw.line(screen, faint, t_pts[1], h_pts[2], 2); pygame.draw.line(screen, faint, t_pts[1], h_pts[1], 1); pygame.draw.line(screen, faint, t_pts[1], h_pts[3], 1)
        pygame.draw.line(screen, faint, t_pts[2], h_pts[4], 2); pygame.draw.line(screen, faint, t_pts[2], h_pts[3], 1); pygame.draw.line(screen, faint, t_pts[2], h_pts[5], 1)
        pygame.draw.polygon(screen, color, h_pts, 4)
        font_val = pygame.font.SysFont("arial", int(SIZE*0.45), bold=True)
        txt = font_val.render(str(value), True, Colors.WHITE)
        shd = font_val.render(str(value), True, (0, 0, 0))
        screen.blit(shd, shd.get_rect(center=(cx+2, cy+2)))
        screen.blit(txt, txt.get_rect(center=(cx, cy)))
    
    SELECT_PLAYERS, SELECT_DICE, SELECT_ROUNDS, IDLE, SPIN, COLLAPSE, REVEAL, END = range(8)
    state, players, scores = SELECT_PLAYERS, [], {}
    current_player, current_round, result_value, sudden_death, t0 = 0, 1, None, False, 0
    dice_faces, rounds_total = 6, 10
    
    def reset_match():
        nonlocal scores, current_player, current_round, sudden_death, state
        scores = {p[0]:0 for p in players}; current_player, current_round = 0, 1
        sudden_death, state = False, IDLE
        particles.clear()
    
    while True:
        mx, my = pygame.mouse.get_pos()
        
        if sudden_death and state==SPIN:
            rot_speed = Physics.ROTATE_SUDDEN_DEATH
        elif state==SPIN:
            rot_speed = Physics.ROTATE_SPIN
        else:
            rot_speed = Physics.ROTATE_BASE
        engine.rotate_cells(cells, rot_speed)
        particles.update(absorb=(state==COLLAPSE))
        
        bg_col = (20, 0, 10) if sudden_death else Colors.BG_DARK
        screen.fill(bg_col)
        engine.draw_stars(speed_mult=2.5 if state == SPIN else 1.0)
        
        for c in cells:
            sx, sy = engine.project(*c)
            if state in (COLLAPSE, REVEAL, SELECT_PLAYERS, SELECT_DICE, SELECT_ROUNDS, END):
                col = (60, 60, 60)
            elif sudden_death:
                col = Colors.RED
            elif state == SPIN and players:
                col = players[current_player][1]  # Color del jugador actual
            else:
                col = (120, 120, 180)
            pygame.draw.circle(screen, col, (sx, sy), 3)
        
        for x, y, z, col in particles.particles:
            sx, sy = engine.project(x, y, z)
            p_col = col if (not sudden_death or random.random() > 0.5) else Colors.RED
            pygame.draw.circle(screen, p_col, (sx, sy), 5)
            pygame.draw.circle(screen, Colors.WHITE, (sx, sy), 2)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if engine.draw_back_arrow().collidepoint(e.pos): return
                if state == SELECT_PLAYERS:
                    for i in range(7):
                        r = pygame.Rect(engine.WIDTH//2 - engine.BASE*0.3, engine.HEIGHT*0.35 + i*engine.BASE*0.08, engine.BASE*0.6, engine.BASE*0.07)
                        if r.collidepoint(e.pos):
                            players = [(f"P{j+1}", CARD_PALETTE[j]) for j in range(i+1)]; state = SELECT_DICE
                elif state == SELECT_DICE:
                    for i, f in enumerate(DICE_FACES):
                        r = pygame.Rect(engine.WIDTH//2 - engine.BASE*0.2, engine.HEIGHT*0.25 + i*engine.BASE*0.09, engine.BASE*0.4, engine.BASE*0.08)
                        if r.collidepoint(e.pos): dice_faces = f; state = SELECT_ROUNDS
                elif state == SELECT_ROUNDS:
                    for i, rn in enumerate(ROUND_OPTIONS):
                        r = pygame.Rect(engine.WIDTH//2 - engine.BASE*0.2, engine.HEIGHT*0.15 + i*engine.BASE*0.075, engine.BASE*0.4, engine.BASE*0.065)
                        if r.collidepoint(e.pos): rounds_total = rn; reset_match()
                elif state == IDLE:
                    particles.spawn(80, players[current_player][1]); t0 = time.time(); state = SPIN
                elif state == REVEAL:
                    current_player += 1
                    if current_player >= len(players):
                        current_player = 0
                        if sudden_death:
                            mx_v = max(scores.values()); win = [p for p,s in scores.items() if s == mx_v]
                            if len(win) == 1: state = END
                            else: players = [p for p in players if p[0] in win]; scores = {p[0]:0 for p in players}; state = IDLE
                        else:
                            current_round += 1
                            if current_round > rounds_total:
                                mx_v = max(scores.values()); win = [p for p,s in scores.items() if s == mx_v]
                                if len(win) > 1:
                                    players = [p for p in players if p[0] in win]; scores = {p[0]:0 for p in players}; sudden_death = True; state = IDLE
                                else: state = END
                            else: state = IDLE
                    else: state = IDLE
                elif state == END:
                    r_a = pygame.Rect(engine.WIDTH//2-engine.BASE*0.25, engine.HEIGHT*0.82, engine.BASE*0.23, engine.BASE*0.1)
                    r_b = pygame.Rect(engine.WIDTH//2+engine.BASE*0.02, engine.HEIGHT*0.82, engine.BASE*0.23, engine.BASE*0.1)
                    if r_a.collidepoint(mx,my): reset_match()
                    elif r_b.collidepoint(mx,my): return
        
        if state == SELECT_PLAYERS:
            txt = font_big.render("¿CUÁNTOS?", True, Colors.WHITE)
            screen.blit(txt, (engine.WIDTH//2-txt.get_width()//2, engine.HEIGHT*0.2))
            for i in range(7):
                r = pygame.Rect(engine.WIDTH//2-engine.BASE*0.3, engine.HEIGHT*0.35+i*engine.BASE*0.08, engine.BASE*0.6, engine.BASE*0.07)
                hover = r.collidepoint(mx, my)
                for j in range(i+1):
                    off = (j-i/2)*(engine.BASE*0.06)
                    pygame.draw.circle(screen, CARD_PALETTE[j], (int(engine.WIDTH//2+off), int(r.centery)), int(engine.BASE*0.025 if hover else engine.BASE*0.015))
        
        elif state == SELECT_DICE:
            txt = font_big.render("CARAS", True, Colors.WHITE)
            screen.blit(txt, (engine.WIDTH//2-txt.get_width()//2, engine.HEIGHT*0.12))
            for i, f in enumerate(DICE_FACES):
                r = pygame.Rect(engine.WIDTH//2-engine.BASE*0.2, engine.HEIGHT*0.25+i*engine.BASE*0.09, engine.BASE*0.4, engine.BASE*0.08)
                draw_styled_button(r, f"D{f}", (255,180,50), r.collidepoint(mx,my))
        
        elif state == SELECT_ROUNDS:
            txt = font_big.render("RONDAS", True, Colors.WHITE)
            screen.blit(txt, (engine.WIDTH//2-txt.get_width()//2, engine.HEIGHT*0.05))
            for i, rn in enumerate(ROUND_OPTIONS):
                r = pygame.Rect(engine.WIDTH//2-engine.BASE*0.2, engine.HEIGHT*0.15+i*engine.BASE*0.075, engine.BASE*0.4, engine.BASE*0.065)
                draw_styled_button(r, f"{rn} Rondas", (50,210,110), r.collidepoint(mx,my))
        
        elif state in (IDLE, SPIN, COLLAPSE, REVEAL):
            p_name, p_col = players[current_player]
            score_box = pygame.Rect(engine.WIDTH - engine.BASE*0.25, engine.BASE*0.03, engine.BASE*0.22, engine.BASE*0.08)
            pygame.draw.rect(screen, (20, 20, 30), score_box, border_radius=10)
            pygame.draw.rect(screen, p_col, score_box, 2, border_radius=10)
            s_txt = font_small.render(f"{scores.get(p_name, 0)} pts", True, Colors.WHITE)
            screen.blit(s_txt, s_txt.get_rect(center=score_box.center))
            pygame.draw.circle(screen, p_col, (engine.WIDTH//2, int(engine.HEIGHT*0.07)), int(engine.BASE*0.03))
            pygame.draw.circle(screen, Colors.WHITE, (engine.WIDTH//2, int(engine.HEIGHT*0.07)), int(engine.BASE*0.035), 2)
            
            if sudden_death:
                l = font_big.render("MUERTE SÚBITA", True, Colors.RED)
                screen.blit(l, l.get_rect(center=(engine.WIDTH//2, engine.HEIGHT*0.15+math.sin(time.time()*10)*5)))
            else:
                txt = font_small.render(f"Ronda {current_round}/{rounds_total}", True, (200,200,200))
                screen.blit(txt, (engine.WIDTH//2-txt.get_width()//2, engine.HEIGHT*0.12))
            
            if state == SPIN and time.time()-t0 > Timing.SPIN_DURATION_CARDS:
                state = COLLAPSE
            if state == COLLAPSE and not particles.particles:
                result_value = random.randint(1, dice_faces)
                scores[players[current_player][0]] += result_value
                particles.spawn(30, Colors.WHITE)
                t0 = time.time()
                state = REVEAL
            if state == REVEAL:
                current_shake = 5 if (time.time() - t0 < 1.2) else 0
                draw_poly_dice(result_value, p_col, shake=current_shake)
                tp = font_small.render("Toca para continuar...", True, (150, 150, 150))
                screen.blit(tp, (engine.WIDTH//2 - tp.get_width()//2, engine.HEIGHT * 0.9))
        
        elif state == END:
            winner_n = max(scores, key=scores.get); win_col = next(p[1] for p in players if p[0] == winner_n)
            pygame.draw.circle(screen, win_col, (engine.WIDTH//2, int(engine.HEIGHT*0.35)), int(engine.BASE*0.12))
            txt_w = font_big.render("¡VICTORIA!", True, Colors.GOLD)
            screen.blit(txt_w, (engine.WIDTH//2-txt_w.get_width()//2, engine.HEIGHT*0.18))
            leaderboard = sorted(players, key=lambda p: scores[p[0]], reverse=True)
            for i, (p_n, p_c) in enumerate(leaderboard):
                curr_y = engine.HEIGHT*0.52 + (i * engine.BASE * 0.045)
                pygame.draw.circle(screen, p_c, (int(engine.WIDTH//2-engine.BASE*0.12), int(curr_y)), 6)
                txt_s = font_small.render(f"{p_n}: {scores[p_n]} pts", True, (220,220,220))
                screen.blit(txt_s, (engine.WIDTH//2-engine.BASE*0.08, curr_y-txt_s.get_height()//2))
            r_a = pygame.Rect(engine.WIDTH//2-engine.BASE*0.25, engine.HEIGHT*0.82, engine.BASE*0.23, engine.BASE*0.1)
            r_b = pygame.Rect(engine.WIDTH//2+engine.BASE*0.02, engine.HEIGHT*0.82, engine.BASE*0.23, engine.BASE*0.1)
            draw_styled_button(r_a, "¿OTRA?", (46,204,113), r_a.collidepoint(mx,my))
            draw_styled_button(r_b, "SALIR", (231,76,60), r_b.collidepoint(mx,my))
        
        engine.draw_back_arrow()
        pygame.display.flip()
        clock.tick(Timing.FPS)
