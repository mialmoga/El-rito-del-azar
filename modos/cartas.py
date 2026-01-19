import pygame, random, math, time, os

# ================= CONFIG =================
FORCE_SUDDEN_DEATH = False 
FPS = 120
CELL_COUNT = 900
ROTATE_BASE = 0.02
ROTATE_SPIN = 0.12
ROTATE_SUDDEN = 0.35   
SPIN_TIME = 1.4

PALETTE = [
    (210, 30, 90), (255, 100, 10), (255, 180, 50),
    (50, 210, 110), (90, 210, 210), (30, 160, 240), (160, 50, 210)
]

VALUE_TO_FILE = {1: "as", 11: "j", 12: "q", 13: "k", 20: "jk"}

def run(screen, clock):
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    BASE = min(WIDTH, HEIGHT)
    SCALE = int(BASE * 0.7)

    font_big   = pygame.font.SysFont("arial", int(BASE*0.07), bold=True)
    font_mid   = pygame.font.SysFont("arial", int(BASE*0.045), bold=True)
    font_small = pygame.font.SysFont("arial", int(BASE*0.035))
    font_joker = pygame.font.SysFont("georgia", int(BASE*0.050), italic=True, bold=True)

    cells = [[random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)] for _ in range(CELL_COUNT)]
    bg_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(2, 6), random.randint(1, 3)] for _ in range(120)]

    def project(x, y, z, factor=1.0):
        f = (SCALE * factor) / (z + 2)
        return WIDTH//2 + int(x*f), HEIGHT//2 + int(y*f)

    def rotate_cells(speed):
        ct, st = math.cos(speed), math.sin(speed)
        for c in cells:
            x, z = c[0], c[2]; c[0] = x*ct - z*st; c[2] = x*st + z*ct

    def draw_bg_stars(speed_mult=1.0, is_joker=False):
        screen.fill((5, 5, 12))
        star_col = (255, 215, 0) if is_joker else (150, 150, 200)
        trail_col = (100, 100, 150) if not is_joker else (180, 150, 50)
        for s in bg_stars:
            s[1] -= s[2] * speed_mult
            if s[1] < 0: 
                s[1] = HEIGHT
                s[0] = random.randint(0, WIDTH)
            pygame.draw.line(screen, trail_col, (s[0], s[1]), (s[0], s[1] + 12), 1)
            pygame.draw.circle(screen, star_col, (int(s[0]), int(s[1])), s[3])

    # --- NUEVA FUNCIÓN: FLECHA DE REGRESO ---
    def draw_back_arrow():
        size = int(BASE * 0.05)
        rect = pygame.Rect(BASE * 0.05, BASE * 0.05, size, size)
        color = (255, 215, 0) if rect.collidepoint(pygame.mouse.get_pos()) else (245, 245, 245)
        pygame.draw.lines(screen, color, False, [
            (rect.right, rect.top), (rect.left, rect.centery), (rect.right, rect.bottom)
        ], 5)
        return rect

    card_images = {}
    art_path = os.path.join(os.path.dirname(__file__), "art")
    C_WIDTH, C_HEIGHT = int(BASE * 0.45), int((BASE * 0.45) * (1306 / 825))
    RADIUS = int(C_WIDTH * 0.1)

    def load_art():
        for v in list(range(1, 14)) + [20]:
            name = VALUE_TO_FILE.get(v, str(v))
            path = os.path.join(art_path, f"{name}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (C_WIDTH, C_HEIGHT))
                mask = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255), mask.get_rect(), border_radius=RADIUS)
                img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                card_images[v] = img
            except:
                f = pygame.Surface((C_WIDTH, C_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(f, (30, 30, 40), f.get_rect(), border_radius=RADIUS); card_images[v] = f
    load_art()

    def draw_styled_button(rect, text, color, hover=False):
        main_col = color if hover else (20, 20, 30)
        pygame.draw.rect(screen, main_col, rect, border_radius=18)
        pygame.draw.rect(screen, color, rect, 3, border_radius=18)
        t = font_mid.render(text, True, (255, 255, 255) if hover else color)
        screen.blit(t, t.get_rect(center=rect.center))

    # ================= ESTADOS =================
    SELECT_PLAYERS, SELECT_ROUNDS, IDLE, SPIN, COLLAPSE, REVEAL, END = range(7)
    state = SELECT_PLAYERS
    players, scores = [], {}
    current_player, current_round, rounds_total = 0, 1, 3
    result_value, sudden_death, t0 = None, False, 0
    winner_override = None

    while True:
        mx, my = pygame.mouse.get_pos()
        draw_bg_stars(speed_mult=2.5 if state == SPIN else 1.0, is_joker=(state == REVEAL and result_value == 20))
        
        rot_speed = ROTATE_SUDDEN if sudden_death else (ROTATE_SPIN if state == SPIN else ROTATE_BASE)
        rotate_cells(rot_speed)
        
        if players and current_player < len(players):
            p_col = players[current_player][1]
            p_name = players[current_player][0]
        else:
            p_col = (255, 255, 255)
            p_name = ""

        for c in cells:
            f_abs = max(0.01, 1.0 - (time.time()-t0)*2) if state == COLLAPSE else 1.0
            sx, sy = project(c[0]*f_abs, c[1]*f_abs, c[2]*f_abs)
            c_col = p_col if state in (SPIN, COLLAPSE, REVEAL) else (100, 100, 150)
            if sudden_death: c_col = (255, 50, 50)
            pygame.draw.circle(screen, c_col, (sx, sy), 3)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.MOUSEBUTTONDOWN:
                # Si toca la flecha, sale al menú principal
                if draw_back_arrow().collidepoint(e.pos): return

                if state == SELECT_PLAYERS:
                    for i in range(7):
                        r_area = pygame.Rect(WIDTH//2 - BASE*0.3, HEIGHT*0.35 + i*BASE*0.08, BASE*0.6, BASE*0.07)
                        if r_area.collidepoint(e.pos):
                            players = [("P"+str(j+1), PALETTE[j]) for j in range(i+1)]
                            scores = {p[0]:0 for p in players}
                            current_player = 0; state = SELECT_ROUNDS
                elif state == SELECT_ROUNDS:
                    for i in range(1, 6):
                        r = pygame.Rect(WIDTH//2 - BASE*0.2, HEIGHT*0.35 + (i-1)*BASE*0.1, BASE*0.4, BASE*0.08)
                        if r.collidepoint(e.pos): rounds_total = i; state = IDLE
                elif state == IDLE: t0 = time.time(); state = SPIN
                elif state == REVEAL:
                    if result_value != 20 or (time.time() - t0 > 1.2):
                        current_player += 1
                        if current_player >= len(players) or winner_override:
                            if winner_override: state = END
                            elif sudden_death:
                                current_player = 0; mx_s = max(scores.values())
                                winners = [p for p, s in scores.items() if s == mx_s]
                                if len(winners) == 1: state = END
                                else:
                                    players = [p for p in players if p[0] in winners]
                                    scores = {p[0]:0 for p in players}; state = IDLE
                            elif current_round >= rounds_total or FORCE_SUDDEN_DEATH:
                                mx_s = max(scores.values())
                                winners = [p for p, s in scores.items() if s == mx_s]
                                winners_f = [p for p in players] if FORCE_SUDDEN_DEATH else [p for p in players if p[0] in winners]
                                if len(winners_f) > 1:
                                    players = winners_f; scores = {p[0]:0 for p in players}
                                    current_player = 0; sudden_death = True; state = IDLE
                                else: state = END
                            else: current_player = 0; current_round += 1; state = IDLE
                        else: state = IDLE
                elif state == END:
                    r_again = pygame.Rect(WIDTH//2 - BASE*0.25, HEIGHT*0.82, BASE*0.23, BASE*0.1)
                    r_back = pygame.Rect(WIDTH//2 + BASE*0.02, HEIGHT*0.82, BASE*0.23, BASE*0.1)
                    if r_again.collidepoint(e.pos):
                        scores = {p[0]:0 for p in players}; current_player = 0
                        current_round = 1; sudden_death = False; winner_override = None
                        state = IDLE
                    elif r_back.collidepoint(e.pos): return

        if state == SELECT_PLAYERS:
            txt = font_big.render("¿CUÁNTOS?", True, (255, 255, 255))
            screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT*0.2))
            for i in range(7):
                r_area = pygame.Rect(WIDTH//2 - BASE*0.3, HEIGHT*0.35 + i*BASE*0.08, BASE*0.6, BASE*0.07)
                hover = r_area.collidepoint(mx, my)
                for j in range(i+1):
                    off_x = (j - i/2) * (BASE*0.06)
                    pygame.draw.circle(screen, PALETTE[j], (int(WIDTH//2 + off_x), int(HEIGHT*0.35 + i*BASE*0.08 + BASE*0.035)), int(BASE*0.025 if hover else BASE*0.015))

        elif state == SELECT_ROUNDS:
            txt = font_big.render("RONDAS", True, (255, 255, 255))
            screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT*0.2))
            for i in range(1, 6):
                r = pygame.Rect(WIDTH//2 - BASE*0.2, HEIGHT*0.35 + (i-1)*BASE*0.1, BASE*0.4, BASE*0.08)
                draw_styled_button(r, f"{i} Rondas", (255, 180, 50), r.collidepoint(mx, my))

        elif state in (IDLE, SPIN, COLLAPSE, REVEAL):
            # --- PUNTAJE ESQUINA SUPERIOR DERECHA ---
            score_box = pygame.Rect(WIDTH - BASE*0.25, BASE*0.03, BASE*0.22, BASE*0.08)
            pygame.draw.rect(screen, (20, 20, 30), score_box, border_radius=10)
            pygame.draw.rect(screen, p_col, score_box, 2, border_radius=10)
            s_txt = font_small.render(f"{scores.get(p_name, 0)} pts", True, (255, 255, 255))
            screen.blit(s_txt, s_txt.get_rect(center=score_box.center))

            pygame.draw.circle(screen, p_col, (WIDTH//2, HEIGHT*0.07), int(BASE*0.03))
            pygame.draw.circle(screen, (255,255,255), (WIDTH//2, HEIGHT*0.07), int(BASE*0.035), 2)
            
            if not sudden_death:
                txt_round = font_small.render(f"Ronda {current_round} / {rounds_total}", True, (200, 200, 200))
                screen.blit(txt_round, (WIDTH//2 - txt_round.get_width()//2, HEIGHT*0.12))
            else:
                lbl = font_mid.render("MUERTE SÚBITA", True, (255, 50, 50))
                screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, HEIGHT*0.13))

            if state == SPIN and time.time()-t0 > SPIN_TIME: t0 = time.time(); state = COLLAPSE
            
            if state == COLLAPSE and time.time()-t0 > 0.5:
                if random.random() < 0.08: result_value = 20
                else: result_value = random.randint(1, 13)
                score_to_add = 14 if result_value == 1 else result_value
                if sudden_death and result_value == 20: winner_override = players[current_player][0]
                scores[p_name] += score_to_add
                t0 = time.time(); state = REVEAL
            
            if state == REVEAL:
                is_joker = (result_value == 20)
                shk = 0
                if is_joker and (time.time() - t0 < 1.2): shk = 15
                elif sudden_death: shk = 8
                
                x, y = WIDTH//2 - C_WIDTH//2, HEIGHT//2 - C_HEIGHT//2
                border_col = (255, 215, 0) if is_joker else p_col
                pygame.draw.rect(screen, border_col, (x-8, y-8, C_WIDTH+16, C_HEIGHT+16), width=5, border_radius=RADIUS+8)
                screen.blit(card_images[result_value], (x + random.randint(-shk,shk), y + random.randint(-shk,shk)))
                
                if is_joker:
                    tj = font_joker.render("FORBIDDEN FRUIT", True, (255, 215, 0))
                    screen.blit(tj, tj.get_rect(center=(WIDTH//2, y + C_HEIGHT + BASE*0.08)))
                
                prompt_txt = "Toca para continuar..." if (not is_joker or time.time()-t0 > 1.2) else ""
                if prompt_txt:
                    tp = font_small.render(prompt_txt, True, (150, 150, 150))
                    screen.blit(tp, (WIDTH//2 - tp.get_width()//2, HEIGHT * 0.9))

        elif state == END:
            win_n = winner_override if winner_override else max(scores, key=scores.get)
            win_col = next(p[1] for p in players if p[0] == win_n)
            pygame.draw.circle(screen, win_col, (WIDTH//2, HEIGHT*0.40), int(BASE*0.12))
            pygame.draw.circle(screen, (255, 215, 0), (WIDTH//2, HEIGHT*0.40), int(BASE*0.13), 4)
            txt_w = font_big.render("¡VICTORIA!", True, (255, 215, 0))
            screen.blit(txt_w, (WIDTH//2-txt_w.get_width()//2, HEIGHT*0.20))
            
            leaderboard = []
            for p_name, p_color in players: leaderboard.append((p_name, p_color, scores[p_name]))
            leaderboard.sort(key=lambda x: x[2], reverse=True)

            start_y = HEIGHT * 0.55
            for i, (p_name, p_color, p_score) in enumerate(leaderboard):
                curr_y = start_y + (i * BASE * 0.04)
                dot_x = WIDTH // 2 - BASE * 0.12
                pygame.draw.circle(screen, p_color, (int(dot_x), int(curr_y)), int(BASE * 0.01))
                t_col = (255, 215, 0) if p_name == win_n else (220, 220, 220)
                txt_line = font_small.render(f"{p_name}: {p_score} pts", True, t_col)
                screen.blit(txt_line, (dot_x + BASE * 0.03, curr_y - txt_line.get_height()//2))

            r_again = pygame.Rect(WIDTH//2 - BASE*0.25, HEIGHT*0.82, BASE*0.23, BASE*0.1)
            r_back = pygame.Rect(WIDTH//2 + BASE*0.02, HEIGHT*0.82, BASE*0.23, BASE*0.1)
            draw_styled_button(r_again, "¿OTRA?", (46, 204, 113), r_again.collidepoint(mx,my))
            draw_styled_button(r_back, "SALIR", (231, 76, 60), r_back.collidepoint(mx,my))

        # Dibujar siempre la flecha encima de todo
        draw_back_arrow()
        pygame.display.flip(); clock.tick(FPS)