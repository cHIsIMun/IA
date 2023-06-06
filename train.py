from stable_baselines3 import A2C
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
import gym

# Importe o ambiente que criamos anteriormente
from gym_env import FlappyAgent  # Adapte o nome do módulo conforme necessário

# Cria o ambiente
env = FlappyAgent()
eval_env = Monitor(env, "eval_logs")

# Envelopa o ambiente para treinamento
env = DummyVecEnv([lambda: env])

# Cria o agente de aprendizado (A2C é uma forma de Actor-Critic)
model = A2C('MlpPolicy', env, verbose=1)

# Treina o agente por 10^5 passos
model.learn(total_timesteps=100000)

# Salva o modelo treinado
model.save("a2c_flappy")

# Avalia o modelo treinado
mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=10)


print(f"Mean reward: {mean_reward}, Std reward: {std_reward}")

# Visualiza o agente treinado em tempo de execução
obs = env.reset()
while True:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
    if done:
        obs = env.reset()
