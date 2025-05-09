import asyncio
from viam.module.module import Module
from viam.services.vision import Vision
from viam.resource.registry import Registry, ResourceCreatorRegistration
try:
    from models.sig_diff_vision import DiffVision
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.sig_diff_vision import DiffVision


async def main():
    # Register the model
    Registry.register_resource_creator(
        Vision.SUBTYPE,
        DiffVision.MODEL,
        ResourceCreatorRegistration(DiffVision.new_vision)
    )
    
    module = Module.from_args()
    await module.start()


if __name__ == '__main__':
    asyncio.run(main())
