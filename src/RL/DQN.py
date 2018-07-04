# -*- coding: utf-8 -*-
import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from RL.Envs.environment import env

"""
<OpenAI>
env : CartPole-v1
pls follow the official doc of openAI


<Handmade environment>
env    : Arduino Sensor => distance sensor
state  : distance
action : go forward/backward with intensity => 4 action

<details of action>
go_further_forward
go_forward
go_backward
go_further_backward

"""

def env_init(game_name='CartPole-v1'):
    # initialise game
    env = gym.make(game_name)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    return env, state_size, action_size

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95   # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

    def train(self, agent, env, EPISODES, state_size, batch_size):
        done = False
        for e in range(EPISODES):
            state = env.reset()
            state = np.reshape(state, [1, state_size])
            for episode in range(500):
                # env.render()
                action = agent.act(state)
                next_state, reward, done, _ = env.step(action)
                reward = reward if not done else -10
                next_state = np.reshape(next_state, [1, state_size])
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    print("episode: {}/{}, score: {}, e: {:.2}"
                          .format(e, EPISODES, episode, agent.epsilon))
                    break
                if len(agent.memory) > batch_size:
                    agent.replay(batch_size)
        return agent

    def demo(self, agent, env, EPISODES, state_size, batch_size):
        done = False
        for e in range(EPISODES):
            state = env.reset()
            env.render()
            state = np.reshape(state, [1, state_size])
            for episode in range(500):
                action = agent.act(state)
                next_state, reward, done, _ = env.step(action)
                reward = reward if not done else -10
                next_state = np.reshape(next_state, [1, state_size])
                state = next_state
                if done:
                    break
        return 'done'

if __name__ == "__main__":
    EPISODES = 50
    batch_size = 32
    game_name = 'CartPole-v1'

    # initialise game
    env, state_size, action_size = env_init(game_name)

    # initialise agent
    agent = DQNAgent(state_size, action_size)

    # load model
    agent.load("../models/cartpole-dqn.h5")

    # train
    # agent.train(agent, env, EPISODES, state_size, batch_size)

    # save model/agent state
    agent.save("cartpole-dqn.h5")

    agent.demo(agent, env, EPISODES, state_size, batch_size)