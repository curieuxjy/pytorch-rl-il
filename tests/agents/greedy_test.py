import unittest
from rlil.environments import GymEnvironment
from rlil.agents import GreedyAgent
from rlil.approximation import QNetwork
from rlil.policies import SoftmaxPolicy, DeterministicPolicy
from rlil.environments import State, Action
from rlil import nn
import torch
from torch.optim import Adam
import gym


class TestGreedy(unittest.TestCase):
    def test_q_discrete(self):
        env = gym.make('CartPole-v0')
        env = GymEnvironment(env)

        model = nn.Sequential(nn.Flatten(), nn.Linear(
            env.state_space.shape[0], Action.action_space().n))
        optimizer = Adam(model.parameters())
        agent = GreedyAgent(q=QNetwork(model, optimizer))

        env.reset()
        while not env._state.done:
            action = agent.act(env.state, env.reward)
            state, reward = env.step(action)

    def test_policy_discrete(self):
        env = gym.make('CartPole-v0')
        env = GymEnvironment(env)

        model = nn.Sequential(nn.Flatten(), nn.Linear(
            env.state_space.shape[0], Action.action_space().n))
        optimizer = Adam(model.parameters())
        agent = GreedyAgent(
            policy=SoftmaxPolicy(model, optimizer))

        env.reset()
        while not env._state.done:
            action = agent.act(env.state, env.reward)
            state, reward = env.step(action)

    def test_policy_continuous(self):
        env = gym.make('LunarLanderContinuous-v2')
        env = GymEnvironment(env)

        model = nn.Sequential(nn.Flatten(), nn.Linear(
            env.state_space.shape[0], Action.action_space().shape[0]))
        optimizer = Adam(model.parameters())
        agent = GreedyAgent(policy=DeterministicPolicy(
            model, optimizer, Action.action_space()))

        env.reset()
        while not env._state.done:
            action = agent.act(env.state, env.reward)
            state, reward = env.step(action)