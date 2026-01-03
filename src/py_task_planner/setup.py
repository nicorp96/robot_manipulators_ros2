from setuptools import find_packages, setup
from glob import glob

package_name = 'py_task_planner'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*launch.[pxy][yma]*')),
        ('share/' + package_name + '/utils', glob('utils/*.py')), 
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nrodriguez',
    maintainer_email='nicolas.rodriguez_pena@hm.edu',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'py_task_example = py_task_planner.py_task_example:main',
            'py_task_example_2 = py_task_planner.py_task_example_2:main',
        ],
    },
)
