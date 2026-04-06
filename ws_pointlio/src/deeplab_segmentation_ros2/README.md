# deeplab_segmentation_ros2

ROS 2 Python package for semantic segmentation using `torchvision.models.segmentation.deeplabv3_resnet50`.

## Features

- Subscribes to either a raw `sensor_msgs/msg/Image` topic or a `sensor_msgs/msg/CompressedImage` topic.
- YAML parameter `input_is_compressed` selects the subscriber type.
- Publishes segmentation mask, overlay image, and obstacle mask.
- Logs detected classes and pixel counts per frame.
- Includes a helper to download and save the pretrained checkpoint locally.

## YAML example

```yaml
/deeplab_segmentation_node:
  ros__parameters:
    input_topic: /camera/image_raw/compressed
    input_is_compressed: true
    mask_topic: /segmentation/mask
    overlay_topic: /segmentation/overlay
    obstacle_mask_topic: /segmentation/obstacle_mask
    checkpoint_file: /absolute/path/to/deeplabv3_resnet50_coco_voc.pth
    obstacle_ignore_classes: ["background", "floor", "ground", "sky"]
    log_detected_classes: true
```

Set `input_is_compressed: false` and `input_topic: /camera/image_raw` for raw images.

## Download checkpoint

```bash
python3 -m deeplab_segmentation_ros2.download_checkpoint
```

## Build

```bash
colcon build --packages-select deeplab_segmentation_ros2 --symlink-install
source install/setup.bash
```

## Launch

```bash
ros2 launch deeplab_segmentation_ros2 segmentation.launch.py   config_file:=src/deeplab_segmentation_ros2/config/segmentation_params.yaml
```
