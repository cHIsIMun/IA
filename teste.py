from stable_baselines3 import A2C
from gym_env import FlappyAgent  # Importa o ambiente que você criou

# Carrega o ambiente
env = FlappyAgent()

# Carrega o modelo treinado
model = A2C.load("a2c_flappy")

# Reinicia o ambiente
obs = env.reset()
while True:
    # O modelo determina a ação
    action, _states = model.predict(obs)
    
    # Executa a ação no ambiente e obtém os resultados
    obs, rewards, done, info = env.step(action)
    
    # Renderiza o ambiente
    env.render()
    
    # Se o episódio acabou, reinicia o ambiente
    if done:
        obs = env.reset()
