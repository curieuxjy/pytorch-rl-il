import torch
import numpy as np
import os
from rlil.environments.envs.diag_q import q_iteration, tabular_env, time_limit_wrapper
from rlil.environments import GymEnvironment, ENVS, State, Action
from rlil.presets import continuous


STATE_DISC = 32
ACTION_DISC = 5
MAX_STEPS = 200

ORIGIN_ENV = tabular_env.InvertedPendulum(
    state_discretization=STATE_DISC, action_discretization=ACTION_DISC)
random_init = {
    i: 1.0 / ORIGIN_ENV.num_states for i in range(ORIGIN_ENV.num_states)}
ORIGIN_ENV = tabular_env.InvertedPendulum(
    state_discretization=STATE_DISC, action_discretization=ACTION_DISC, init_dist=random_init)
ENV = time_limit_wrapper.TimeLimitWrapper(ORIGIN_ENV, MAX_STEPS)
RLIL_ENV = GymEnvironment(ENVS["pendulum"], append_time=True)


def compute_true_action_values(qval_path=None):
    """
    compute true action values using q_iteration
    Args:
        qval_path (string): 
        If qval_path is not None, this function return saved q_vals.

    Returns:
        qvals (np.array)
    """

    if qval_path is not None:
        qvals = np.load(qval_path)
        return qvals

    params = {
        'num_itrs': 300,
        'ent_wt': 0.0,
        'discount': 0.99,
    }

    qvals = q_iteration.softq_iteration(ENV, **params, verbose=True)
    np.save("pendulum_q.npy", qvals)
    return qvals


def compute_true_state_values(qvals):
    """
    Return state values by taking max over qvals
    """
    vvals = np.zeros((MAX_STEPS, STATE_DISC, STATE_DISC))
    for wrapped_s in range(ENV.num_states - 1):
        time, s = ENV.unwrap_state(wrapped_s)
        th, thv = ENV.wrapped_env.th_thv_from_id(s)
        th, thv = ENV.wrapped_env.disc_th_thv(th, thv)
        v = qvals[wrapped_s].max()
        vvals[time, th, thv] = v
    return vvals


def get_all_states():
    """
    Return State for computing q or v.
    """
    s1, s2, s3, s4 = [], [], [], []
    for wrapped_s in range(ENV.num_states - 1):
        time, s = ENV.unwrap_state(wrapped_s)
        th, thv = ENV.wrapped_env.th_thv_from_id(s)
        s1.append(np.cos(th))
        s2.append(np.sin(th))
        s3.append(thv)
        s4.append(min(time / MAX_STEPS, 1.0))

    states = torch.cat((torch.tensor(s1, dtype=torch.float32).unsqueeze(1),
                        torch.tensor(s2, dtype=torch.float32).unsqueeze(1),
                        torch.tensor(s3, dtype=torch.float32).unsqueeze(1),
                        torch.tensor(s4, dtype=torch.float32).unsqueeze(1)), dim=1)
    return State(states)


def predict_action_values(q_func):
    """
    Predict action values of all states and actions.
    Returns:
        pred_qvals (np.array): Predicted action values
    """
    states = get_all_states()
    torques = torch.tensor([ENV.wrapped_env.torque_from_id(
        i) for i in range(ACTION_DISC)], dtype=torch.float32).unsqueeze(0)
    torques = torch.repeat_interleave(torques, states.shape[0], dim=0)
    actions_list = [Action(torques[:, i].unsqueeze(1))
                    for i in range(ACTION_DISC)]
    pred_q_list = []
    for i in range(ACTION_DISC):
        pred_q_list.append(
            q_func(states.to(q_func.device), actions_list[0].to(q_func.device)))
    pred_qvals = torch.stack(pred_q_list, dim=1)
    return pred_qvals


def predict_state_values(q_func):
    """
    Predict state values of all states and actions.
    Returns:
        pred_vvals (np.array): Predicted state values
    """
    pred_qvals = predict_action_values(q_func)
    values = torch.max(pred_qvals, dim=1)[0]

    pred_vvals = np.zeros((MAX_STEPS, STATE_DISC, STATE_DISC))
    for wrapped_s in range(ENV.num_states - 1):
        time, s = ENV.unwrap_state(wrapped_s)
        th, thv = ENV.wrapped_env.th_thv_from_id(s)
        th, thv = ENV.wrapped_env.disc_th_thv(th, thv)
        pred_vvals[time, th, thv] = values[wrapped_s]
    return pred_vvals


def predict_state_values_ppo(feature_nw, v_func):
    """
    This function is for ppo to predict state values.
    """
    states = get_all_states()
    features = feature_nw(states.to(feature_nw.device))
    values = v_func(features)

    pred_vvals = np.zeros((MAX_STEPS, STATE_DISC, STATE_DISC))
    for wrapped_s in range(ENV.num_states - 1):
        time, s = ENV.unwrap_state(wrapped_s)
        th, thv = ENV.wrapped_env.th_thv_from_id(s)
        th, thv = ENV.wrapped_env.disc_th_thv(th, thv)
        pred_vvals[time, th, thv] = values[wrapped_s]
    return pred_vvals


def state_to_th_thv_time(states):
    theta = torch.atan2(states.raw[:, 1], states.raw[:, 0]).cpu().detach().numpy()
    theta_v = states.raw[:, 2].cpu().detach().numpy()
    time_step = (states.raw[:, -1] * MAX_STEPS).floor().int().cpu().detach().numpy()
    return theta, theta_v, time_step


def compute_true_action_values_from_samples(full_qvals, states, actions):
    theta, theta_v, time_step = state_to_th_thv_time(states)
    torques = actions.features.cpu().detach().numpy()
    qvals = np.zeros(states.shape[0])
    for i, (th, thv, t, trq) in enumerate(zip(theta, theta_v, time_step, torques)):
        s_idx = ENV.wrapped_env.id_from_th_thv(th, thv)
        s_idx = ENV.wrap_state(s_idx, t)
        a_idx = ENV.wrapped_env.id_from_torque(trq)
        qvals[i] = full_qvals[s_idx][a_idx]
    return qvals
