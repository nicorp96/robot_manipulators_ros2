import os
import yaml

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)

from launch.launch_description_sources import PythonLaunchDescriptionSource

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


def launch_setup(context, *args, **kwargs):
    launch_rviz = LaunchConfiguration("launch_rviz")
    warehouse_sqlite_path = LaunchConfiguration("warehouse_sqlite_path")
    use_sim_time = LaunchConfiguration("use_sim_time")
    publish_robot_description_semantic = LaunchConfiguration(
        "publish_robot_description_semantic"
    )
    no_gui_ctrl = LaunchConfiguration("no_gui_ctrl")
    fake_controller = LaunchConfiguration("fake_controller").perform(context)

    robot_description_pkg_dir = get_package_share_directory("robot_descriptions")
    robot_config_pkg_dir = get_package_share_directory("robot_moveit_config")
    urdf_file_path = os.path.join(robot_description_pkg_dir, "urdf/xarm6.urdf.xacro")
    if fake_controller.lower() == "true":
        mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotFakeSystemHardware",
            "robot_ip": "",
        }
        controllers = ["xarm6_traj_controller", "xarm_gripper_traj_controller"]
        ros2_control_params = os.path.join(
            robot_config_pkg_dir, "config/xarm/xarm6_controllers.yaml"
        )
        trajectory_exc_ctrl = "config/xarm/moveit_controllers.yaml"
    else:
        mappings = {
            "ros2_control_plugin": "uf_robot_hardware/UFRobotSystemHardware",
            "robot_ip": "192.168.20.208",
        }
        controllers = ["xarm6_traj_controller"]

        ros2_control_params = os.path.join(
            robot_config_pkg_dir, "config/xarm/xarm6_controllers_real.yaml"
        )
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
        .to_moveit_configs()
    )

    robot_description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("xarm_description"),
                    "launch",
                    "_robot_description.launch.py",
                ]
            )
        ),
        launch_arguments={
            "robot_description": yaml.dump(moveit_config.robot_description),
        }.items(),
    )

    warehouse_ros_config = {
        "warehouse_plugin": "warehouse_ros_sqlite::DatabaseConnection",
        "warehouse_host": warehouse_sqlite_path,
    }

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            warehouse_ros_config,
            {
                "use_sim_time": use_sim_time,
                "publish_robot_description_semantic": publish_robot_description_semantic,
            },
        ],
    )

    robot_planner_node_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("xarm_planner"), "launch", "_robot_planner.launch.py"]
            )
        ),
        condition=IfCondition(no_gui_ctrl),
        launch_arguments={
            "moveit_config_dump": moveit_config,
        }.items(),
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("robot_moveit_config"), "rviz", "plannerxarm.rviz"]
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

    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    ros2_control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("xarm_controller"),
                    "launch",
                    "_ros2_control.launch.py",
                ]
            )
        ),
        launch_arguments={
            "robot_description": yaml.dump(moveit_config.robot_description),
            "ros2_control_params": ros2_control_params,
        }.items(),
    )
    nodes = [
        robot_description_launch,
        move_group_node,
        robot_planner_node_launch,
        joint_state_broadcaster,
        ros2_control_launch,
    ]
    for controller in controllers:
        nodes.append(
            Node(
                package="controller_manager",
                executable="spawner",
                output="screen",
                arguments=[
                    controller,
                    "--controller-manager",
                    "/controller_manager",
                ],
            )
        )
    nodes.append(rviz_node)
    return nodes


def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "launch_rviz", default_value="true", description="Launch RViz?"
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "warehouse_sqlite_path",
            default_value=os.path.expanduser("~/.ros/warehouse_ros.sqlite"),
            description="Path where the warehouse database should be stored",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Using or not time from simulation",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "publish_robot_description_semantic",
            default_value="true",
            description="MoveGroup publishes robot description semantic",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "no_gui_ctrl",
            default_value="false",
            description="no gui ctrl",
        )
    )
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
