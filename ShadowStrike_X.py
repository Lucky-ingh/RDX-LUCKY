import pygame
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('ShadowStrike X Mobile')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

player = pygame.Rect(350, 500, 50, 50)
bullets = []
enemies = []
score = 0
lives = 3

LEFT_BTN = pygame.Rect(30, 500, 70, 70)
RIGHT_BTN = pygame.Rect(120, 500, 70, 70)
SHOOT_BTN = pygame.Rect(700, 500, 70, 70)

move_left = False
move_right = False

for _ in range(5):
    enemies.append(pygame.Rect(random.randint(0, 750), random.randint(-300, -40), 40, 40))

running = True
while running:
    screen.fill((20,20,30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if LEFT_BTN.collidepoint(event.pos):
                move_left = True
            if RIGHT_BTN.collidepoint(event.pos):
                move_right = True
            if SHOOT_BTN.collidepoint(event.pos):
                bullets.append(pygame.Rect(player.x+20, player.y, 10, 20))

        if event.type == pygame.MOUSEBUTTONUP:
            move_left = False
            move_right = False

    if move_left and player.x > 0:
        player.x -= 6
    if move_right and player.x < WIDTH-50:
        player.x += 6

    for bullet in bullets[:]:
        bullet.y -= 8
        if bullet.y < 0:
            bullets.remove(bullet)

    for enemy in enemies:
        enemy.y += 4

        if enemy.y > HEIGHT:
            enemy.y = random.randint(-200, -40)
            enemy.x = random.randint(0, 750)
            lives -= 1

        if player.colliderect(enemy):
            enemy.y = random.randint(-200, -40)
            enemy.x = random.randint(0, 750)
            lives -= 1

        for bullet in bullets[:]:
            if bullet.colliderect(enemy):
                score += 10
                enemy.y = random.randint(-200, -40)
                enemy.x = random.randint(0, 750)
                if bullet in bullets:
                    bullets.remove(bullet)

    pygame.draw.rect(screen, (0,255,0), player)

    for bullet in bullets:
        pygame.draw.rect(screen, (255,255,0), bullet)

    for enemy in enemies:
        pygame.draw.rect(screen, (255,0,0), enemy)

    pygame.draw.rect(screen, (80,80,80), LEFT_BTN)
    pygame.draw.rect(screen, (80,80,80), RIGHT_BTN)
    pygame.draw.rect(screen, (150,0,0), SHOOT_BTN)

    screen.blit(font.render('L', True, (255,255,255)), (55,520))
    screen.blit(font.render('R', True, (255,255,255)), (145,520))
    screen.blit(font.render('FIRE', True, (255,255,255)), (705,520))

    screen.blit(font.render(f'Score: {score}', True, (255,255,255)), (10,10))
    screen.blit(font.render(f'Lives: {lives}', True, (255,255,255)), (10,50))

    if lives <= 0:
        game_over = font.render('GAME OVER', True, (255,0,0))
        screen.blit(game_over, (330,280))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
