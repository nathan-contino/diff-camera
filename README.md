# Module diff-camera 

Wraps a camera component. Runs each captured image against the previous image (or the past `image_memories` remembered unique comparison images). Only returns an image if the image differs from the previous image more than the configured `required_diff`.

## Model natch:diff-camera:diff-camera

Provide a description of the model and any relevant information.

### Configuration

The following attribute template can be used to configure this model:

```json
{
"image_memories": <int>,
"required_diff": <float>,
"input_camera": <string>
}
```

#### Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                |
|---------------|--------|-----------|----------------------------|
| `image_memories` | int  | Required  | How many unique recent comparison images to retain for diffing. |
| `required_diff` | float | Optional  | A percentage, specified as a decimal between 0.0 and 1.0, that an input image must differ in a pixel diff from any image in the past N unique `image_memories` to avoid getting filtered out. |
| `input_camera` | string | Required | The camera whose images will be filtered based on diffs with recent images. |

#### Example Configuration

The following configuration retains **5** unique recent images for diffing from a camera component named `camera-1`. If a new image differs from each comparison image by **at least 20%**:

1. If this module has already retained 5 images:
   1. Discards the oldest comparison image.
   1. Adds the new image to the collection of comparison images.
1. Returns the new image.

If the new image is more than 80% similar (in other words, less than 20% different) to a retained image, the module does not return an image.

```json
{
  "image_memories": 5,
  "required_diff": 0.2,
  "input_camera": "camera-1"
}
```

### DoCommand

This model provides functionality to empty the stack of image memories using a DoCommand:

#### targeted_memory_erasure

Much like Lacuna, Inc, use this configuration to delete all stored comparison images:

```json
{
  "targeted_memory_erasure": {
  }
}
```
