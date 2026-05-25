from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    # Initialize Arguments
    robot = LaunchConfiguration("robot").perform(context)
    nodes_to_launch = []
    if robot == "ur5":
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/ur5_bringup.launch.py",
                    ]
                ),
                launch_arguments={
                    "fake_controllers": "false",
                }.items(),
            )
        )
    elif robot == "ur5_fake":
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/ur5_bringup.launch.py",
                    ]
                ),
                launch_arguments={
                    "fake_controllers": "true",
                }.items(),
            )
        )

    elif robot == "ur5_sim":
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/ur5_simulation.launch.py",
                    ]
                )
            )
        )
    elif robot == "xarm6":
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/xarm6_bringup.launch.py",
                    ]
                ),
                launch_arguments={
                    "fake_controllers": "false",
                }.items(),
            )
        )
    elif robot == "xarm6_fake":
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/xarm6_bringup.launch.py",
                    ]
                ),
                launch_arguments={
                    "fake_controllers": "true",
                }.items(),
            )
        )
    elif robot == "franka_sim":
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/franka_simulation.launch.py",
                    ]
                )
            )
        )

    return nodes_to_launch


def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot",
            description="Roboter Name",
            default_value="xarm6",
            choices=["ur5","ur5_fake","ur5_sim", "xarm6", "xarm6_fake", "franka_sim"],
        )
    )
    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
