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
    robot = LaunchConfiguration("robot").perform(context)
    controllers_file = LaunchConfiguration("controllers_file")
    initial_joint_controllers = PathJoinSubstitution(
        [FindPackageShare("robot_descriptions"), "config", controllers_file]
    )
    sim_gazebo = LaunchConfiguration("sim_gazebo")
    moveit_config = None
    if "ur5" in robot:
        group_name = "ur_manipulator"
        tool_name = "tool0"
        ref_frame = "base_link"
        use_sim_time = False
        sim_gazebo = "false"
        if "sim" in robot:
            sim_gazebo = "true"
            use_sim_time = True

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
    elif "xarm6" in robot:
        group_name = "xarm6"
        tool_name = "link_eef"
        ref_frame = "link_base"
        use_sim_time = False
        robot_description_pkg_dir = get_package_share_directory("robot_descriptions")
        urdf_file_path = os.path.join(
            robot_description_pkg_dir, "urdf/xarm6.urdf.xacro"
        )
        mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotSystemHardware",
            "robot_ip": "192.168.20.208",
        }
        trajectory_cfg = "config/xarm/moveit_controllers_real.yaml"
        if "fake" in robot:
            mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotFakeSystemHardware",
            "robot_ip": "",
            }
            trajectory_cfg = "config/xarm/moveit_controllers.yaml"

        moveit_config = (
            MoveItConfigsBuilder(robot_name="xarm", package_name="robot_moveit_config")
            .robot_description(file_path=urdf_file_path, mappings=mappings)
            .robot_description_semantic(file_path="srdf/xarm.srdf.xacro")
            .moveit_cpp(
                file_path=get_package_share_directory("robot_moveit_config")
                + "/config/moveit_py.yaml"
            )
            .robot_description_kinematics(file_path="config/xarm/kinematics.yaml")
            .trajectory_execution(file_path=trajectory_cfg)
            .joint_limits(file_path="config/xarm/joint_limits.yaml")
            .to_moveit_configs()
        )
    elif robot == "franka_sim":
        group_name = "fer_manipulator"
        tool_name = "fer_hand"
        ref_frame = "fer_link0"
        use_sim_time = True
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
            .moveit_cpp(
                file_path=get_package_share_directory("robot_moveit_config")
                + "/config/moveit_py.yaml"
            )
            .robot_description_kinematics(
                file_path="config/franka/kinematics_moveit.yaml"
            )
            .trajectory_execution(file_path="config/franka/moveit_controllers.yaml")
            .joint_limits(file_path="config/franka/joint_limits_moveit.yaml")
            .to_moveit_configs()
        )
    else:
        print("Error wrong robot type")

    moveit_py_node = Node(
        name="py_task_example_all",
        package="py_task_planner",
        executable="py_task_example_all",
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
    ]


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "robot",
            description="Robot Moveit",
            default_value="xarm6",
            choices=["ur5", "ur5_sim", "xarm6", "xarm6_fake", "franka_sim"],
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
