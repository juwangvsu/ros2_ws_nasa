from setuptools import setup

package_name = 'mdds30_serial_driver'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/mdds30.launch.py']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    maintainer='ju wang',
    maintainer_email='jwang@vsu.edu',
    description='ROS 2 Python driver for Cytron SmartDriveDuo-30 (MDDS30) in Serial Simplified mode.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mdds30_node = mdds30_serial_driver.mdds30_node:main',
            'mdds30_test_50pct = mdds30_serial_driver.test_50pct_node:main',
        ],
    },
)
