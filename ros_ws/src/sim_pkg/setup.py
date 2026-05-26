from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sim_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/sim_pkg']),
        ('share/sim_pkg', ['package.xml']),
        (os.path.join('share', 'sim_pkg', 'launch'), glob('sim_pkg/launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_node = sim_pkg.camera_node:main',
            'image_publisher = sim_pkg.image_publisher:main',
            'decision_node = sim_pkg.decision_node:main',
        ],
    },
)
