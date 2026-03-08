from setuptools import setup
from glob import glob

package_name = 'pointlio_nav_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ju wang',
    maintainer_email='jwang@vsu.edu',
    description='Bridge Point-LIO outputs into Nav2-friendly /map and /scan topics, with optional static TF publishers.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'map_and_scan_node = pointlio_nav_bridge.map_and_scan_node:main',
        ],
    },
)
