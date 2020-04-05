import torch
from rlil.environments import squash_action
from rlil.approximation import Approximation
from rlil.nn import RLNetwork


class BCQDeterministicPolicy(Approximation):
    def __init__(
            self,
            model,
            optimizer,
            space,
            name='policy',
            **kwargs
    ):
        model = BCQDeterministicPolicyNetwork(model, space)
        super().__init__(
            model,
            optimizer,
            name=name,
            **kwargs
        )


class BCQDeterministicPolicyNetwork(RLNetwork):
    def __init__(self, model, space):
        super().__init__(model)
        self._action_dim = space.shape[0]
        self._tanh_scale = torch.tensor(
            (space.high - space.low) / 2).to(self.device)
        self._tanh_mean = torch.tensor(
            (space.high + space.low) / 2).to(self.device)

    def forward(self, states, vae_actions):
        x = torch.cat((states.features.float(),
                       vae_actions.features.float()), dim=1)
        a = vae_actions.features + 0.05 * \
            self.model(x) * states.mask.float().unsqueeze(-1)
        return squash_action(a, self._tanh_scale, self._tanh_mean)

    def to(self, device):
        self._tanh_mean = self._tanh_mean.to(device)
        self._tanh_scale = self._tanh_scale.to(device)
        return super().to(device)