import unittest
import numpy as np
import torch
from torch.optim import Adam
import gym
import pybullet
import pybullet_envs
import time
from rlil.environments import GymEnvironment
from rlil import nn
from rlil.agents import GreedyAgent
from rlil.approximation import QNetwork
from rlil.policies import SoftmaxPolicy, DeterministicPolicy
from rlil.experiments import SingleEnvRunner, ParallelEnvRunner


def make_discrete_agent(env):
    model = nn.Sequential(nn.Flatten(), nn.Linear(
        env.state_space.shape[0], env.action_space.n))
    optimizer = Adam(model.parameters())
    return GreedyAgent(q=QNetwork(model, optimizer))


def make_continuous_agent(env):
    model = nn.Sequential(nn.Flatten(), nn.Linear(
        env.state_space.shape[0], env.action_space.shape[0]))
    optimizer = Adam(model.parameters())
    return GreedyAgent(policy=DeterministicPolicy(model, optimizer, env.action_space))


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()

    def test_single_runner_discrete(self):
        env = gym.make('CartPole-v0')
        env = GymEnvironment(env)
        runner = SingleEnvRunner(
            make_discrete_agent, env, episodes=100)
        print("SingleEnv discrete exec time: {:.3f}".format(
            time.time() - self.startTime))

    def test_parallel_runner_discrete(self):
        env = gym.make('CartPole-v0')
        env = GymEnvironment(env)
        seeds = [i for i in range(5)]
        runner = ParallelEnvRunner(
            make_discrete_agent, env, 5, seeds, episodes=100)
        print("ParallelEnv discrete exec time: {:.3f}".format(
            time.time() - self.startTime))

    def test_single_runner_continuous(self):
        env = gym.make('Walker2DBulletEnv-v0')
        env = GymEnvironment(env)
        runner = SingleEnvRunner(
            make_continuous_agent, env, episodes=20)
        print("SingleEnv continuous exec time: {:.3f}".format(
            time.time() - self.startTime))

    def test_parallel_runner_continuous(self):
        env = gym.make('Walker2DBulletEnv-v0')
        env = GymEnvironment(env)
        seeds = [i for i in range(4)]
        runner = ParallelEnvRunner(
            make_continuous_agent, env, 4, seeds, episodes=20)
        print("ParallelEnv continuous exec time: {:.3f}".format(
            time.time() - self.startTime))