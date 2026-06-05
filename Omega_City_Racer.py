# Omega City Racer - Beast Mode (Rebuilt for Stability)
import pygame
import random
import math
import os
import sys

# 1. INITIALIZATION
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
# Use FULLSCREEN and SCALED for the best cross-platform experience
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Omega City Racer")
clock = pygame.time.Clock()

# 2. ROBUST ASSET LOADING
# This part is critical for Android. We must find the folder where the script lives.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

def load_asset(filename, size=None):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        if not os.path.exists(path):
            print(f"DEBUG: Missing {filename}")
            raise FileNotFoundError
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as e:
        print(f"DEBUG: Error loading {filename}: {e}")
        # Return a visible placeholder so the game doesn't crash
        surf = pygame.Surface(size if size else (50, 50))
        surf.fill((255, 0, 255)) # Magenta placeholder
        pygame.draw.rect(surf, (255, 255, 255), (0, 0, surf.get_width(), surf.get_height()), 2)
        return surf

# Load all assets at start
PLAYER_SIZE = (int(W * 0.18), int(W * 0.18 * 1.6))
TRAFFIC_SIZE = (int(W * 0.16), int(W * 0.16 * 1.5))
COIN_SIZE = (int(W * 0.1), int(W * 0.1))

player_img = load_asset("player_car.png", PLAYER_SIZE)
road_img = load_asset("road_texture.png", (W, H))
bg_img = load_asset("city_background.png", (W, H))
coin_img = load_asset("coin.png", COIN_SIZE)
traffic_imgs = [
    load_asset("traffic_car_1.png", TRAFFIC_SIZE),
    load_asset("traffic_car_2.png", TRAFFIC_SIZE)
]

font = pygame.font.SysFont("Arial", int(H * 0.04), True)

# 3. GAME OBJECTS
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_x = W // 2 - PLAYER_SIZE[0] // 2
        self.player_y = H - PLAYER_SIZE[1] - 100
        self.target_x = self.player_x
        self.score = 0
        self.speed = 12
        self.road_y = 0
        self.game_over = False
        self.traffic = []
        self.coins = []
        
        # Initial spawn
        for _ in range(3): self.spawn_traffic()
        for _ in range(4): self.spawn_coin()

    def spawn_traffic(self):
        lane = random.randint(0, 2)
        lane_w = W // 3
        x = lane * lane_w + (lane_w - TRAFFIC_SIZE[0]) // 2
        y = random.randint(-H, -200)
        self.traffic.append({"x": x, "y": y, "speed": random.randint(5, 10), "img": random.choice(traffic_imgs)})

    def spawn_coin(self):
        self.coins.append({"x": random.randint(50, W-50), "y": random.randint(-H, -100)})

    def update(self):
        if self.game_over: return

        # Road scrolling
        self.road_y += self.speed
        if self.road_y >= H: self.road_y = 0

        # Input handling (Touch/Mouse)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            self.target_x = mx - PLAYER_SIZE[0] // 2
        
        # Smooth player movement
        self.player_x += (self.target_x - self.player_x) * 0.15
        self.player_x = max(0, min(W - PLAYER_SIZE[0], self.player_x))

        # Update Traffic
        player_rect = pygame.Rect(self.player_x + 15, self.player_y + 15, PLAYER_SIZE[0] - 30, PLAYER_SIZE[1] - 30)
        for t in self.traffic[:]:
            t["y"] += t["speed"] + (self.score // 200)
            t_rect = pygame.Rect(t["x"] + 10, t["y"] + 10, TRAFFIC_SIZE[0] - 20, TRAFFIC_SIZE[1] - 20)
            
            if player_rect.colliderect(t_rect):
                self.game_over = True
            
            if t["y"] > H:
                self.traffic.remove(t)
                self.spawn_traffic()
                self.score += 5

        # Update Coins
        for c in self.coins[:]:
            c["y"] += self.speed
            if math.hypot(self.player_x + PLAYER_SIZE[0]//2 - c["x"], self.player_y + PLAYER_SIZE[1]//2 - c["y"]) < 60:
                self.score += 25
                self.coins.remove(c)
                self.spawn_coin()
            elif c["y"] > H:
                self.coins.remove(c)
                self.spawn_coin()

    def draw(self):
        # Draw background and road
        screen.blit(bg_img, (0, 0))
        screen.blit(road_img, (0, self.road_y))
        screen.blit(road_img, (0, self.road_y - H))

        # Draw entities
        for c in self.coins: screen.blit(coin_img, (c["x"] - COIN_SIZE[0]//2, c["y"] - COIN_SIZE[1]//2))
        for t in self.traffic: screen.blit(t["img"], (t["x"], t["y"]))
        screen.blit(player_img, (self.player_x, self.player_y))

        # HUD
        score_surf = font.render(f"NEON SCORE: {self.score}", True, (0, 255, 255))
        screen.blit(score_surf, (20, 20))

        if self.game_over:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            msg = font.render("SYSTEM CRITICAL: GAME OVER", True, (255, 50, 50))
            retry = font.render("TOUCH TO REBOOT", True, (255, 255, 255))
            screen.blit(msg, (W//2 - msg.get_width()//2, H//2 - 50))
            screen.blit(retry, (W//2 - retry.get_width()//2, H//2 + 20))
            if pygame.mouse.get_pressed()[0]: self.reset()

        pygame.display.flip()

# 4. MAIN LOOP
game = Game()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    
    game.update()
    game.draw()
    clock.tick(60)

pygame.quit()
