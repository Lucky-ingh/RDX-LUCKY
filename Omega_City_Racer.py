# Omega City Racer - NITRO BEAST EDITION (FIXED & REWRITTEN)
import pygame
import random
import math
import os
import sys

# 1. INITIALIZATION & SMOOTHNESS CONFIG
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
# Use SCALED for high performance and smooth visuals
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Omega City Racer - Nitro Beast")
clock = pygame.time.Clock()

# 2. ASSET LOADING (Robust & Procedural Fallback)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

def load_asset(filename, size, fallback_color):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        if not os.path.exists(path): raise FileNotFoundError
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, fallback_color, (0, 0, size[0], size[1]), border_radius=12)
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, size[0], size[1]), 2, border_radius=12)
        return surf

PLAYER_SIZE = (int(W * 0.12), int(W * 0.12 * 2.2))
TRAFFIC_SIZE = (int(W * 0.11), int(W * 0.11 * 2.0))
COIN_SIZE = (int(W * 0.08), int(W * 0.08))

player_img = load_asset("player_car.png", PLAYER_SIZE, (0, 200, 255))
traffic_imgs = [
    load_asset("traffic_car_1.png", TRAFFIC_SIZE, (255, 50, 50)),
    load_asset("traffic_car_2.png", TRAFFIC_SIZE, (255, 150, 0))
]
coin_img = load_asset("coin.png", COIN_SIZE, (255, 255, 0))
font_large = pygame.font.SysFont("Arial", int(H * 0.06), True)
font_medium = pygame.font.SysFont("Arial", int(H * 0.04), True)
font_small = pygame.font.SysFont("Arial", int(H * 0.03), True)

# 3. GAME LOGIC
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.px = W // 2 - PLAYER_SIZE[0] // 2
        self.py = H - PLAYER_SIZE[1] - 150
        self.target_x = self.px
        self.score = 0
        self.base_speed = 10
        self.speed = self.base_speed
        self.nitro = 100  # Nitro fuel (0-100)
        self.is_boosting = False
        self.nitro_active = False  # Is nitro currently ON?
        self.hold_timer = 0  # Timer for holding car still
        self.hold_threshold = 120  # 2 seconds at 60FPS
        self.last_mouse_x = self.px
        self.road_y = 0
        self.game_over = False
        self.game_over_timer = 0
        self.traffic = []
        self.coins = []
        self.particles = []
        self.city_lights = []
        self.lane_positions = [W // 6, W // 2, W - W // 6]  # 3 lanes
        
        # Initial city lights for background
        for _ in range(25):
            self.city_lights.append({
                "x": random.randint(0, W),
                "y": random.randint(0, H),
                "size": random.randint(3, 8),
                "color": (random.randint(100, 255), 0, random.randint(100, 255))
            })
            
        for _ in range(5): 
            self.spawn_traffic()
        for _ in range(4): 
            self.spawn_coin()

    def spawn_traffic(self):
        """Spawn traffic in random lanes with better positioning"""
        lane_idx = random.randint(0, 2)
        x = self.lane_positions[lane_idx] - TRAFFIC_SIZE[0] // 2
        y = random.randint(-800, -300)
        
        # Avoid overlapping traffic
        for t in self.traffic:
            if abs(t["y"] - y) < 200:
                y = min(y - 250, -1000)
                break
        
        self.traffic.append({
            "x": x,
            "y": y,
            "speed": random.randint(6, 12),
            "img": random.choice(traffic_imgs),
            "lane": lane_idx
        })

    def spawn_coin(self):
        """Spawn coin in random lane"""
        lane_idx = random.randint(0, 2)
        x = self.lane_positions[lane_idx]
        y = random.randint(-600, -100)
        self.coins.append({"x": x, "y": y, "lane": lane_idx, "rotation": 0})

    def update(self):
        if self.game_over:
            self.game_over_timer += 1
            return

        # INPUT: Get mouse position and movement
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mx, my = pygame.mouse.get_pos()

        if mouse_pressed:
            self.target_x = mx - PLAYER_SIZE[0] // 2
            
            # DETECT HOLD: Check if car is stationary for 2 seconds
            if abs(mx - self.last_mouse_x) < 5:  # Mouse hasn't moved much
                self.hold_timer += 1
                if self.hold_timer >= self.hold_threshold and self.nitro > 0:
                    self.nitro_active = True
            else:
                self.hold_timer = 0
                self.nitro_active = False
            
            self.last_mouse_x = mx
        else:
            self.hold_timer = 0
            self.nitro_active = False

        # Clamp position to screen bounds
        self.target_x = max(0, min(W - PLAYER_SIZE[0], self.target_x))
        
        # Smooth movement (easing)
        self.px += (self.target_x - self.px) * 0.15
        self.px = max(0, min(W - PLAYER_SIZE[0], self.px))

        # SPEED LOGIC with automatic nitro
        if self.nitro_active and self.nitro > 0:
            self.is_boosting = True
            self.speed = self.base_speed * 2.3
            self.nitro -= 0.9
            
            # Nitro particles
            for _ in range(3):
                self.particles.append({
                    "x": self.px + PLAYER_SIZE[0] // 2,
                    "y": self.py + PLAYER_SIZE[1] + 10,
                    "vx": random.uniform(-3, 3),
                    "vy": random.uniform(6, 12),
                    "life": 255,
                    "size": random.randint(2, 5)
                })
        else:
            self.is_boosting = False
            self.speed = self.base_speed + (self.score // 1000) * 0.5  # Gradual speed increase
            if self.nitro < 100:
                self.nitro += 0.12  # Refill nitro when not boosting

        # Road & City Light scrolling
        self.road_y += self.speed
        if self.road_y >= H:
            self.road_y = 0
        
        for light in self.city_lights:
            light["y"] += self.speed * 0.3
            if light["y"] > H:
                light["y"] = -20
                light["x"] = random.randint(0, W)

        # COLLISION & ENTITY UPDATES
        p_rect = pygame.Rect(self.px + 10, self.py + 20, PLAYER_SIZE[0] - 20, PLAYER_SIZE[1] - 40)
        
        # Traffic collision & updates
        for t in self.traffic[:]:
            t["y"] += t["speed"] + (self.speed * 0.4)
            t_rect = pygame.Rect(t["x"] + 8, t["y"] + 15, TRAFFIC_SIZE[0] - 16, TRAFFIC_SIZE[1] - 30)
            
            if p_rect.colliderect(t_rect):
                self.game_over = True
                return
            
            if t["y"] > H + 100:
                self.traffic.remove(t)
                self.spawn_traffic()
                self.score += 10

        # Coin collection & updates
        for c in self.coins[:]:
            c["y"] += self.speed
            c["rotation"] = (c["rotation"] + 5) % 360
            
            coin_distance = math.hypot(
                self.px + PLAYER_SIZE[0] // 2 - c["x"],
                self.py + PLAYER_SIZE[1] // 2 - c["y"]
            )
            
            if coin_distance < 80:
                self.score += 50
                self.nitro = min(100, self.nitro + 20)  # Coins refill nitro!
                self.coins.remove(c)
                self.spawn_coin()
            elif c["y"] > H + 100:
                self.coins.remove(c)
                self.spawn_coin()

        # Particle updates
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.2  # Gravity
            p["life"] -= 12
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self):
        # 1. Background (Dark Neon City Vibes)
        screen.fill((8, 8, 20))
        
        # City lights
        for light in self.city_lights:
            pygame.draw.circle(
                screen,
                light["color"],
                (int(light["x"]), int(light["y"])),
                light["size"]
            )

        # 2. Neon Road Lanes
        for i in range(1, 3):
            lx = i * (W // 3)
            pygame.draw.line(screen, (0, 255, 255), (lx, 0), (lx, H), 3)
        
        # Road markings (center dashed lines)
        for y in range(-50, H + 50, 80):
            ry = (y + self.road_y) % (H + 100)
            pygame.draw.rect(screen, (255, 255, 150), (W // 2 - 3, ry, 6, 40))

        # 3. Particles (Nitro effects)
        for p in self.particles:
            color = (0, 255, 255, int(p["life"]))
            pygame.draw.circle(screen, color[:3], (int(p["x"]), int(p["y"])), p["size"])

        # 4. Coins
        for c in self.coins:
            screen.blit(coin_img, (c["x"] - COIN_SIZE[0] // 2, c["y"] - COIN_SIZE[1] // 2))

        # 5. Traffic
        for t in self.traffic:
            screen.blit(t["img"], (t["x"], t["y"]))

        # 6. Player with Nitro Glow
        if self.is_boosting:
            # Glow effect when boosting
            glow_size = (PLAYER_SIZE[0] * 1.8, PLAYER_SIZE[1] * 1.8)
            glow = pygame.Surface(glow_size, pygame.SRCALPHA)
            pygame.draw.ellipse(
                glow,
                (0, 255, 255, 60),
                (0, 0, glow.get_width(), glow.get_height())
            )
            screen.blit(
                glow,
                (self.px - PLAYER_SIZE[0] * 0.4, self.py - PLAYER_SIZE[1] * 0.4)
            )
        
        screen.blit(player_img, (self.px, self.py))

        # 7. HUD (Beat Mode UI)
        # Nitro Bar Background
        pygame.draw.rect(screen, (40, 40, 60), (W - 180, 20, 160, 30), border_radius=8)
        
        # Nitro Bar Fill
        nitro_color = (0, 255, 100) if self.nitro > 30 else (255, 100, 0)
        if self.is_boosting:
            nitro_color = (255, 0, 200)
        
        pygame.draw.rect(
            screen,
            nitro_color,
            (W - 175, 25, (self.nitro / 100) * 150, 20),
            border_radius=6
        )
        
        # Nitro Label
        nitro_txt = font_small.render(f"NITRO: {int(self.nitro)}%", True, (255, 255, 255))
        screen.blit(nitro_txt, (W - 170, 32))

        # Score Display
        score_txt = font_medium.render(f"SCORE: {self.score}", True, (0, 255, 200))
        screen.blit(score_txt, (20, 20))

        # Hold Timer Display (when holding)
        if self.hold_timer > 0 and not self.nitro_active:
            hold_percent = min(100, (self.hold_timer / self.hold_threshold) * 100)
            timer_txt = font_small.render(f"AUTO NITRO: {int(hold_percent)}%", True, (255, 200, 0))
            screen.blit(timer_txt, (20, 80))

        # Speed Display
        speed_txt = font_small.render(f"SPEED: {int(self.speed * 10)}", True, (100, 200, 255))
        screen.blit(speed_txt, (20, 130))

        # Game Over Screen
        if self.game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 240))
            screen.blit(overlay, (0, 0))
            
            msg = font_large.render("ENGINE FAILURE", True, (255, 50, 50))
            sub_msg = font_medium.render("GAME OVER", True, (255, 100, 100))
            score_msg = font_medium.render(f"FINAL SCORE: {self.score}", True, (0, 255, 200))
            retry = font_small.render("TOUCH TO REBOOT", True, (100, 255, 150))
            
            screen.blit(msg, (W // 2 - msg.get_width() // 2, H // 2 - 100))
            screen.blit(sub_msg, (W // 2 - sub_msg.get_width() // 2, H // 2 - 30))
            screen.blit(score_msg, (W // 2 - score_msg.get_width() // 2, H // 2 + 20))
            screen.blit(retry, (W // 2 - retry.get_width() // 2, H // 2 + 80))
            
            if pygame.mouse.get_pressed()[0]:
                self.reset()

        pygame.display.flip()

# 4. MAIN LOOP
game = Game()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    game.update()
    game.draw()
    clock.tick(60)  # Locked at 60FPS for smoothness

pygame.quit()
