import asyncio
from viam.module.module import Module
from viam.resource.registry import Registry, ResourceCreatorRegistration
try:
    from models.sig_diff_vision import DiffVision
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.sig_diff_vision import DiffVision

if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
