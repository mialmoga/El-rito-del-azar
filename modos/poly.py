import pygame, random, math, time

#================= CONFIG =================

FPS = 120
CELL_COUNT = 900
ROTATE_BASE = 0.02
ROTATE_SPIN = 0.12
ROTATE_SUDDEN = 0.35
SPIN_TIME = 1.4
PARTICLE_SPEED = 0.03
ABSORB_SPEED = 0.08

DICE_FACES = [4, 6, 8, 10, 12, 20]
ROUND_OPTIONS = list(range(1, 11))

PALETTE = [
(210, 30, 90), (255, 100, 10), (255, 180, 50),
(50, 210, 110), (90, 210, 210), (30, 160, 240), (160, 50, 210)
]

def run(screen, clock):
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    BASE = min(WIDTH, HEIGHT)
    SCALE = int(BASE * 0.7)

    font_big = pygame.font.SysFont("arial", int(BASE*0.07), bold=True)
    font_mid = pygame.font.SysFont("arial", int(BASE*0.045), bold=True)
    font_small = pygame.font.SysFont("arial", int(BASE*0.035))
    cells = [[random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)] for _ in range(CELL_COUNT)]
    particles = []
    bg_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(2, 6), random.randint(1, 3)] for _ in range(120)]

    def project(x, y, z):
        f = SCALE / (z + 2)
        return WIDTH//2 + int(x*f), HEIGHT//2 + int(y*f)

    def rotate_cells(speed):
        ct, st = math.cos(speed), math.sin(speed)
        for c in cells:
            x, z = c[0], c[2]
            c[0], c[2] = x*ct - z*st, x*st + z*ct

    def draw_back_arrow():
        size = int(BASE * 0.05)
        rect = pygame.Rect(BASE * 0.05, BASE * 0.05, size, size)
        color = (255, 215, 0) if rect.collidepoint(pygame.mouse.get_pos()) else (245, 245, 245)
        pygame.draw.lines(screen, color, False, [(rect.right, rect.top), (rect.left, rect.centery), (rect.right, rect.bottom)], 5)
        return rect

    def spawn_particles(n, base_color):
        for _ in range(n):
            jitter = lambda c: max(0, min(255, c + random.randint(-30,30)))
            col = (jitter(base_color[0]), jitter(base_color[1]), jitter(base_color[2]))
            particles.append([random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1), col])

    def update_particles(absorb=False):
        alive = []
        for x, y, z, col in particles:
            if absorb:
                x, y, z = x*(1-ABSORB_SPEED), y*(1-ABSORB_SPEED), z*(1-ABSORB_SPEED)
                if abs(x)+abs(y)+abs(z) < 0.01: continue
            else:
                x += random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
                y += random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
                z += random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
            alive.append([x,y,z,col])
        particles[:] = alive

    def draw_ritual_bg(speed_mult=1.0):
        bg_col = (20, 0, 10) if sudden_death else (5, 5, 12)
        screen.fill(bg_col)
        for s in bg_stars:
            s[1] -= s[2] * speed_mult
            if s[1] < 0: s[1] = HEIGHT; s[0] = random.randint(0, WIDTH)
            pygame.draw.line(screen, (70, 70, 120), (s[0], s[1]), (s[0], s[1] + 10), 1)
            pygame.draw.circle(screen, (150, 150, 200), (int(s[0]), int(s[1])), s[3])

    def draw_world(dim=False):
        draw_ritual_bg(speed_mult=2.5 if state == SPIN else 1.0)
        for c in cells:
            sx, sy = project(*c)
            col = (60, 60, 60) if dim else (120, 120, 180)
            if sudden_death and not dim: col = (255, 50, 50)
            pygame.draw.circle(screen, col, (sx, sy), 3)
        for x, y, z, col in particles:
            sx, sy = project(x, y, z)
            p_col = col if (not sudden_death or random.random() > 0.5) else (255, 0, 0)
            pygame.draw.circle(screen, p_col, (sx, sy), 5)
            pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 2)

    def draw_styled_button(rect, text, color, hover=False):
        main_col = color if hover else (20, 20, 30)
        pygame.draw.rect(screen, main_col, rect, border_radius=18)
        pygame.draw.rect(screen, color, rect, 3, border_radius=18)
        t = font_mid.render(text, True, (255, 255, 255) if hover else color)
        screen.blit(t, t.get_rect(center=rect.center))

    def draw_poly_dice(value, color, shake=0):
        SIZE = int(BASE * 0.4)
        sx, sy = random.randint(-shake, shake), random.randint(-shake, shake)
        cx, cy = WIDTH//2 + sx, HEIGHT//2 + sy
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
        txt = font_val.render(str(value), True, (255, 255, 255))
        shd = font_val.render(str(value), True, (0, 0, 0))
        screen.blit(shd, shd.get_rect(center=(cx+2, cy+2)))
        screen.blit(txt, txt.get_rect(center=(cx, cy)))

    # ================= ESTADOS =================
    SELECT_PLAYERS, SELECT_DICE, SELECT_ROUNDS, IDLE, SPIN, COLLAPSE, REVEAL, END = range(8)
    state, players, scores = SELECT_PLAYERS, [], {}
    current_player, current_round, result_value, sudden_death, t0 = 0, 1, None, False, 0
    dice_faces, rounds_total = 6, 10

    def reset_match():
        nonlocal scores, current_player, current_round, sudden_death, state, particles
        scores = {p[0]:0 for p in players}; current_player, current_round = 0, 1
        sudden_death, state, particles = False, IDLE, []

    while True:
        mx, my = pygame.mouse.get_pos()
        rotate_cells(ROTATE_SUDDEN if sudden_death and state==SPIN else ROTATE_SPIN if state==SPIN else ROTATE_BASE)
        update_particles(absorb=(state==COLLAPSE))
        draw_world(dim=(state in (COLLAPSE, REVEAL, SELECT_PLAYERS, SELECT_DICE, SELECT_ROUNDS, END)))

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if draw_back_arrow().collidepoint(e.pos): return
                if state == SELECT_PLAYERS:
                    for i in range(7):
                        r = pygame.Rect(WIDTH//2 - BASE*0.3, HEIGHT*0.35 + i*BASE*0.08, BASE*0.6, BASE*0.07)
                        if r.collidepoint(e.pos):
                            players = [("P"+str(j+1), PALETTE[j]) for j in range(i+1)]; state = SELECT_DICE
                elif state == SELECT_DICE:
                    for i, f in enumerate(DICE_FACES):
                        r = pygame.Rect(WIDTH//2 - BASE*0.2, HEIGHT*0.25 + i*BASE*0.09, BASE*0.4, BASE*0.08)
                        if r.collidepoint(e.pos):
                            dice_faces = f; state = SELECT_ROUNDS
                elif state == SELECT_ROUNDS:
                    for i, rn in enumerate(ROUND_OPTIONS):
                        r = pygame.Rect(WIDTH//2 - BASE*0.2, HEIGHT*0.15 + i*BASE*0.075, BASE*0.4, BASE*0.065)
                        if r.collidepoint(e.pos):
                            rounds_total = rn; reset_match()
                elif state == IDLE:
                    spawn_particles(80, players[current_player][1]); t0 = time.time(); state = SPIN
                elif state == REVEAL:
                    # AVANCE MANUAL POR CLIC
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
                    r_a = pygame.Rect(WIDTH//2-BASE*0.25, HEIGHT*0.82, BASE*0.23, BASE*0.1)
                    r_b = pygame.Rect(WIDTH//2+BASE*0.02, HEIGHT*0.82, BASE*0.23, BASE*0.1)
                    if r_a.collidepoint(mx,my): reset_match()
                    elif r_b.collidepoint(mx,my): return

        if state == SELECT_PLAYERS:
            txt = font_big.render("¿CUÁNTOS?", True, (255, 255, 255))
            screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT*0.2))
            for i in range(7):
                r = pygame.Rect(WIDTH//2-BASE*0.3, HEIGHT*0.35+i*BASE*0.08, BASE*0.6, BASE*0.07)
                hover = r.collidepoint(mx, my)
                for j in range(i+1):
                    off = (j-i/2)*(BASE*0.06)
                    pygame.draw.circle(screen, PALETTE[j], (int(WIDTH//2+off), int(r.centery)), int(BASE*0.025 if hover else BASE*0.015))

        elif state == SELECT_DICE:
            txt = font_big.render("CARAS", True, (255, 255, 255))
            screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT*0.12))
            for i, f in enumerate(DICE_FACES):
                r = pygame.Rect(WIDTH//2-BASE*0.2, HEIGHT*0.25+i*BASE*0.09, BASE*0.4, BASE*0.08)
                draw_styled_button(r, f"D{f}", (255,180,50), r.collidepoint(mx,my))

        elif state == SELECT_ROUNDS:
            txt = font_big.render("RONDAS", True, (255, 255, 255))
            screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT*0.05))
            for i, rn in enumerate(ROUND_OPTIONS):
                r = pygame.Rect(WIDTH//2-BASE*0.2, HEIGHT*0.15+i*BASE*0.075, BASE*0.4, BASE*0.065)
                draw_styled_button(r, f"{rn} Rondas", (50,210,110), r.collidepoint(mx,my))

        elif state in (IDLE, SPIN, COLLAPSE, REVEAL):
            p_name, p_col = players[current_player]
            
            # --- CONTADOR DE PUNTOS ESQUINA (De Código A) ---
            score_box = pygame.Rect(WIDTH - BASE*0.25, BASE*0.03, BASE*0.22, BASE*0.08)
            pygame.draw.rect(screen, (20, 20, 30), score_box, border_radius=10)
            pygame.draw.rect(screen, p_col, score_box, 2, border_radius=10)
            s_txt = font_small.render(f"{scores.get(p_name, 0)} pts", True, (255, 255, 255))
            screen.blit(s_txt, s_txt.get_rect(center=score_box.center))
            
            pygame.draw.circle(screen, p_col, (WIDTH//2, HEIGHT*0.07), int(BASE*0.03))
            pygame.draw.circle(screen, (255,255,255), (WIDTH//2, HEIGHT*0.07), int(BASE*0.035), 2)
            
            if sudden_death:
                l = font_big.render("MUERTE SÚBITA", True, (255,50,50))
                screen.blit(l, l.get_rect(center=(WIDTH//2, HEIGHT*0.15+math.sin(time.time()*10)*5)))
            else:
                txt = font_small.render(f"Ronda {current_round}/{rounds_total}", True, (200,200,200))
                screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT*0.12))

            if state == SPIN and time.time()-t0 > SPIN_TIME:
                state = COLLAPSE
            if state == COLLAPSE and not particles:
                result_value = random.randint(1, dice_faces)
                scores[players[current_player][0]] += result_value
                spawn_particles(30, (255,255,255))
                t0 = time.time()
                state = REVEAL
            if state == REVEAL:
                # TEMBLOR LIMITADO A 1.2 SEGUNDOS
                current_shake = 5 if (time.time() - t0 < 1.2) else 0
                draw_poly_dice(result_value, p_col, shake=current_shake)
                
                # PROMPT DE CONTINUAR (De Código A)
                tp = font_small.render("Toca para continuar...", True, (150, 150, 150))
                screen.blit(tp, (WIDTH//2 - tp.get_width()//2, HEIGHT * 0.9))

        elif state == END:
            winner_n = max(scores, key=scores.get); win_col = next(p[1] for p in players if p[0] == winner_n)
            pygame.draw.circle(screen, win_col, (WIDTH//2, HEIGHT*0.35), int(BASE*0.12))
            txt_w = font_big.render("¡VICTORIA!", True, (255, 215, 0))
            screen.blit(txt_w, (WIDTH//2-txt_w.get_width()//2, HEIGHT*0.18))
            leaderboard = sorted(players, key=lambda p: scores[p[0]], reverse=True)
            for i, (p_n, p_c) in enumerate(leaderboard):
                curr_y = HEIGHT*0.52 + (i * BASE * 0.045)
                pygame.draw.circle(screen, p_c, (int(WIDTH//2-BASE*0.12), int(curr_y)), 6)
                txt_s = font_small.render(f"{p_n}: {scores[p_n]} pts", True, (220,220,220))
                screen.blit(txt_s, (WIDTH//2-BASE*0.08, curr_y-txt_s.get_height()//2))
            r_a = pygame.Rect(WIDTH//2-BASE*0.25, HEIGHT*0.82, BASE*0.23, BASE*0.1)
            r_b = pygame.Rect(WIDTH//2+BASE*0.02, HEIGHT*0.82, BASE*0.23, BASE*0.1)
            draw_styled_button(r_a, "¿OTRA?", (46,204,113), r_a.collidepoint(mx,my))
            draw_styled_button(r_b, "SALIR", (231,76,60), r_b.collidepoint(mx,my))

        draw_back_arrow()
        pygame.display.flip()
        clock.tick(FPS)
