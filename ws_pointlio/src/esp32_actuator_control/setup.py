from setuptools import setup

package_name = 'esp32_actuator_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/actuator_control.launch.py']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='robot',
    maintainer_email='robot@example.com',
    description='Keyboard/joystick actuator control for ESP32 serial actuator controller.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'actuator_control_node = esp32_actuator_control.actuator_control_node:main',
        ],
    },
)
