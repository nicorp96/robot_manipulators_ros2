######################################################################################
#          Code is heavily based on the tutorials/examples of the Moveit Documentation
#          https://moveit.picknik.ai/
#
#          University of Applied Sciences, Laboratory of Autonomous Systems (LAS)
######################################################################################

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from moveit_configs_utils import MoveItConfigsBuilder
from launch.substitutions import (
    LaunchConfiguration,
    PythonExpression,
    PathJoinSubstitution,
)
from launch_ros.substitutions import FindPackageShare

from pathlib import Path
import os


def launch_setup(context, *args, **kwargs):
    group_name = "ur_manipulator"
    tool_name = "tool0"
    ref_frame = "base_link"
    use_sim_time = False
    sim_gazebo = "false"
    controllers_file = LaunchConfiguration("controllers_file")
    initial_joint_controllers = PathJoinSubstitution(
        [FindPackageShare("robot_descriptions"), "config", controllers_file]
    )
    urdf_launch_dir = get_package_share_directory("robot_descriptions")
    urdf_file_path = os.path.join(urdf_launch_dir, "urdf/ur.urdf.xacro")
    mappings = {
        "name": "ur",
        "sim_gazebo": sim_gazebo,
        "simulation_controllers": initial_joint_controllers,
    }
    moveit_config = (
        MoveItConfigsBuilder(robot_name="ur", package_name="robot_moveit_config")
        .robot_description(file_path=urdf_file_path, mappings=mappings)
        .robot_description_semantic(Path("srdf") / "ur.srdf.xacro", {"name": "ur"})
        .moveit_cpp(
            file_path=get_package_share_directory("robot_moveit_config")
            + "/config/moveit_py.yaml"
        )
        .robot_description_kinematics(file_path="config/ur5/kinematics.yaml")
        .trajectory_execution(file_path="config/ur5/moveit_controllers.yaml")
        .joint_limits(file_path="config/ur5/joint_limits.yaml")
        .to_moveit_configs()
    )

    joy_node = Node(
        name="joy_node",
        package="joy",
        executable="joy_node",
        output="both",
        parameters=[
            {'autorepeat_rate': 2.0},
            {'coalesce_interval_ms': 1000},
            {'deadzone': 0.1},
        ],
    )
    moveit_py_node = Node(
        name="py_suction_control",
        package="py_task_planner",
        executable="py_suction_control",
        output="both",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": use_sim_time},
            {"group_name": group_name},
            {"tool_name": tool_name},
            {"ref_frame": ref_frame},
        ],
    )

    return [
        moveit_py_node,
        joy_node,
    ]


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "controllers_file",
            default_value="ur_controllers.yaml",
            description="YAML file with the controllers configuration.",
        )
    )

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
