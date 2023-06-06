import gym
from gym import spaces
import numpy as np
import pygame
import pygame.font
import random

# Constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SIZE = 50
PLAYER_ORIGINAL_SIZE = (PLAYER_SIZE, PLAYER_SIZE)
PLAYER_CROUCH_SIZE = (PLAYER_SIZE, PLAYER_SIZE // 2)
OBSTACLE_WIDTH = 50
OBSTACLE_MIN_HEIGHT = PLAYER_SIZE
OBSTACLE_MAX_HEIGHT = 150
OBSTACLE_SPEED = 5
NUM_LIVES = 10
WHITE = (255, 255, 255)
RED = (255, 0, 0)


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

    def draw(self, screen):
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

    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, OBSTACLE_WIDTH, self.height))


class FlappyAgent(gym.Env):
    def __init__(self):
        super(FlappyAgent, self).__init__()

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Expandindo o espaço de observação para abrigar novas variáveis
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(7,))  # Adicionando novas variáveis de observação

        self.player = Player()
        self.obstacles = []
        self.obstacle_timer = 0

        self.font = pygame.font.Font(None, 36)

        self.clock = pygame.time.Clock()

    def step(self, action):
        reward = 0.1  # Recompensa por cada passo sem colidir

        if action == 1:  # Pular
            self.player.jump()
            reward -= 0.05  # Penalidade por pular desnecessariamente
        elif action == 2:  # Agachar
            self.player.crouch()
            reward -= 0.05  # Penalidade por agachar desnecessariamente
        else:  # Não fazer nada
            self.player.stand_up()

        self.player.apply_gravity()
        self.player.draw(self.screen)

        self.obstacle_timer += 1
        if self.obstacle_timer >= 50:
            self.obstacles.append(Obstacle())
            self.obstacle_timer = 0

        for obstacle in self.obstacles:
            obstacle.move()
            obstacle.draw(self.screen)

            player_collision_y = self.player.y + PLAYER_SIZE // 2 if self.player.is_crouching else self.player.y
            if (
                self.player.x < obstacle.x + OBSTACLE_WIDTH
                and self.player.x + PLAYER_SIZE > obstacle.x
                and player_collision_y < obstacle.y + obstacle.height
                and player_collision_y + PLAYER_SIZE > obstacle.y
            ):
                self.player.lives -= 1
                if self.player.lives == 0:
                    reward = -1.0
                    return self._get_default_observation(), reward, True, {}
                else:
                    self.obstacles.remove(obstacle)
                    reward = -1.0
                    return self._get_default_observation(), reward, False, {}

            if obstacle.x + OBSTACLE_WIDTH < 0:
                reward += 1.0
                self.obstacles.remove(obstacle)

        observation = self._get_observation()

        if np.isnan(observation).any() or np.isinf(observation).any():
            observation = self._get_default_observation()

        return observation, reward, False, {}

    def _get_observation(self):
        if len(self.obstacles) > 0:
            next_obstacle = min(self.obstacles, key=lambda x: x.x)
            next_next_obstacle = None

            if len(self.obstacles) > 1:
                self.obstacles.sort(key=lambda x: x.x)
                next_next_obstacle = self.obstacles[1] if self.obstacles[0] == next_obstacle else self.obstacles[0]

            player_height_ratio = self.player.y / SCREEN_HEIGHT
            is_crouching = int(self.player.is_crouching)
            next_obstacle_distance = (next_obstacle.x - self.player.x - PLAYER_SIZE) / SCREEN_WIDTH
            next_obstacle_height = (next_obstacle.y - next_obstacle.height) / SCREEN_HEIGHT
            next_obstacle_next_distance = (
                (next_next_obstacle.x - next_obstacle.x - OBSTACLE_WIDTH) / SCREEN_WIDTH
                if next_next_obstacle
                else (SCREEN_WIDTH - (next_obstacle.x + OBSTACLE_WIDTH)) / SCREEN_WIDTH
            )
            obstacle_type = self._get_obstacle_type(next_obstacle.height)

            observation = np.array(
                [
                    player_height_ratio,
                    is_crouching,
                    next_obstacle_distance,
                    next_obstacle_height,
                    next_obstacle_next_distance,
                    obstacle_type,
                ]
            )

            observation = gym.utils.normalize(observation)  # Normaliza o vetor de observação

            # Verifica se alguma das observações contém um valor inválido (nan ou infinito)
            if np.isnan(observation).any() or np.isinf(observation).any():
                return self._get_default_observation()  # Retorna uma observação padrão em caso de valores inválidos

            return observation
        else:
            return self._get_default_observation()  # Retorna uma observação padrão se não houver obstáculos

    def _get_default_observation(self):
        return np.array([0.0, 0, 1.0, 1.0, 1.0, 0])  # Observação padrão quando não há obstáculos
