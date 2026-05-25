######################################################################################
#          Code is heavily based on the tutorials/examples of the Moveit Documentation
#          https://moveit.picknik.ai/
#
#          University of Applied Sciences, Laboratory of Autonomous Systems (LAS)              
######################################################################################

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder
from launch.substitutions import (
    LaunchConfiguration,
)
import os
from pathlib import Path
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
)
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.substitutions import FindPackageShare

def launch_setup(context, *args, **kwargs):
    robot_description_pkg_dir = get_package_share_directory("robot_descriptions")
    sim_gazebo = LaunchConfiguration("sim_gazebo").perform(context)
    controllers_file = LaunchConfiguration("controllers_file")
    initial_joint_controllers = PathJoinSubstitution(
        [FindPackageShare("robot_descriptions"), "config", controllers_file]
    )
    urdf_file_path = os.path.join(robot_description_pkg_dir, "urdf/xarm6.urdf.xacro")
    use_sim_time = False
    if sim_gazebo.lower() == "true":
        use_sim_time = True
    
    mappings = {
            "name": "ur",
            "sim_gazebo": sim_gazebo,
            "simulation_controllers": initial_joint_controllers,
        }

    urdf_launch_dir = get_package_share_directory("robot_descriptions")
    urdf_file_path = os.path.join(urdf_launch_dir, "urdf/ur.urdf.xacro")
    mappings = {
        "name": "ur",
        "sim_gazebo": sim_gazebo,
        "simulation_controllers": initial_joint_controllers,
    }
    moveit_config = (
        MoveItConfigsBuilder(
            robot_name="ur", package_name="robot_moveit_config"
        )
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
    moveit_py_node = Node(name="py_task_ur", package="py_task_planner", executable="py_task_ur",
                          output="both", parameters=[moveit_config.to_dict(), {"use_sim_time": use_sim_time}])
    
    return [moveit_py_node]

def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_gazebo",
            default_value="false",
            description="simulation",
        )
    )
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

    
