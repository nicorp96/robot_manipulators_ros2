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
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/ur_control.launch.py",
                    ]
                ),
                launch_arguments={
                    "robot_ip": "192.2222.227",
                    "use_mock_hardware": "true",
                    "ur_type": "ur5",
                    "launch_rviz": "false",
                    "description_file": "ur.urdf.xacro",
                    "initial_joint_controller": "joint_trajectory_controller",
                }.items(),
            )
        )
    else:
        nodes_to_launch.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        FindPackageShare("robot_bringup"),
                        "/launch",
                        "/ur_control.launch.py",
                    ]
                ),
                launch_arguments={
                    "robot_ip": "192.168.20.157",
                    "use_mock_hardware": "false",
                    "ur_type": "ur5",
                    "launch_rviz": "false",
                    "description_file": "ur.urdf.xacro",
                    "initial_joint_controller": "joint_trajectory_controller",
                }.items(),
            )
        )

    moveit_ur5_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                FindPackageShare("robot_moveit_config"),
                "/launch",
                "/ur5_moveit_ros2.launch.py",
            ]
        ),
        launch_arguments={
            "ur_type": "ur5",
            "publish_robot_description_semantic": "true",
            "sim_gazebo": "false",
            "use_fake_hardware": "false",
            "use_sim_time": "false",
            "controllers_file": "ur_controllers.yaml",
            "launch_rviz": "true",
        }.items(),
    )
    nodes_to_launch.append(moveit_ur5_node)
    return nodes_to_launch


def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_controllers",
            default_value="False",
            description="Indicate whether robot will run with fake controllers.",
        )
    )
    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
