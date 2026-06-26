"""
🌙 MOTOR DEL RITUAL
El corazón palpitante que anima todos los modos.
Aquí vive la magia compartida.
"""

import pygame
import random
import math
from .config import Colors, Physics, Scale


class RitualEngine:
    """Motor compartido para efectos rituales 3D"""
    
    def __init__(self, screen):
        self.screen = screen
        info = pygame.display.Info()
        self.WIDTH = info.current_w
        self.HEIGHT = info.current_h
        self.BASE = min(self.WIDTH, self.HEIGHT)
        self.SCALE = int(self.BASE * Scale.WORLD_SCALE)
        
        # Universo de estrellas
        self.bg_stars = self._create_stars()
        
    def _create_stars(self):
        """Genera el universo de fondo"""
        return [
            [
                random.randint(0, self.WIDTH),
                random.randint(0, self.HEIGHT),
                random.uniform(2, 6),
                random.randint(1, 3)
            ]
            for _ in range(Physics.STAR_COUNT)
        ]
    
    def create_cells(self, count=None, with_color=False):
        """Crea células 3D para el ritual"""
        if count is None:
            count = Physics.CELL_COUNT
            
        cells = []
        for _ in range(count):
            cell = [
                random.uniform(-1, 1),  # x
                random.uniform(-1, 1),  # y
                random.uniform(-1, 1),  # z
            ]
            if with_color:
                import colorsys
                z = cell[2]
                hue = (z + 1) / 2
                r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1)
                cell.append([int(r * 255), int(g * 255), int(b * 255)])
                cell.append(hue)
            cells.append(cell)
        return cells
    
    def project(self, x, y, z, factor=1.0):
        """Proyecta coordenadas 3D a 2D"""
        f = (self.SCALE * factor) / (z + 2)
        return (
            self.WIDTH // 2 + int(x * f),
            self.HEIGHT // 2 + int(y * f)
        )
    
    def rotate_cells(self, cells, speed):
        """Rota células alrededor del eje Y"""
        ct, st = math.cos(speed), math.sin(speed)
        for c in cells:
            x, z = c[0], c[2]
            c[0] = x * ct - z * st
            c[2] = x * st + z * ct
    
    def draw_stars(self, speed_mult=1.0, color_override=None):
        """Dibuja el universo de estrellas de fondo"""
        self.screen.fill(Colors.BG_DARK)
        
        star_col = color_override or Colors.STAR_CORE
        trail_col = Colors.STAR_TRAIL
        
        for s in self.bg_stars:
            s[1] -= s[2] * speed_mult
            if s[1] < 0:
                s[1] = self.HEIGHT
                s[0] = random.randint(0, self.WIDTH)
            
            # Trail
            pygame.draw.line(
                self.screen,
                trail_col,
                (s[0], s[1]),
                (s[0], s[1] + 10),
                1
            )
            # Core
            pygame.draw.circle(
                self.screen,
                star_col,
                (int(s[0]), int(s[1])),
                s[3]
            )
    
    def draw_back_arrow(self):
        """Dibuja flecha de retorno y retorna su rect para detección"""
        size = int(self.BASE * Scale.BACK_ARROW_SIZE)
        margin = int(self.BASE * Scale.BACK_ARROW_MARGIN)
        rect = pygame.Rect(margin, margin, size, size)
        
        mx, my = pygame.mouse.get_pos()
        color = Colors.GOLD if rect.collidepoint(mx, my) else Colors.WHITE
        
        pygame.draw.lines(
            self.screen,
            color,
            False,
            [
                (rect.right, rect.top),
                (rect.left, rect.centery),
                (rect.right, rect.bottom)
            ],
            5
        )
        return rect
    
    def draw_styled_button(self, rect, text, font, color, hover=False):
        """Dibuja botón estilizado con glow"""
        if hover:
            glow_rect = rect.inflate(15, 15)
            pygame.draw.rect(
                self.screen,
                color,
                glow_rect,
                border_radius=30,
                width=2
            )
        
        main_col = color if hover else (15, 15, 25)
        pygame.draw.rect(self.screen, main_col, rect, border_radius=26)
        pygame.draw.rect(self.screen, color, rect, 4, border_radius=26)
        
        txt_col = Colors.WHITE if hover else color
        t = font.render(text, True, txt_col)
        self.screen.blit(t, t.get_rect(center=rect.center))


class ParticleSystem:
    """Sistema de partículas para efectos rituales"""
    
    def __init__(self):
        self.particles = []
    
    def spawn(self, n, color):
        """Genera n partículas con color dado"""
        for _ in range(n):
            self.particles.append([
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                color
            ])
    
    def update(self, absorb=False):
        """Actualiza partículas (expanden o absorben)"""
        alive = []
        for x, y, z, col in self.particles:
            if absorb:
                x *= (1 - Physics.ABSORB_SPEED)
                y *= (1 - Physics.ABSORB_SPEED)
                z *= (1 - Physics.ABSORB_SPEED)
                # Descartar partículas invisibles → permite detectar colapso completo
                if abs(x) + abs(y) + abs(z) < 0.01:
                    continue
            else:
                x += random.uniform(-Physics.PARTICLE_SPEED, Physics.PARTICLE_SPEED)
                y += random.uniform(-Physics.PARTICLE_SPEED, Physics.PARTICLE_SPEED)
                z += random.uniform(-Physics.PARTICLE_SPEED, Physics.PARTICLE_SPEED)
            alive.append([x, y, z, col])
        self.particles = alive
    
    def draw(self, engine, size=None):
        """Dibuja todas las partículas"""
        if size is None:
            size = Scale.PARTICLE_SPIN
        
        for x, y, z, col in self.particles:
            sx, sy = engine.project(x, y, z)
            pygame.draw.circle(engine.screen, col, (sx, sy), size)
            # Núcleo blanco
            pygame.draw.circle(
                engine.screen,
                (255, 255, 255),
                (sx, sy),
                max(1, size // 2)
            )
    
    def clear(self):
        """Limpia todas las partículas"""
        self.particles = []
