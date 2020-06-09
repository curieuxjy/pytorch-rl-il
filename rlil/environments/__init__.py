from .base import Environment
from .gym import GymEnvironment
from .state import State
from .action import Action, action_decorator, clip_action, squash_action
from .reward_fns import *
from rlil.diag_q.tabular import tabular_env, time_limit_wrapper
import gym
from gym.envs.registration import registry, make, spec


def register(id, *args, **kvargs):
    if id in registry.env_specs:
        return
    else:
        return gym.envs.registration.register(id, *args, **kvargs)


# Half gravity envs
register(id='HalfGravityWalker2DBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:HalfGravityWalker2DBulletEnv',
         max_episode_steps=1000,
         reward_threshold=2500.0)
register(id='HalfGravityHalfCheetahBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:HalfGravityHalfCheetahBulletEnv',
         max_episode_steps=1000,
         reward_threshold=3000.0)

register(id='HalfGravityAntBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:HalfGravityAntBulletEnv',
         max_episode_steps=1000,
         reward_threshold=2500.0)

register(id='HalfGravityHopperBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:HalfGravityHopperBulletEnv',
         max_episode_steps=1000,
         reward_threshold=2500.0)

register(id='HalfGravityHumanoidBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:HalfGravityHumanoidBulletEnv',
         max_episode_steps=1000)

# Double gravity envs
register(id='DoubleGravityWalker2DBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:DoubleGravityWalker2DBulletEnv',
         max_episode_steps=1000,
         reward_threshold=2500.0)
register(id='DoubleGravityDoubleCheetahBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:DoubleGravityDoubleCheetahBulletEnv',
         max_episode_steps=1000,
         reward_threshold=3000.0)

register(id='DoubleGravityAntBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:DoubleGravityAntBulletEnv',
         max_episode_steps=1000,
         reward_threshold=2500.0)

register(id='DoubleGravityHopperBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:DoubleGravityHopperBulletEnv',
         max_episode_steps=1000,
         reward_threshold=2500.0)

register(id='DoubleGravityHumanoidBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:DoubleGravityHumanoidBulletEnv',
         max_episode_steps=1000)

# Different gait bullet envs
register(id='HalfFrontLegsAntBulletEnv-v0',
         entry_point='rlil.environments.envs.mismatch_env:HalfFrontLegsAntBulletEnv',
         max_episode_steps=1000,
         reward_threshold=2500.0)

# Grid world envs
register(id='CoordinateWiseSimpleGridEnv-v0',
         entry_point='rlil.diag_q.envs.diag_q_env:CoordinateWiseSimpleGrid',
         max_episode_steps=300)

register(id='CoordinateWiseLavaGridEnv-v0',
         entry_point='rlil.diag_q.envs.diag_q_env:CoordinateWiseLavaGrid',
         max_episode_steps=300)

register(id='RandomObsSimpleGridEnv-v0',
         entry_point='rlil.diag_q.envs.diag_q_env:RandomObsSimpleGrid',
         max_episode_steps=300)

register(id='RandomObsLavaGridEnv-v0',
         entry_point='rlil.diag_q.envs.diag_q_env:RandomObsLavaGrid',
         max_episode_steps=300)


__all__ = ["Environment", "State", "GymEnvironment", "Action"]

# some example envs
# can also enter ID directly
ENVS = {
    # grid environments
    "simple_grid": "CoordinateWiseSimpleGridEnv-v0",
    "lava_grid": "CoordinateWiseLavaGridEnv-v0",
    # classic discrete environments
    "cartpole": "CartPole-v0",
    "acrobot": "Acrobot-v1",
    # classic continuous environments
    "pendulum": "Pendulum-v0",
    "mountaincar": "MountainCarContinuous-v0",
    "lander": "LunarLanderContinuous-v2",
    # Bullet robotics environments
    "ant": "AntBulletEnv-v0",
    "cheetah": "HalfCheetahBulletEnv-v0",
    "humanoid": "HumanoidBulletEnv-v0",
    "hopper": "HopperBulletEnv-v0",
    "walker": "Walker2DBulletEnv-v0",
    # Half gravity bullet envs
    "half_gravity_ant": "HalfGravityAntBulletEnv-v0",
    "half_gravity_cheetah": "HalfGravityHalfCheetahBulletEnv-v0",
    "half_gravity_humanoid": "HalfGravityHumanoidBulletEnv-v0",
    "half_gravity_hopper": "HalfGravityHopperBulletEnv-v0",
    "half_gravity_walker": "HalfGravityWalker2DBulletEnv-v0",
    # Double gravity bullet envs
    "double_gravity_ant": "DoubleGravityAntBulletEnv-v0",
    "double_gravity_cheetah": "DoubleGravityHalfCheetahBulletEnv-v0",
    "double_gravity_humanoid": "DoubleGravityHumanoidBulletEnv-v0",
    "double_gravity_hopper": "DoubleGravityHopperBulletEnv-v0",
    "double_gravity_walker": "DoubleGravityWalker2DBulletEnv-v0",
    # Different gait bullet envs
    "half_front_legs_ant": 'HalfFrontLegsAntBulletEnv-v0'
}


REWARDS = {
    "Pendulum-v0": PendulumReward,
    "MountainCarContinuous-v0": MountainCarContinuousReward,
}


# Diagnosing q environments

def make_diag_q_pendulum(state_disc=32, action_disc=5, max_steps=200):
    env = tabular_env.InvertedPendulum(
        state_discretization=state_disc,
        action_discretization=action_disc)
    random_init = {
        i: 1.0 / env.num_states for i in range(env.num_states)}
    env = tabular_env.InvertedPendulum(
        state_discretization=state_disc,
        action_discretization=action_disc,
        init_dist=random_init)
    env = time_limit_wrapper.TimeLimitWrapper(env, max_steps)
    return env
