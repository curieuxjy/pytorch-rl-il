import rlil.presets.continuous
import rlil.presets.batch_continuous
import inspect

__all__ = ["continuous", "batch_continuous"]


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }