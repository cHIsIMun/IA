import pygame
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SIZE = 50
PLAYER_ORIGINAL_SIZE = (PLAYER_SIZE, PLAYER_SIZE)
PLAYER_CROUCH_SIZE = (PLAYER_SIZE, PLAYER_SIZE // 2)
OBSTACLE_WIDTH = 50
OBSTACLE_MIN_HEIGHT = PLAYER_SIZE
OBSTACLE_MAX_HEIGHT = 150
OBSTACLE_SPEED = 5
NUM_LIVES = 5

WHITE = (255, 255, 255)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


class Player:
    def __init__(self):
        self.x = 100  # Posiciona o jogador no lado esquerdo da tela
        self.y = SCREEN_HEIGHT - PLAYER_SIZE  # Posiciona o jogador no limite inferior da tela
        self.gravity = 0.5  # Força da gravidade
        self.y_velocity = 0  # Velocidade vertical inicial
        self.is_crouching = False
        self.return_to_original_size = False
        self.lives = NUM_LIVES

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

        # Mantém o jogador alinhado com o limite da tela
        if self.x < 0:
            self.x = 0
        elif self.x + PLAYER_SIZE > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - PLAYER_SIZE

    def apply_gravity(self):
        self.y_velocity += self.gravity

        if self.is_crouching:
            self.y_velocity += 5  # Aumenta a velocidade de queda quando agachado

        self.y += self.y_velocity

        # Colisão com a parte inferior da tela
        if self.y + PLAYER_SIZE > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - PLAYER_SIZE
            self.y_velocity = 0

    def jump(self):
        if self.y + PLAYER_SIZE == SCREEN_HEIGHT:
            self.y_velocity = -15

    def crouch(self):
        self.is_crouching = True

    def stand_up(self):
        if self.y + PLAYER_SIZE == SCREEN_HEIGHT:  # Verifica se o cubo está tocando o chão
            self.return_to_original_size = True
        self.is_crouching = False

    def draw(self):
        if self.return_to_original_size:
            self.y = SCREEN_HEIGHT - PLAYER_SIZE
            pygame.draw.rect(screen, WHITE, (self.x, self.y, PLAYER_SIZE, PLAYER_SIZE))
            self.return_to_original_size = False
        elif self.is_crouching:
            pygame.draw.rect(screen, WHITE, (self.x, self.y + PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE // 2))
        else:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, PLAYER_SIZE, PLAYER_SIZE))


class Obstacle:
    def __init__(self):
        self.x = SCREEN_WIDTH
        up = random.choice([0,0,0,35,60])
        if up == 35 or up == 60:
            self.height = random.randint(150, 300)  # Altura do obstáculo aleatória    
        else:
            self.height = random.randint(OBSTACLE_MIN_HEIGHT, OBSTACLE_MAX_HEIGHT)  # Altura do obstáculo aleatória
        self.y = SCREEN_HEIGHT - self.height - up

    def move(self):
        self.x -= OBSTACLE_SPEED

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, OBSTACLE_WIDTH, self.height))


player = Player()
obstacles = []
jumping = False  # Variável para controlar se o jogador está pulando
obstacle_timer = 0

clock = pygame.time.Clock()

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                jumping = True
            elif event.key == pygame.K_DOWN:
                player.crouch()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player.stand_up()

    if jumping:
        player.jump()
        jumping = False

    player.apply_gravity()
    player.draw()

    # Gerar obstáculos aleatoriamente a cada 1 segundo
    obstacle_timer += clock.get_rawtime()
    if obstacle_timer >= random.choice([50, 55, 60]):
        obstacles.append(Obstacle())
        obstacle_timer = 0

    for obstacle in obstacles:
        obstacle.move()
        obstacle.draw()

        # Verificar colisão entre o jogador e os obstáculos
        player_collision_y = player.y + PLAYER_SIZE // 2 if player.is_crouching else player.y
        if (
            player.x < obstacle.x + OBSTACLE_WIDTH
            and player.x + PLAYER_SIZE > obstacle.x
            and player_collision_y < obstacle.y + obstacle.height
            and player_collision_y + PLAYER_SIZE > obstacle.y
        ):
            # Colisão detectada
            player.lives -= 1
            if player.lives == 0:
                running = False
            else:
                obstacles.remove(obstacle)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
