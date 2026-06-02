import pygame, random, math

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('ShadowStrike X AutoFire')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36, bold=True)

player_x = WIDTH // 2
player_y = HEIGHT - 320
bullets = []
enemies = []
stars = []
score = 0
lives = 5
shoot_timer = 0

for i in range(100):
    stars.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)])

for i in range(7):
    enemies.append([random.randint(80, WIDTH-80), random.randint(-800, -50), random.randint(3, 6)])

running = True
while running:
    screen.fill((5,5,25))

    for s in stars:
        s[1] += s[2]
        if s[1] > HEIGHT:
            s[0] = random.randint(0, WIDTH)
            s[1] = 0
        pygame.draw.circle(screen, (180,180,255), (s[0], s[1]), s[2])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            player_x = max(50, min(WIDTH-50, x))

    # Auto Fire
    shoot_timer += 1
    if shoot_timer >= 10:
        bullets.append([player_x, player_y-40])
        shoot_timer = 0

    # Fighter Jet
    pygame.draw.polygon(screen, (170,170,200), [
        (player_x, player_y-60),
        (player_x-45, player_y+45),
        (player_x+45, player_y+45)
    ])
    pygame.draw.polygon(screen, (255,70,70), [
        (player_x, player_y-60),
        (player_x-15, player_y),
        (player_x+15, player_y)
    ])
    pygame.draw.circle(screen, (0,220,255), (player_x, player_y-15), 10)

    for b in bullets[:]:
        b[1] -= 20
        pygame.draw.rect(screen, (0,255,255), (b[0]-3, b[1], 6, 30))
        if b[1] < 0:
            bullets.remove(b)

    for e in enemies:
        e[1] += e[2]

        if e[1] > HEIGHT:
            e[0] = random.randint(80, WIDTH-80)
            e[1] = random.randint(-500, -50)
            lives -= 1

        pygame.draw.circle(screen, (200,0,80), (e[0], e[1]), 30)
        pygame.draw.circle(screen, (255,100,100), (e[0]-12, e[1]-6), 6)
        pygame.draw.circle(screen, (255,100,100), (e[0]+12, e[1]-6), 6)
        pygame.draw.arc(screen, (255,255,255), (e[0]-15, e[1], 30, 18), 0, 3.14, 2)

        if math.hypot(player_x-e[0], player_y-e[1]) < 55:
            lives -= 1
            e[0] = random.randint(80, WIDTH-80)
            e[1] = random.randint(-500, -50)

        for b in bullets[:]:
            if math.hypot(b[0]-e[0], b[1]-e[1]) < 32:
                score += 10
                e[0] = random.randint(80, WIDTH-80)
                e[1] = random.randint(-500, -50)
                if b in bullets:
                    bullets.remove(b)

    screen.blit(font.render(f'SCORE: {score}', True, (255,220,0)), (20,20))
    screen.blit(font.render(f'❤ {lives}', True, (255,70,70)), (20,65))

    if lives <= 0:
        txt = font.render('GAME OVER', True, (255,0,0))
        screen.blit(txt, (WIDTH//2-120, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()