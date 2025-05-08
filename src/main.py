import asyncio
from viam.module.module import Module
from viam.components.camera import Camera
from viam.resource.registry import Registry, ResourceCreatorRegistration
try:
    from models.diff_camera import DiffCamera
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.diff_camera import DiffCamera

async def main():
    Registry.register_resource_creator(
        "rdk:component:camera",
        DiffCamera.MODEL,
        ResourceCreatorRegistration(DiffCamera.new_camera)
    )
    
    module = Module.from_args()

    await module.start()


if __name__ == '__main__':
    asyncio.run(main())
