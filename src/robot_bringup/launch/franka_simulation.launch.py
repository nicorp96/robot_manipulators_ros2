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
    load_gripper = LaunchConfiguration("load_gripper")
    franka_hand_name = LaunchConfiguration("franka_hand_name")
    arm_id_name = LaunchConfiguration("arm_id_name")
    start_rviz = LaunchConfiguration("start_rviz")

    franka_control_gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                FindPackageShare("robot_simulation"),
                "/launch",
                "/",
                "/franka_gz_controller.launch.py",
            ]
        ),
        launch_arguments={
            "load_gripper_name": load_gripper,
            "franka_hand_name": franka_hand_name,
            "arm_id_name": arm_id_name,
            "start_rviz": start_rviz,
        }.items(),
    )

    franka_moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                FindPackageShare("robot_moveit_config"),
                "/launch",
                "/moveit_2_franka.launch.py",
            ]
        ),
        launch_arguments={"use_sim_time": "true"}.items(),
    )

    nodes_to_launch = [
        franka_control_gz_launch,
        franka_moveit_launch,
    ]

    return nodes_to_launch


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "load_gripper",
            default_value="true",
            description="true/false for activating the gripper",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "franka_hand_name",
            default_value="franka_hand",
            description="Default value: franka_hand",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "arm_id_name",
            default_value="fer",
            description="Available values: fr3, fp3 and fer",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "start_rviz",
            default_value="false",
            description="true/false for start rviz",
        )
    )

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
