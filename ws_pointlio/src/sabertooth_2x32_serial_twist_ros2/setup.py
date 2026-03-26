from setuptools import find_packages, setup

package_name = 'sabertooth_2x32_serial_twist'

setup(
    name=package_name,
    version='0.2.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', ['launch/sabertooth_twist.launch.py']),
        ('share/' + package_name + '/config', ['config/sabertooth_twist.yaml']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='OpenAI',
    maintainer_email='user@example.com',
    description='ROS 2 driver for Sabertooth 2x32 serial motor control with Twist /cmd_vel input',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sabertooth_twist_node = sabertooth_2x32_serial_twist.sabertooth_twist_node:main',
        ],
    },
)
