from setuptools import setup
from glob import glob

package_name = "deeplab_segmentation_ros2"

setup(
    name=package_name,
    version="0.0.3",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.py")),
        (f"share/{package_name}/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="OpenAI",
    maintainer_email="user@example.com",
    description="ROS 2 DeepLabV3 segmentation node with raw or compressed input selection.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "segmentation_node = deeplab_segmentation_ros2.segmentation_node:main",
            "download_checkpoint = deeplab_segmentation_ros2.download_checkpoint:main",
        ],
    },
)
