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
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
)

def launch_setup(context, *args, **kwargs):
    robot_description_pkg_dir = get_package_share_directory("robot_descriptions")
    fake_controller = LaunchConfiguration("fake_controller").perform(context)
    urdf_file_path = os.path.join(robot_description_pkg_dir, "urdf/xarm6.urdf.xacro")
    if fake_controller.lower() == "true":
        mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotFakeSystemHardware",
            "robot_ip": "",
        }
        trajectory_exc_ctrl = "config/xarm/moveit_controllers.yaml"
    else:
        mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotSystemHardware",
            "robot_ip": "192.168.20.208",
        }
        trajectory_exc_ctrl = "config/xarm/moveit_controllers_real.yaml"

    moveit_config = (
        MoveItConfigsBuilder(robot_name="xarm", package_name="robot_moveit_config")
        .robot_description(file_path=urdf_file_path, mappings=mappings)
        .robot_description_semantic(file_path="srdf/xarm.srdf.xacro")
        .planning_pipelines(
            pipelines=["ompl", "stomp", "pilz_industrial_motion_planner"],
            default_planning_pipeline="ompl",
        )
        .robot_description_kinematics(file_path="config/xarm/kinematics.yaml")
        .trajectory_execution(file_path=trajectory_exc_ctrl)
        .joint_limits(file_path="config/xarm/joint_limits.yaml")
    )
    moveit_py_node = Node(name="py_task_example_2", package="py_task_planner", executable="py_task_example_2",
                          output="both", parameters=[moveit_config.to_dict(), {"use_sim_time": False}])
    
    return [moveit_py_node]

def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_controller",
            default_value="true",
            description="fake controller",
        )
    )
    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )

    
