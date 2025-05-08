import asyncio
from viam.module.module import Module
from viam.components.camera import Camera
try:
    from models.diff_camera import DiffCamera
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.diff_camera import DiffCamera


async def main():
    module = Module()
    module.add_model(Camera.SUBTYPE, DiffCamera.MODEL, DiffCamera)
    await module.start()


if __name__ == '__main__':
    asyncio.run(main())
