import sys
from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple)

from typing_extensions import Self
from viam.components.camera import Camera
from viam.media.video import NamedImage, ViamImage
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName, ResponseMetadata
from viam.proto.component.camera import GetPropertiesResponse, GetImageResponse
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes
import numpy as np
from PIL import Image
import io
from viam.services.vision import Vision


class DiffCamera(Camera):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(ModelFamily("natch", "diff-camera"), "diff-camera")
    SUBTYPE: ClassVar[ResourceName] = Camera.SUBTYPE

    def __init__(self, name: str):
        super().__init__(name)
        self.image_memories: List[np.ndarray] = []
        self.required_diff: float = 0.2  # Default 20% difference required
        self.input_camera: Optional[Camera] = None

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Camera component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Dict[str, str]:
        """Validate the configuration for the diff camera."""

        deps = []

        if "image_memories" not in config:
            raise ValueError("image_memories is required")
        if not isinstance(config["image_memories"], int) or config["image_memories"] < 1:
            raise ValueError("image_memories must be a positive integer")
            
        if "input_camera" not in config:
            raise ValueError("input_camera is required")
        if not isinstance(config["input_camera"], str):
            raise ValueError("input_camera must be a string")
        deps.append(config["input_camera"])
            
        if "required_diff" in config:
            if not isinstance(config["required_diff"], (int, float)):
                raise ValueError("required_diff must be a number")
            if not 0 <= config["required_diff"] <= 1:
                raise ValueError("required_diff must be between 0 and 1")
        
        # Return a mapping of dependency names to their types
        return deps

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        # Get the input camera from dependencies
        input_camera_name = config.attributes.fields["input_camera"].string_value
        input_camera_resource_name = ResourceName(
            namespace="rdk",
            type="component",
            subtype="camera",
            name=input_camera_name
        )
        
        if input_camera_resource_name not in dependencies:
            raise ValueError(f"Input camera {input_camera_name} not found in dependencies")
            
        # Cast the dependency to Camera type using the cast method
        self.input_camera = Camera.from_robot(dependencies[input_camera_resource_name])
        
        # Set configuration parameters
        self.image_memories = []  # Clear existing memories on reconfigure
        self.required_diff = config.attributes.fields["required_diff"].number_value if "required_diff" in config.attributes.fields else 0.2

    async def get_image(self, mime_type: str = "") -> GetImageResponse:
        """Get an image from the input camera if it differs enough from stored images."""
        if not self.input_camera:
            raise RuntimeError("Input camera not set")
            
        # Get image from input camera
        response = await self.input_camera.get_image(mime_type)
        img_data = response.image
        img = Image.open(io.BytesIO(img_data))
        img_array = np.array(img)
        
        # If no memories, store and return the image
        if not self.image_memories:
            self.image_memories.append(img_array)
            self.logger.info("No previous images to compare against, storing first image")
            return response
            
        # Check if image differs enough from all stored images
        is_different = True
        for i, memory in enumerate(self.image_memories):
            diff = self._calculate_image_diff(img_array, memory)
            self.logger.info(f"Image difference with memory {i}: {diff:.2%}")
            if diff < self.required_diff:
                is_different = False
                self.logger.info(f"Image too similar to memory {i} (diff: {diff:.2%} < required: {self.required_diff:.2%})")
                break
                
        if is_different:
            # Add new image to memories, removing oldest if at capacity
            if len(self.image_memories) >= self.image_memories:
                self.image_memories.pop(0)
                self.logger.info("Removed oldest image from memory")
            self.image_memories.append(img_array)
            self.logger.info(f"Image different enough from all memories, storing (diff > {self.required_diff:.2%})")
            return response
            
        # If not different enough, return None
        self.logger.info("Image not different enough from memories, not returning")
        return None

    async def get_images(self) -> List[GetImageResponse]:
        """Get multiple images from the camera."""
        img = await self.get_image()
        return [img] if img else []

    async def get_point_cloud(self) -> Tuple[bytes, str]:
        """Get a point cloud from the camera."""
        raise NotImplementedError("Point cloud not supported by diff camera")

    async def get_properties(self) -> Camera.Properties:
        """Get the camera properties."""
        if not self.input_camera:
            raise RuntimeError("Input camera not set")
        return await self.input_camera.get_properties()

    async def do_command(self, command: Dict[str, ValueTypes], *, timeout: Optional[float] = None) -> Dict[str, ValueTypes]:
        """Handle custom commands."""
        if "targeted_memory_erasure" in command:
            self.image_memories = []
            return {"status": "success", "message": "All image memories cleared"}
        return {"status": "error", "message": "Unknown command"}

    def _calculate_image_diff(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate the difference between two images as a percentage."""
        if img1.shape != img2.shape:
            # Resize the larger image to match the smaller one
            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]
            if h1 * w1 > h2 * w2:
                img1 = np.array(Image.fromarray(img1).resize((w2, h2)))
            else:
                img2 = np.array(Image.fromarray(img2).resize((w1, h1)))
        
        # Calculate mean absolute difference
        diff = np.mean(np.abs(img1.astype(float) - img2.astype(float)))
        max_diff = 255.0  # Maximum possible difference for uint8 images
        return diff / max_diff

    async def get_geometries(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> List[Geometry]:
        self.logger.error("`get_geometries` is not implemented")
        raise NotImplementedError()

