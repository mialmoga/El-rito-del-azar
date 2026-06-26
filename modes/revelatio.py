"""🔮 REVELATIO - Juego Simultáneo de Cartas"""
import pygame, random, time, math, os, sys
sys.path.insert(0, '/home/claude/ritual_refactor')
from core import Colors, RitualEngine, CARD_PALETTE, VALUE_TO_FILE

def run(screen, clock):
    engine = RitualEngine(screen)
    font_big = pygame.font.SysFont("arial", int(engine.BASE*0.08), bold=True)
    font_mid = pygame.font.SysFont("arial", int(engine.BASE*0.05), bold=True)
    cells = engine.create_cells()
    
    card_images = {}
    C_WIDTH = int(engine.BASE * 0.22) 
    C_HEIGHT = int(C_WIDTH * (1306 / 825))
    art_path = os.path.join(os.path.dirname(__file__), "..", "assets", "art")
    
    def load_art():
        for v in list(range(1, 14)) + [20]:
            name = VALUE_TO_FILE.get(v, str(v))
            try:
                img = pygame.image.load(os.path.join(art_path, f"{name}.png")).convert_alpha()
                card_images[v] = pygame.transform.smoothscale(img, (C_WIDTH, C_HEIGHT))
            except:
                f = pygame.Surface((C_WIDTH, C_HEIGHT)); f.fill((20, 20, 40)); card_images[v] = f
    load_art()
    
    def get_power(val):
        if val == 20: return 99
        if val == 1: return 14
        return val
    
    SELECT, IDLE, SPIN, REVEAL = range(4)
    state = SELECT
    players, original_players = [], []
    sudden_death = False
    t0 = 0
    
    while True:
        mx, my = pygame.mouse.get_pos()
        
        bg_col = (40, 10, 10) if sudden_death else Colors.BG_DARK
        screen.fill(bg_col)
        speed_mult = 2.5 if state == SPIN else 1.0
        engine.draw_stars(speed_mult=speed_mult)
        
        rot_speed = 0.12 if state == SPIN else 0.02
        engine.rotate_cells(cells, rot_speed)
        
        for c in cells:
            sx, sy = engine.project(*c)
            col = Colors.RED if sudden_death else (120, 120, 180)
            pygame.draw.circle(screen, col, (sx, sy), 2)
        
        back_rect = engine.draw_back_arrow()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(e.pos): return
                
                if state == SELECT:
                    for i in range(6):
                        r_area = pygame.Rect(engine.WIDTH//2 - engine.BASE*0.3, engine.HEIGHT*0.35 + i*engine.BASE*0.08, engine.BASE*0.6, engine.BASE*0.07)
                        if r_area.collidepoint(e.pos):
                            players = [[f"P{j+1}", CARD_PALETTE[j], 0] for j in range(i+1)]
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
            txt = font_big.render("¿CUÁNTOS?", True, Colors.WHITE)
            screen.blit(txt, (engine.WIDTH//2-txt.get_width()//2, engine.HEIGHT*0.2))
            for i in range(6):
                r_area = pygame.Rect(engine.WIDTH//2 - engine.BASE*0.3, engine.HEIGHT*0.35 + i*engine.BASE*0.08, engine.BASE*0.6, engine.BASE*0.07)
                hover = r_area.collidepoint(mx, my)
                for j in range(i+1):
                    off_x = (j - i/2) * (engine.BASE*0.06)
                    rad = int(engine.BASE*0.025 if hover else engine.BASE*0.015)
                    pygame.draw.circle(screen, CARD_PALETTE[j], (int(engine.WIDTH//2 + off_x), int(r_area.centery)), rad)
        
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
                pygame.draw.circle(screen, win_col, (engine.WIDTH//2, int(engine.HEIGHT*0.12)), int(engine.BASE*0.06 + pulse))
                pygame.draw.circle(screen, Colors.WHITE, (engine.WIDTH//2, int(engine.HEIGHT*0.12)), int(engine.BASE*0.065 + pulse), 4)
            else:
                lbl = font_mid.render("¡EMPATE!", True, Colors.WHITE)
                screen.blit(lbl, (engine.WIDTH//2 - lbl.get_width()//2, engine.HEIGHT*0.12))
            
            for i, p in enumerate(players):
                r_idx, c_idx = divmod(i, cols)
                x = (engine.WIDTH // (cols + 1)) * (c_idx + 1) - C_WIDTH // 2
                y = (engine.HEIGHT // (rows + 1)) * (r_idx + 1) - C_HEIGHT // 2
                pygame.draw.circle(screen, p[1], (x + C_WIDTH//2, y - int(engine.BASE*0.04)), int(engine.BASE*0.022))
                pygame.draw.circle(screen, Colors.WHITE, (x + C_WIDTH//2, y - int(engine.BASE*0.04)), int(engine.BASE*0.022), 2)
                is_w = (get_power(p[2]) == max_p)
                pygame.draw.rect(screen, Colors.WHITE if is_w else p[1], (x-8, y-8, C_WIDTH+16, C_HEIGHT+16), 5 if is_w else 2, border_radius=15)
                screen.blit(card_images[p[2]], (x, y))
        
        pygame.display.flip(); clock.tick(120)
