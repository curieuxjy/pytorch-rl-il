import torch
from torch.distributions.normal import Normal
from torch.nn.functional import mse_loss
from rlil.environments import action_decorator, Action
from ._agent import Agent


class BCQ(Agent):
    """
    Batch-Constrained Q-learning (BCQ)

    BCQ is an algorithm to train an agent from a fixed batch.
    Traditional off-policy algorithms such as DQN and DDPG fail to train an agent from a fixed batch
    due to extraporation error. Extraporation error causes overestimation of the q values for state-action
    pairs that fall outside of the distribution of the fixed batch.
    BCQ attempts to eliminate extrapolation error by constraining the agent's actions to the data
    distribution of the batch.

    https://arxiv.org/abs/1812.02900

    Args:
        q_1 (QContinuous): An Approximation of the continuous action Q-function.
        q_2 (QContinuous): An Approximation of the continuous action Q-function.
        policy (DeterministicPolicy): An Approximation of a deterministic policy.
        replay_buffer (ReplayBuffer): The experience replay buffer.
        action_space (gym.spaces.Box): Description of the action space.
        discount_factor (float): Discount factor for future rewards.
        minibatch_size (int): The number of experiences to sample in each training update.
        noise_policy (float): the amount of noise to add to each action (before scaling).
        noise_td3 (float): the amount of noise to add to each action in trick three.
        policy_update_td3 (int): Number of timesteps per training update the policy in trick two.
        replay_start_size (int): Number of experiences in replay buffer when training begins.
        update_frequency (int): Number of timesteps per training update.
    """

    def __init__(self,
                 q_1,
                 q_2,
                 policy,
                 replay_buffer,
                 action_space,
                 discount_factor=0.99,
                 minibatch_size=32,
                 noise_policy=0.1,
                 noise_td3=0.2,
                 policy_update_td3=2,
                 replay_start_size=5000,
                 update_frequency=1,
                 device=torch.device("cpu")
                 ):
        # objects
        self.q_1 = q_1
        self.q_2 = q_2
        self.policy = policy
        self.replay_buffer = replay_buffer
        self.device = device
        # hyperparameters
        self.replay_start_size = replay_start_size
        self.update_frequency = update_frequency
        self.minibatch_size = minibatch_size
        self.discount_factor = discount_factor
        # private
        self._noise_policy = Normal(
            0, noise_policy * torch.tensor((action_space.high - action_space.low) / 2).to(self.device))
        self._noise_td3 = Normal(
            0, noise_td3 * torch.tensor((action_space.high - action_space.low) / 2).to(self.device))
        self._policy_update_td3 = policy_update_td3
        self._low = torch.tensor(action_space.low, device=self.device)
        self._high = torch.tensor(action_space.high, device=self.device)
        self._states = None
        self._actions = None
        self._train_count = 0

    def act(self, states, reward):
        self.replay_buffer.store(self._states, self._actions, reward, states)
        self._train()
        self._states = states
        self._actions = self._choose_actions(states)
        return self._actions

    @action_decorator
    def _choose_actions(self, states):
        actions = self.policy.eval(states.to(self.device))
        actions = actions + self._noise_policy.sample([actions.shape[0]])
        actions = torch.min(actions, self._high)
        actions = torch.max(actions, self._low)
        return actions.to("cpu")

    def _train(self):
        if self._should_train():
            # sample transitions from buffer
            (states, actions, rewards, next_states, _) = self.replay_buffer.sample(
                self.minibatch_size, device=self.device)

            # Trick Three: Target Policy Smoothing
            next_actions = self.policy.target(next_states)
            next_actions += self._noise_td3.sample([next_actions.shape[0]])
            next_actions = torch.min(next_actions, self._high)
            next_actions = torch.max(next_actions, self._low)
 
            # train q-network
            # Trick One: clipped double q learning
            q_targets = rewards + self.discount_factor * \
                torch.min(self.q_1.target(next_states, next_actions), self.q_2.target(next_states, next_actions))
            self.q_1.reinforce(mse_loss(self.q_1(states, actions.features), q_targets))
            self.q_2.reinforce(mse_loss(self.q_2(states, actions.features), q_targets))

            # train policy
            # Trick Two: delayed policy updates
            if self._train_count % self._policy_update_td3 == 0:
                greedy_actions = self.policy(states)
                loss = -self.q_1(states, greedy_actions).mean()
                self.policy.reinforce(loss)
                self.policy.zero_grad()
            self.q_1.zero_grad()
            self.q_2.zero_grad()

    def _should_train(self):
        self._train_count += 1
        return len(self.replay_buffer) > self.replay_start_size and self._train_count % self.update_frequency == 0
