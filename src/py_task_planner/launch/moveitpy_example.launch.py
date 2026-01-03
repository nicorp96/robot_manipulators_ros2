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
    group_name = LaunchConfiguration("group_name").perform(context)
    tool_name = LaunchConfiguration("tool_name").perform(context)
    ref_frame = LaunchConfiguration("ref_frame").perform(context)
    use_sim_time = PythonExpression(
        ["'True' if '", LaunchConfiguration("use_sim_time"), "' == 'true' else 'False'"]
    )
    controllers_file = LaunchConfiguration("controllers_file")
    initial_joint_controllers = PathJoinSubstitution(
        [FindPackageShare("robot_descriptions"), "config", controllers_file]
    )
    sim_gazebo = LaunchConfiguration("sim_gazebo")
    fake_sensor_commands = LaunchConfiguration("fake_sensor_commands")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    moveit_config = None
    if robot == "ur5":
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
    elif robot == "xarm6":
        robot_description_pkg_dir = get_package_share_directory("robot_descriptions")
        urdf_file_path = os.path.join(
            robot_description_pkg_dir, "urdf/xarm6.urdf.xacro"
        )
        mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotSystemHardware",
            "robot_ip": "192.168.20.208",
        }
        moveit_config = (
            MoveItConfigsBuilder(robot_name="xarm", package_name="robot_moveit_config")
            .robot_description(file_path=urdf_file_path, mappings=mappings)
            .robot_description_semantic(file_path="srdf/xarm.srdf.xacro")
            .moveit_cpp(
                file_path=get_package_share_directory("robot_moveit_config")
                + "/config/moveit_py.yaml"
            )
            .robot_description_kinematics(file_path="config/xarm/kinematics.yaml")
            .trajectory_execution(file_path="config/xarm/moveit_controllers_real.yaml")
            .joint_limits(file_path="config/xarm/joint_limits.yaml")
            .to_moveit_configs()
        )
    elif robot == "xarm6_fake":
        mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotFakeSystemHardware",
            "robot_ip": "",
        }
        robot_description_pkg_dir = get_package_share_directory("robot_descriptions")
        urdf_file_path = os.path.join(
            robot_description_pkg_dir, "urdf/xarm6.urdf.xacro"
        )
        moveit_config = (
            MoveItConfigsBuilder(robot_name="xarm", package_name="robot_moveit_config")
            .robot_description(file_path=urdf_file_path, mappings=mappings)
            .robot_description_semantic(file_path="srdf/xarm.srdf.xacro")
            .moveit_cpp(
                file_path=get_package_share_directory("robot_moveit_config")
                + "/config/moveit_py.yaml"
            )
            .robot_description_kinematics(file_path="config/xarm/kinematics.yaml")
            .trajectory_execution(file_path="config/xarm/moveit_controllers.yaml")
            .joint_limits(file_path="config/xarm/joint_limits.yaml")
            .to_moveit_configs()
        )
    elif robot == "franka":
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
        name="py_task_example",
        package="py_task_planner",
        executable="py_task_example",
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
            choices=["ur5", "xarm6", "xarm6_fake", "franka"],
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "ref_frame",
            description="Ref. Frame",
            default_value="link_base",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "tool_name",
            description="Tool Name",
            default_value="link_eef",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "group_name",
            description="Group Name",
            default_value="xarm6",
            choices=["ur_manipulator", "xarm6", "fer_manipulator"],
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Make MoveIt to use simulation time. This is needed for the trajectory planing in simulation.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "sim_gazebo",
            default_value="false",
            description="Indicate whether robot will run in simulation.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_sensor_commands",
            default_value="false",
            description="Indicate whether robot will run in simulation.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Indicate whether robot will run in simulation.",
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
