import os
import yaml

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from moveit_configs_utils import MoveItConfigsBuilder

from ament_index_python.packages import get_package_share_directory


def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)

    try:
        with open(absolute_file_path) as file:
            return yaml.safe_load(file)
    except OSError:  # parent of IOError, OSError *and* WindowsError where available
        return None


def declare_arguments():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "launch_rviz", default_value="true", description="Launch RViz?"
            ),
            DeclareLaunchArgument(
                "ur_type",
                description="Typo/series of used UR robot.",
                choices=[
                    "ur3",
                    "ur3e",
                    "ur5",
                    "ur5e",
                    "ur10",
                    "ur10e",
                    "ur16e",
                    "ur20",
                    "ur30",
                ],
            ),
            DeclareLaunchArgument(
                "warehouse_sqlite_path",
                default_value=os.path.expanduser("~/.ros/warehouse_ros.sqlite"),
                description="Path where the warehouse database should be stored",
            ),
            DeclareLaunchArgument(
                "launch_servo", default_value="false", description="Launch Servo?"
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Using or not time from simulation",
            ),
            DeclareLaunchArgument(
                "publish_robot_description_semantic",
                default_value="true",
                description="MoveGroup publishes robot description semantic",
            ),
            DeclareLaunchArgument(
                "sim_gazebo",
                default_value="true",
                description="Indicate whether robot will run in simulation.",
            ),
            DeclareLaunchArgument(
                "fake_sensor_commands",
                default_value="false",
                description="Indicate whether robot will run in simulation.",
            ),
            DeclareLaunchArgument(
                "use_fake_hardware",
                default_value="false",
                description="Indicate whether robot will run in simulation.",
            ),
            DeclareLaunchArgument(
                "controllers_file",
                default_value="ur_controllers.yaml",
                description="YAML file with the controllers configuration.",
            ),
        ]
    )


def generate_launch_description():
    launch_rviz = LaunchConfiguration("launch_rviz")
    ur_type = LaunchConfiguration("ur_type")
    warehouse_sqlite_path = LaunchConfiguration("warehouse_sqlite_path")
    launch_servo = LaunchConfiguration("launch_servo")
    use_sim_time = LaunchConfiguration("use_sim_time")
    publish_robot_description_semantic = LaunchConfiguration(
        "publish_robot_description_semantic"
    )

    controllers_file = LaunchConfiguration("controllers_file")
    initial_joint_controllers = PathJoinSubstitution(
        [FindPackageShare("robot_descriptions"), "config", controllers_file]
    )
    sim_gazebo = LaunchConfiguration("sim_gazebo")
    fake_sensor_commands = LaunchConfiguration("fake_sensor_commands")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")

    urdf_launch_dir = get_package_share_directory("robot_descriptions")
    urdf_file_path = os.path.join(urdf_launch_dir, "urdf/ur_with_table.urdf.xacro")
    mappings = {
        "name": "ur",
        "sim_gazebo": sim_gazebo,
        "fake_sensor_commands": fake_sensor_commands,
        "use_fake_hardware": use_fake_hardware,
        "simulation_controllers": initial_joint_controllers,
    }
    moveit_config = (
        MoveItConfigsBuilder(
            robot_name="ur_with_table", package_name="robot_moveit_config"
        )
        .robot_description(file_path=urdf_file_path, mappings=mappings)
        .robot_description_semantic(
            "srdf/ur.srdf.xacro",
            {
                "name": "ur",
            },
        )
        .planning_pipelines(
            pipelines=["ompl", "stomp", "pilz_industrial_motion_planner"],
            default_planning_pipeline="ompl",
        )
        .robot_description_kinematics(file_path="config/ur5/kinematics.yaml")
        .trajectory_execution(file_path="config/ur5/moveit_controllers.yaml")
        .joint_limits(file_path="config/ur5/joint_limits.yaml")
        .to_moveit_configs()
    )

    warehouse_ros_config = {
        "warehouse_plugin": "warehouse_ros_sqlite::DatabaseConnection",
        "warehouse_host": warehouse_sqlite_path,
    }
    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": True,
        # Publish the planning scene of the physical robot so that rviz plugin can know actual robot
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "monitor_dynamics": False,
        "use_sim_time": use_sim_time,
    }

    ld = LaunchDescription()
    ld.add_entity(declare_arguments())

    wait_robot_description = Node(
        package="robot_descriptions",
        executable="wait_for_robot_description",
        output="screen",
    )
    ld.add_action(wait_robot_description)

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            warehouse_ros_config,
            move_group_configuration,
        ],
    )

    servo_yaml = load_yaml("robot_descriptions", "config/ur_servo.yaml")
    servo_params = {"moveit_servo": servo_yaml}
    servo_node = Node(
        package="moveit_servo",
        condition=IfCondition(launch_servo),
        executable="servo_node",
        parameters=[
            moveit_config.to_dict(),
            servo_params,
        ],
        output="screen",
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("robot_moveit_config"), "rviz", "planner.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        condition=IfCondition(launch_rviz),
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
            warehouse_ros_config,
            {
                "use_sim_time": use_sim_time,
            },
        ],
    )

    ld.add_action(
        RegisterEventHandler(
            OnProcessExit(
                target_action=wait_robot_description,
                on_exit=[move_group_node, rviz_node, servo_node],
            )
        ),
    )

    return ld
