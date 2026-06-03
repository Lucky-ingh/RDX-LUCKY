# Omega City Racer Phase 1
import pygame, random, math

pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 34, True)

car_x = W//2
car_y = H-200
speed = 0
score = 0
road_offset = 0
traffic = []
coins = []

for i in range(6):
    traffic.append([random.randint(100, W-100), random.randint(-800, -100), random.randint(6, 10)])

for i in range(10):
    coins.append([random.randint(100, W-100), random.randint(-1200, 0)])

running = True
while running:
    screen.fill((20,20,25))

    # Road
    road_offset += 20
    if road_offset > 80:
        road_offset = 0

    pygame.draw.rect(screen, (40,40,40), (W//2-250, 0, 500, H))

    for i in range(0, H, 80):
        pygame.draw.rect(screen, (255,255,255), (W//2-5, i+road_offset, 10, 40))

    # Touch control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            car_x = max(W//2-220, min(W//2+220, event.pos[0]))

    # Traffic cars
    for t in traffic:
        t[1] += t[2]

        pygame.draw.rect(screen, (200,50,50), (t[0], t[1], 60, 100))

        if t[1] > H:
            t[0] = random.randint(W//2-220, W//2+220)
            t[1] = random.randint(-800, -100)
            score += 5

        if abs(car_x - t[0]) < 50 and abs(car_y - t[1]) < 80:
            running = False

    # Coins
    for c in coins:
        c[1] += 10
        pygame.draw.circle(screen, (255,215,0), (c[0], c[1]), 12)

        if c[1] > H:
            c[0] = random.randint(W//2-220, W//2+220)
            c[1] = random.randint(-1200, 0)

        if math.hypot(car_x-c[0], car_y-c[1]) < 40:
            score += 10
            c[1] = -100

    # Car (player)
    pygame.draw.rect(screen, (0,200,255), (car_x, car_y, 70, 120))
    pygame.draw.rect(screen, (255,255,255), (car_x+10, car_y+20, 50, 60))

    # HUD
    panel = pygame.Surface((260, 90), pygame.SRCALPHA)
    panel.fill((0,0,0,120))
    screen.blit(panel, (10,10))

    screen.blit(font.render(f"SCORE {score}", True, (0,255,255)), (25,25))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()