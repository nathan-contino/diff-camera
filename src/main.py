import asyncio
from viam.module.module import Module
from viam.components.camera import Camera
from viam.proto.common import ResourceName
try:
    from models.diff_camera import DiffCamera
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.diff_camera import DiffCamera


async def main():
    module = Module()
    # Register the model using the standard pattern
    camera_resource = ResourceName(
        namespace="rdk",
        type="component",
        subtype="camera",
        name=""
    )
    module.add_model_from_registry(camera_resource, DiffCamera.MODEL)
    await module.start()


if __name__ == '__main__':
    asyncio.run(main())
