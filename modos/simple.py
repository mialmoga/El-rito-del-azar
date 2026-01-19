import pygame, random, math, time, colorsys

def run(screen, clock):
    info = pygame.display.Info()
    WIDTH, HEIGHT = info.current_w, info.current_h
    BASE = min(WIDTH, HEIGHT)

    FPS = 120
    CELL_COUNT = 900
    SCALE = int(BASE * 0.7)

    # ================= AJUSTES DE TAMAÑO =================
    # Ajusta aquí el tamaño de cada tipo de partícula
    FONDO_SIZE = 2         # Las partículas del universo/fondo
    SPIN_SIZE = 3          # Las partículas naranjas que saltan al girar
    # =====================================================

    # Otros parámetros del ritual
    ROTATE_BASE = 0.02
    ROTATE_SPIN = 0.12
    SPIN_TIME = 1.3
    PARTICLE_SPEED = 0.03
    ABSORB_SPEED = 0.08
    COLLAPSE_TIME = 0.35
    
    BG_COLOR = (5, 5, 12)
    WHITE = (245, 245, 245)
    ORANGE = (255, 160, 90)
    RED = (220, 60, 60)
    GOLD = (255, 215, 0)

    font_big = pygame.font.SysFont("arial", int(BASE * 0.07), bold=True)
    font_mid = pygame.font.SysFont("arial", int(BASE * 0.045), bold=True)

    # ================= MUNDO =================
    cells = []
    for _ in range(CELL_COUNT):
        z = random.uniform(-1, 1)
        hue = (z + 1) / 2
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1)
        cells.append([
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            z,
            [int(r * 255), int(g * 255), int(b * 255)],
            hue
        ])

    particles = []
    bg_stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(2, 6), random.randint(1, 3)] for _ in range(120)]
    
    spin_phase = 0.0
    color_locked = False
    collapse_start = None

    def project(x, y, z):
        f = SCALE / (z + 2)
        return WIDTH // 2 + int(x * f), HEIGHT // 2 + int(y * f)

    def rotate_cells(speed):
        ct, st = math.cos(speed), math.sin(speed)
        for c in cells:
            x, z = c[0], c[2]
            c[0] = x * ct - z * st
            c[2] = x * st + z * ct

    def update_colors(spinning=False, collapsing=False):
        nonlocal spin_phase, color_locked
        if collapsing: color_locked = True
        if color_locked:
            for c in cells: c[3] = RED
            return
        if spinning: spin_phase += 0.01
        for c in cells:
            hue = c[4]
            if spinning: hue = (hue + spin_phase) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1)
            c[3] = [int(r * 255), int(g * 255), int(b * 255)]

    def spawn_particles(n, color):
        for _ in range(n):
            particles.append([random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1), color])

    def update_particles(absorb=False):
        nonlocal particles
        alive = []
        for x, y, z, col in particles:
            if absorb:
                x *= (1 - ABSORB_SPEED); y *= (1 - ABSORB_SPEED); z *= (1 - ABSORB_SPEED)
            else:
                x += random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
                y += random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
                z += random.uniform(-PARTICLE_SPEED, PARTICLE_SPEED)
            alive.append([x, y, z, col])
        particles = alive

    def draw_ritual_bg(speed_mult=1.0):
        screen.fill(BG_COLOR)
        for s in bg_stars:
            s[1] -= s[2] * speed_mult
            if s[1] < 0: 
                s[1] = HEIGHT
                s[0] = random.randint(0, WIDTH)
            pygame.draw.line(screen, (70, 70, 120), (s[0], s[1]), (s[0], s[1] + 12), 1)
            pygame.draw.circle(screen, (150, 150, 200), (int(s[0]), int(s[1])), s[3])

    def draw_world(dim=False):
        draw_ritual_bg(speed_mult=2.5 if state == SPIN else 1.0)
        
        # Dibujo de las celdas del FONDO
        for c in cells:
            sx, sy = project(c[0], c[1], c[2])
            col = [max(0, val - 100) for val in c[3]] if dim else c[3]
            pygame.draw.circle(screen, col, (sx, sy), FONDO_SIZE) 
        
        # Dibujo de las partículas del SPIN
        for x, y, z, col in particles:
            sx, sy = project(x, y, z)
            pygame.draw.circle(screen, col, (sx, sy), SPIN_SIZE)
            pygame.draw.circle(screen, (255, 255, 255), (sx, sy), max(1, SPIN_SIZE // 2))

    def draw_back_arrow():
        size = int(BASE * 0.05)
        rect = pygame.Rect(BASE * 0.05, BASE * 0.05, size, size)
        color = GOLD if rect.collidepoint(pygame.mouse.get_pos()) else WHITE
        pygame.draw.lines(screen, color, False, [
            (rect.right, rect.top), (rect.left, rect.centery), (rect.right, rect.bottom)
        ], 5)
        return rect

    def draw_die_face(value, center_x):
        SIZE = int(BASE * 0.28)
        x, y = center_x - SIZE // 2, HEIGHT // 2 - SIZE // 2
        pygame.draw.rect(screen, (15, 15, 25), (x, y, SIZE, SIZE), border_radius=22)
        pygame.draw.rect(screen, GOLD, (x, y, SIZE, SIZE), 4, border_radius=22)
        
        o = SIZE // 4
        positions = {
            1: [(0, 0)], 2: [(-o, -o), (o, o)], 3: [(-o, -o), (0, 0), (o, o)],
            4: [(-o, -o), (o, -o), (-o, o), (o, o)],
            5: [(-o, -o), (o, -o), (0, 0), (-o, o), (o, o)],
            6: [(-o, -o), (o, -o), (-o, 0), (o, 0), (-o, o), (o, o)],
        }
        for dx, dy in positions[value]:
            pygame.draw.circle(screen, (255, 255, 255), (center_x + dx, HEIGHT // 2 + dy), SIZE // 18)

    # ================= ESTADOS =================
    SELECT_COUNT, IDLE, SPIN, COLLAPSE, REVEAL = range(5)
    state = SELECT_COUNT
    dice_count, results, t0 = None, [], 0

    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if draw_back_arrow().collidepoint(mx, my): return
                if state == SELECT_COUNT:
                    if pygame.Rect(WIDTH * 0.2, HEIGHT * 0.45, BASE * 0.25, BASE * 0.12).collidepoint(mx, my):
                        dice_count = 1; state = IDLE
                    if pygame.Rect(WIDTH * 0.55, HEIGHT * 0.45, BASE * 0.25, BASE * 0.12).collidepoint(mx, my):
                        dice_count = 2; state = IDLE
                elif state == IDLE:
                    spawn_particles(40, ORANGE); t0 = time.time(); state = SPIN
                elif state == REVEAL:
                    color_locked = False; state = IDLE

        if state == SELECT_COUNT:
            draw_ritual_bg()
            txt = font_big.render("¿Cuántos dados?", True, WHITE)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT * 0.33))
            b1 = pygame.Rect(WIDTH * 0.2, HEIGHT * 0.45, BASE * 0.25, BASE * 0.12)
            b2 = pygame.Rect(WIDTH * 0.55, HEIGHT * 0.45, BASE * 0.25, BASE * 0.12)
            for b, txt in [(b1, "1"), (b2, "2")]:
                h = b.collidepoint(mx, my)
                pygame.draw.rect(screen, (30, 30, 50) if h else (15, 15, 30), b, border_radius=20)
                pygame.draw.rect(screen, GOLD if h else WHITE, b, 2, border_radius=20)
                t_surf = font_mid.render(txt, True, WHITE)
                screen.blit(t_surf, t_surf.get_rect(center=b.center))
        elif state == IDLE:
            rotate_cells(ROTATE_BASE); update_colors(); update_particles(); draw_world()
        elif state == SPIN:
            rotate_cells(ROTATE_SPIN); update_colors(spinning=True); update_particles(); draw_world()
            if time.time() - t0 > SPIN_TIME: collapse_start = time.time(); state = COLLAPSE
        elif state == COLLAPSE:
            update_colors(collapsing=True); update_particles(absorb=True); draw_world(dim=True)
            if time.time() - collapse_start > COLLAPSE_TIME:
                results = [random.randint(1, 6) for _ in range(dice_count)]; state = REVEAL
        elif state == REVEAL:
            rotate_cells(ROTATE_BASE); update_colors(); update_particles(); draw_world(dim=True)
            if dice_count == 1: draw_die_face(results[0], WIDTH // 2)
            else:
                draw_die_face(results[0], WIDTH // 2 - int(BASE * 0.18))
                draw_die_face(results[1], WIDTH // 2 + int(BASE * 0.18))

        draw_back_arrow()
        pygame.display.flip(); clock.tick(FPS)