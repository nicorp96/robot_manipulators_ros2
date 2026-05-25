import os

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


def declare_arguments():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "launch_rviz", default_value="true", description="Launch RViz?"
            ),
            DeclareLaunchArgument(
                "warehouse_sqlite_path",
                default_value=os.path.expanduser("~/.ros/warehouse_ros.sqlite"),
                description="Path where the warehouse database should be stored",
            ),
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Using or not time from simulation",
            ),
            DeclareLaunchArgument(
                "publish_robot_description_semantic",
                default_value="true",
                description="MoveGroup publishes robot description semantic",
            ),
        ]
    )


def generate_launch_description():
    launch_rviz = LaunchConfiguration("launch_rviz")
    warehouse_sqlite_path = LaunchConfiguration("warehouse_sqlite_path")
    use_sim_time = LaunchConfiguration("use_sim_time")

    urdf_launch_dir = get_package_share_directory("robot_descriptions")
    urdf_file_path = os.path.join(urdf_launch_dir, "urdf/franka_panda.urdf.xacro")

    moveit_config = (
        MoveItConfigsBuilder(
            robot_name="franka_panda", package_name="robot_moveit_config"
        )
        .robot_description(
            urdf_file_path,
            {
                "arm_id": "fer",
                "franka_hand": "franka_hand",
                "load_gripper": "true",
            },
        )
        .robot_description_semantic(Path("srdf") / "franka.srdf.xacro")
        .planning_pipelines(
            pipelines=["ompl", "stomp", "pilz_industrial_motion_planner"],
            default_planning_pipeline="ompl",
        )
        .robot_description_kinematics(file_path="config/franka/kinematics_moveit.yaml")
        .trajectory_execution(file_path="config/franka/moveit_controllers.yaml")
        .joint_limits(file_path="config/franka/joint_limits_moveit.yaml")
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

    # wait_robot_description = Node(
    #     package="robot_descriptions",
    #     executable="wait_for_robot_description",
    #     output="screen",
    # )
    # ld.add_action(wait_robot_description)

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

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("robot_moveit_config"), "rviz", "planner_franka.rviz"]
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
    ld.add_action(move_group_node)
    ld.add_action(rviz_node)
    # ld.add_action(
    #     RegisterEventHandler(
    #         OnProcessExit(
    #             #target_action=wait_robot_description,
    #             on_exit=[move_group_node, rviz_node],
    #         )
    #     ),
    # )

    return ld
