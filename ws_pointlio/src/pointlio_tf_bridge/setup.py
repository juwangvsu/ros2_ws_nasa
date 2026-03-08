from setuptools import setup
from glob import glob

package_name = 'pointlio_tf_bridge'

setup(
    name=package_name,
    version='0.1.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@example.com',
    description='Bridge Point-LIO TF to odom/base_link and publish static TF to baal/base.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'republish_pointlio_tf_as_odom = pointlio_tf_bridge.republish_pointlio_tf_as_odom:main',
        ],
    },
)
