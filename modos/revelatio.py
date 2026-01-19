import pygame, random, math, time, os

# ================= CONFIG =================
PALETTE = [
    (210, 30, 90), (255, 100, 10), (255, 180, 50),
    (50, 210, 110), (90, 210, 210), (30, 160, 240)
]

def run(screen, clock):
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    BASE = min(WIDTH, HEIGHT)
    SCALE = int(BASE * 0.7)

    font_big = pygame.font.SysFont("arial", int(BASE*0.08), bold=True)
    font_mid = pygame.font.SysFont("arial", int(BASE*0.05), bold=True)
    
    cells = [[random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1)] for _ in range(900)]
    bg_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(2, 6), random.randint(1, 3)] for _ in range(120)]
    
    card_images = {}
    C_WIDTH = int(BASE * 0.22) 
    C_HEIGHT = int(C_WIDTH * (1306 / 825))
    art_path = os.path.join(os.path.dirname(__file__), "art")
    
    def load_art():
        for v in list(range(1, 14)) + [20]:
            name = {1:"as", 11:"j", 12:"q", 13:"k", 20:"jk"}.get(v, str(v))
            try:
                img = pygame.image.load(os.path.join(art_path, f"{name}.png")).convert_alpha()
                card_images[v] = pygame.transform.smoothscale(img, (C_WIDTH, C_HEIGHT))
            except:
                f = pygame.Surface((C_WIDTH, C_HEIGHT)); f.fill((20, 20, 40)); card_images[v] = f
    load_art()

    def get_power(val):
        if val == 20: return 99
        if val == 1:  return 14
        return val

    def draw_world(st_code, is_sd=False):
        screen.fill((5, 5, 12) if not is_sd else (40, 10, 10))
        for s in bg_stars:
            s[1] -= s[2] * (2.5 if st_code == 2 else 1.0)
            if s[1] < 0: s[1] = HEIGHT; s[0] = random.randint(0, WIDTH)
            pygame.draw.line(screen, (70, 70, 120), (s[0], s[1]), (s[0], s[1]+10), 1)
            pygame.draw.circle(screen, (150, 150, 200), (int(s[0]), int(s[1])), s[3])
        
        rot_speed = 0.02 if st_code != 2 else 0.12
        ct, st = math.cos(rot_speed), math.sin(rot_speed)
        for c in cells:
            x, z = c[0], c[2]; c[0], c[2] = x*ct - z*st, x*st + z*ct
            f = SCALE / (c[2] + 2); sx, sy = WIDTH//2 + int(c[0]*f), HEIGHT//2 + int(c[1]*f)
            pygame.draw.circle(screen, (255, 50, 50) if is_sd else (120, 120, 180), (sx, sy), 2)

    # --- FLECHA CORREGIDA A TAMAÑO 0.05 ---
    def draw_back_arrow():
        size = int(BASE * 0.05)
        rect = pygame.Rect(BASE * 0.05, BASE * 0.05, size, size)
        color = (255, 215, 0) if rect.collidepoint(pygame.mouse.get_pos()) else (255, 255, 255)
        pygame.draw.lines(screen, color, False, [
            (rect.right, rect.top), (rect.left, rect.centery), (rect.right, rect.bottom)
        ], 5)
        return rect

    # ================= ESTADOS =================
    SELECT, IDLE, SPIN, REVEAL = range(4)
    state = SELECT
    players = [] 
    original_players = []
    sudden_death = False

    while True:
        mx, my = pygame.mouse.get_pos()
        draw_world(state, sudden_death)
        back_rect = draw_back_arrow()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(e.pos): return
                
                if state == SELECT:
                    for i in range(6):
                        r_area = pygame.Rect(WIDTH//2 - BASE*0.3, HEIGHT*0.35 + i*BASE*0.08, BASE*0.6, BASE*0.07)
                        if r_area.collidepoint(e.pos):
                            players = [[f"P{j+1}", PALETTE[j], 0] for j in range(i+1)]
                            original_players = [p[:] for p in players]
                            state = IDLE
                elif state == IDLE: t0 = time.time(); state = SPIN
                elif state == REVEAL:
                    mv = max(get_power(p[2]) for p in players)
                    winners = [p for p in players if get_power(p[2]) == mv]
                    if len(winners) > 1:
                        players = winners; sudden_death = True; state = IDLE
                    else:
                        players = [p[:] for p in original_players]; sudden_death = False; state = IDLE

        if state == SELECT:
            txt = font_big.render("¿CUÁNTOS?", True, (255, 255, 255))
            screen.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT*0.2))
            
            for i in range(6):
                r_area = pygame.Rect(WIDTH//2 - BASE*0.3, HEIGHT*0.35 + i*BASE*0.08, BASE*0.6, BASE*0.07)
                hover = r_area.collidepoint(mx, my)
                for j in range(i+1):
                    off_x = (j - i/2) * (BASE*0.06)
                    orb_x = int(WIDTH//2 + off_x)
                    orb_y = int(HEIGHT*0.35 + i*BASE*0.08 + BASE*0.035)
                    rad = int(BASE*0.025 if hover else BASE*0.015)
                    pygame.draw.circle(screen, PALETTE[j], (orb_x, orb_y), rad)

        elif state == SPIN:
            if time.time() - t0 > 1.2:
                for p in players:
                    p[2] = 20 if random.random() < 0.08 else random.randint(1, 13)
                state = REVEAL

        elif state == REVEAL:
            cols = 3 if len(players) > 3 else len(players)
            rows = (len(players) + cols - 1) // cols
            max_p = max(get_power(p[2]) for p in players)
            winners_list = [p for p in players if get_power(p[2]) == max_p]
            
            if len(winners_list) == 1:
                win_col = winners_list[0][1]
                pulse = math.sin(time.time()*5)*6
                pygame.draw.circle(screen, win_col, (WIDTH//2, HEIGHT*0.12), int(BASE*0.06 + pulse))
                pygame.draw.circle(screen, (255, 255, 255), (WIDTH//2, HEIGHT*0.12), int(BASE*0.065 + pulse), 4)
            else:
                lbl = font_mid.render("¡EMPATE!", True, (255, 255, 255))
                screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, HEIGHT*0.12))

            for i, p in enumerate(players):
                r_idx, c_idx = divmod(i, cols)
                x = (WIDTH // (cols + 1)) * (c_idx + 1) - C_WIDTH // 2
                y = (HEIGHT // (rows + 1)) * (r_idx + 1) - C_HEIGHT // 2
                pygame.draw.circle(screen, p[1], (x + C_WIDTH//2, y - BASE*0.04), int(BASE*0.022))
                pygame.draw.circle(screen, (255,255,255), (x + C_WIDTH//2, y - BASE*0.04), int(BASE*0.022), 2)
                is_w = (get_power(p[2]) == max_p)
                pygame.draw.rect(screen, (255,255,255) if is_w else p[1], (x-8, y-8, C_WIDTH+16, C_HEIGHT+16), 5 if is_w else 2, border_radius=15)
                screen.blit(card_images[p[2]], (x, y))

        pygame.display.flip(); clock.tick(120)