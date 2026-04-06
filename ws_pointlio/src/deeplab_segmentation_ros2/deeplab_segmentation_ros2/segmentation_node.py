
import os
from typing import Dict, List

import cv2
import numpy as np
from PIL import Image as PILImage
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor
from sensor_msgs.msg import Image, CompressedImage
from std_msgs.msg import Header
import torch
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet50


VOC_CLASSES: List[str] = [
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
]


VOC_COLORS = np.array(
    [
        [0, 0, 0],
        [128, 0, 0],
        [0, 128, 0],
        [128, 128, 0],
        [0, 0, 128],
        [128, 0, 128],
        [0, 128, 128],
        [128, 128, 128],
        [64, 0, 0],
        [192, 0, 0],
        [64, 128, 0],
        [192, 128, 0],
        [64, 0, 128],
        [192, 0, 128],
        [64, 128, 128],
        [192, 128, 128],
        [0, 64, 0],
        [128, 64, 0],
        [0, 192, 0],
        [128, 192, 0],
        [0, 64, 128],
    ],
    dtype=np.uint8,
)


class SegmentationNode(Node):
    def __init__(self) -> None:
        super().__init__("deeplab_segmentation_node")

        self.declare_parameter("input_topic", "/camera/image_raw")
        self.declare_parameter("input_is_compressed", False)
        self.declare_parameter("mask_topic", "/segmentation/mask")
        self.declare_parameter("overlay_topic", "/segmentation/overlay")
        self.declare_parameter("obstacle_mask_topic", "/segmentation/obstacle_mask")
        self.declare_parameter("checkpoint_file", "")
        self.declare_parameter("obstacle_ignore_classes", ["background", "floor", "ground", "sky"])
        self.declare_parameter("log_detected_classes", True)

        self.input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        self.input_is_compressed = (
            self.get_parameter("input_is_compressed").get_parameter_value().bool_value
        )
        self.mask_topic = self.get_parameter("mask_topic").get_parameter_value().string_value
        self.overlay_topic = self.get_parameter("overlay_topic").get_parameter_value().string_value
        self.obstacle_mask_topic = (
            self.get_parameter("obstacle_mask_topic").get_parameter_value().string_value
        )
        self.checkpoint_file = self.get_parameter("checkpoint_file").get_parameter_value().string_value
        self.obstacle_ignore_class_names = [
            str(x)
            for x in self.get_parameter("obstacle_ignore_classes")
            .get_parameter_value()
            .string_array_value
        ]
        self.log_detected_classes = (
            self.get_parameter("log_detected_classes").get_parameter_value().bool_value
        )

        self.class_to_index: Dict[str, int] = {name: idx for idx, name in enumerate(VOC_CLASSES)}
        self.obstacle_ignore_indices = set()
        for class_name in self.obstacle_ignore_class_names:
            if class_name in self.class_to_index:
                self.obstacle_ignore_indices.add(self.class_to_index[class_name])
            else:
                self.get_logger().warn(
                    f'Ignore class "{class_name}" not found in current class list; skipping it.'
                )

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225]),
            ]
        )
        self.model = self._build_model(self.checkpoint_file)
        self.model.to(self.device)
        self.model.eval()

        self.mask_pub = self.create_publisher(Image, self.mask_topic, 10)
        self.overlay_pub = self.create_publisher(Image, self.overlay_topic, 10)
        self.obstacle_pub = self.create_publisher(Image, self.obstacle_mask_topic, 10)

        if self.input_is_compressed:
            self.subscription = self.create_subscription(
                CompressedImage, self.input_topic, self.image_callback_compressed, 10
            )
            self.get_logger().info(f"Subscribed to compressed input topic: {self.input_topic}")
        else:
            self.subscription = self.create_subscription(
                Image, self.input_topic, self.image_callback_raw, 10
            )
            self.get_logger().info(f"Subscribed to raw input topic: {self.input_topic}")

    def _build_model(self, checkpoint_file: str) -> torch.nn.Module:
        model = deeplabv3_resnet50(weights=None, weights_backbone=None, num_classes=21, aux_loss=True)
        if not checkpoint_file:
            raise ValueError("checkpoint_file parameter must be set")
        state_dict = torch.load(checkpoint_file, map_location="cpu")
        if isinstance(state_dict, dict) and "state_dict" in state_dict:
            state_dict = state_dict["state_dict"]
        missing, unexpected = model.load_state_dict(state_dict, strict=False)
        if missing:
            self.get_logger().warn(f"Missing checkpoint keys: {missing}")
        if unexpected:
            self.get_logger().warn(f"Unexpected checkpoint keys: {unexpected}")
        return model

    def image_callback_raw(self, msg: Image) -> None:
        try:
            frame_bgr = self._image_msg_to_bgr(msg)
            self._run_inference(frame_bgr, msg.header)
        except Exception as exc:
            self.get_logger().error(f"Failed to process raw image: {exc}")

    def image_callback_compressed(self, msg: CompressedImage) -> None:
        try:
            frame_bgr = self._compressed_msg_to_bgr(msg)
            self._run_inference(frame_bgr, msg.header)
        except Exception as exc:
            self.get_logger().error(f"Failed to process compressed image: {exc}")

    def _run_inference(self, frame_bgr: np.ndarray, header: Header) -> None:
        input_tensor = self._preprocess_bgr(frame_bgr).to(self.device)
        with torch.no_grad():
            output = self.model(input_tensor)["out"][0]
            pred = torch.argmax(output, dim=0).cpu().numpy().astype(np.uint8)

        if self.log_detected_classes:
            self._log_detected_classes(pred)

        overlay_bgr = self._make_overlay(frame_bgr, pred)
        obstacle_mask = self._make_obstacle_mask(pred)
        pred_m = pred>0
        obs_m = obstacle_mask>0
        print(f"pred {pred[pred_m]} \n obstacle_mask {obstacle_mask[obs_m]}")
        self.mask_pub.publish(
            self._numpy_to_image_msg(pred, "mono8", header.frame_id, header.stamp)
        )
        self.overlay_pub.publish(
            self._numpy_to_image_msg(overlay_bgr, "bgr8", header.frame_id, header.stamp)
        )
        self.obstacle_pub.publish(
            self._numpy_to_image_msg(obstacle_mask, "mono8", header.frame_id, header.stamp)
        )

    def _preprocess_bgr(self, image_bgr: np.ndarray) -> torch.Tensor:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        pil_image = PILImage.fromarray(image_rgb)
        return self.preprocess(pil_image).unsqueeze(0)

    def _image_msg_to_bgr(self, msg: Image) -> np.ndarray:
        if msg.encoding not in ("bgr8", "rgb8", "mono8"):
            raise ValueError(f"Unsupported image encoding: {msg.encoding}")

        channels = 1 if msg.encoding == "mono8" else 3
        array = np.frombuffer(msg.data, dtype=np.uint8)
        expected_size = msg.height * msg.width * channels
        if array.size < expected_size:
            raise ValueError(f"Image buffer too small: {array.size} < {expected_size}")
        array = array[:expected_size].reshape((msg.height, msg.width, channels))

        if msg.encoding == "rgb8":
            return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        if msg.encoding == "mono8":
            return cv2.cvtColor(array[:, :, 0], cv2.COLOR_GRAY2BGR)
        return array.copy()

    def _compressed_msg_to_bgr(self, msg: CompressedImage) -> np.ndarray:
        np_arr = np.frombuffer(msg.data, dtype=np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("cv2.imdecode returned None")
        return image

    def _numpy_to_image_msg(self, image: np.ndarray, encoding: str, frame_id: str, stamp) -> Image:
        msg = Image()
        msg.header.frame_id = frame_id
        msg.header.stamp = stamp
        msg.height = int(image.shape[0])
        msg.width = int(image.shape[1])
        msg.encoding = encoding
        msg.is_bigendian = False

        if encoding == "mono8":
            if image.ndim != 2:
                raise ValueError("mono8 image must be 2D")
            msg.step = int(image.shape[1])
            msg.data = image.astype(np.uint8).tobytes()
        elif encoding == "bgr8":
            if image.ndim != 3 or image.shape[2] != 3:
                raise ValueError("bgr8 image must be HxWx3")
            msg.step = int(image.shape[1] * 3)
            msg.data = image.astype(np.uint8).tobytes()
        else:
            raise ValueError(f"Unsupported output encoding: {encoding}")

        return msg

    def _make_overlay(self, frame_bgr: np.ndarray, pred: np.ndarray) -> np.ndarray:
        color_mask = VOC_COLORS[pred]
        color_mask_bgr = color_mask[:, :, ::-1]
        return cv2.addWeighted(frame_bgr, 0.5, color_mask_bgr, 0.5, 0.0)

    def _make_obstacle_mask(self, pred: np.ndarray) -> np.ndarray:
        mask = np.ones_like(pred, dtype=np.uint8) * 255
        for idx in self.obstacle_ignore_indices:
            mask[pred == idx] = 0
        return mask

    def _log_detected_classes(self, pred: np.ndarray) -> None:
        unique_classes, counts = np.unique(pred, return_counts=True)
        items = []
        for class_idx, count in zip(unique_classes.tolist(), counts.tolist()):
            class_name = VOC_CLASSES[class_idx] if 0 <= class_idx < len(VOC_CLASSES) else f"class_{class_idx}"
            items.append(f"{class_name}={count}")
        self.get_logger().info("Detected classes (pixels): " + ", ".join(items))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SegmentationNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
