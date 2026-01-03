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
    fake_controllers = LaunchConfiguration("fake_controllers").perform(context)
    nodes_to_launch = []
    if fake_controllers.lower() == "true":
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_moveit_config"),
                        "/launch",
                        "/moveit_2_xarm6.launch.py",
                    ]
                ),
                launch_arguments={
                    "fake_controller": "true",
                    "launch_rviz": "true",
                    "publish_robot_description_semantic": "true",
                    "no_gui_ctrl": "false",
                    "use_sim_time": "false",
                }.items(),
            )
        )
    else:
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_moveit_config"),
                        "/launch",
                        "/moveit_2_xarm6.launch.py",
                    ]
                ),
                launch_arguments={
                    "fake_controller": "false",
                    "launch_rviz": "true",
                    "publish_robot_description_semantic": "true",
                    "no_gui_ctrl": "false",
                    "use_sim_time": "false",
                }.items(),
            )
        )

    return nodes_to_launch


def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_controllers",
            default_value="false",
            description="Indicate whether robot will run with fake controllers.",
        )
    )
    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
