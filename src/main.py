import asyncio
from viam.module.module import Module
try:
    from models.diff_camera import DiffCamera
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.diff_camera import DiffCamera


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
