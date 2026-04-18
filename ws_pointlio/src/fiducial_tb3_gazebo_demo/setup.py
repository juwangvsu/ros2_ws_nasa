from setuptools import setup
from glob import glob
import os

package_name = 'fiducial_tb3_gazebo_demo'


def files_recursive(root):
    out = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            out.append(os.path.join(dirpath, f))
    return out

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
        ('share/' + package_name + '/worlds', glob('worlds/*.world')),
        ('share/' + package_name + '/models/tag_wall', [
            'models/tag_wall/model.config',
            'models/tag_wall/model.sdf',
        ]),
        ('share/' + package_name + '/models/tag_wall/materials/scripts', glob('models/tag_wall/materials/scripts/*')),
        ('share/' + package_name + '/models/tag_wall/materials/textures', glob('models/tag_wall/materials/textures/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='OpenAI',
    maintainer_email='user@example.com',
    description='TurtleBot3 Waffle + Gazebo classic + slam_toolbox + AprilTag startup anchor demo.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'global_anchor_node = fiducial_tb3_gazebo_demo.global_anchor_node:main',
            'go_publisher = fiducial_tb3_gazebo_demo.go_publisher:main',
        ],
    },
)
