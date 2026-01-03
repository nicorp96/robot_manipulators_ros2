######################################################################################
# MoveitPy Templates
#
#          Code is heavily based on the tutorials/examples of the Moveit Documentation
#          https://moveit.picknik.ai/
#
#          University of Applied Sciences, Laboratory of Autonomous Systems (LAS)
######################################################################################


import time
import rclpy
import numpy as np
from .utils.task_node import TaskNode
import moveit.planning
from moveit.planning import (
    MultiPipelinePlanRequestParameters,
    MoveItPy,
)  # must be included even if not directly used
from moveit.core.kinematic_constraints import (
    construct_joint_constraint,
)  # must be included even if not directly used
from moveit.core.robot_state import RobotState
from geometry_msgs.msg import PoseStamped, Pose
import rclpy.node
from .utils.gripper import XarmGripper, SuctionGripper, FrankaGripper
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive


class MyNode(TaskNode):
    def __init__(self):
        super().__init__("mynode")
        self.moveit = MoveItPy(node_name="moveitpy")
        # Declare expected parameters
        self.logger = self.get_logger()
        self.declare_parameter("group_name", "xarm6")  # Default group name
        self.declare_parameter("tool_name", "link_eef")  # Default tool name
        self.declare_parameter("ref_frame", "link_base")  # Default reference frame

        self._load_params()
        self.planning_scene_monitor = self.moveit.get_planning_scene_monitor()
        self.robot_model = self.moveit.get_robot_model()

        self.arm = self.moveit.get_planning_component(self.group_name)
        self.arm.set_workspace(
            min_x=-1.0, min_y=-1.0, min_z=0.0, max_x=1.0, max_y=1.0, max_z=2.0
        )
        self.run()

    def _load_params(self):
        self.group_name = self.get_parameter("group_name").value
        self.tool_name = self.get_parameter("tool_name").value
        self.ref_frame = self.get_parameter("ref_frame").value
        self.use_sim_time = self.get_parameter("use_sim_time").value
        if self.group_name == "xarm6":
            self.gripper = XarmGripper(self, self.moveit)
            self.joints_ex = np.array([0.0, -0.789, 0.0, 0.0, 0.0, 0.0])
        elif self.group_name == "ur_manipulator":
            self.gripper = SuctionGripper(self, use_sim_time=self.use_sim_time)
            self.joints_ex = np.array([0.0, -1.5184, 1.5708, -1.6057, -1.5882, 0.0])
        elif self.group_name == "fer_manipulator":
            self.gripper = FrankaGripper(
                self, self.moveit, use_sim_time=self.use_sim_time
            )
            self.joints_ex = np.array(
                [1.5708 - 0.7854, 0.0, -2.3562, 0.0, 1.5708, 0.7854]
            )

    def plan_and_execute(self, sleep_time=0.0):
        plan_result = self.arm.plan()
        if plan_result:
            self.logger.info("Executing plan")
            robot_trajectory = plan_result.trajectory
            self.moveit.execute(robot_trajectory, controllers=[])
        else:
            self.logger.error("Planning failed")
        time.sleep(sleep_time)

    def get_current_state(self):
        with self.planning_scene_monitor.read_only() as scene:
            robot_state = scene.current_state
        return robot_state

    def add_collision_object(self):
        box_pose = Pose()
        box_pose.position.x = 0.3
        box_pose.position.y = -0.22
        box_pose.position.z = 0.225
        box_size = (0.25, 0.1, 0.45)
        box = SolidPrimitive(type=SolidPrimitive.BOX, dimensions=box_size)
        c_obj = CollisionObject()
        c_obj.header.frame_id = self.ref_frame
        c_obj.id = "my_collobj"
        c_obj.primitives.append(box)
        c_obj.primitive_poses.append(box_pose)
        c_obj.operation = CollisionObject.ADD
        with self.planning_scene_monitor.read_write() as scene:
            scene.apply_collision_object(c_obj)  # apply ADD operation
            scene.current_state.update()
        self.logger.info("Collision object added")

    ##############################################################################################
    # Various ways to define a simple plan:
    ##############################################################################################

    def run(self):
        #self.add_collision_object()
        self.step1()
        self.step_gripper()
        self.step2()
        # self.step3()
        self.step1()
        self.step_gripper()
        self.logger.info(f"current state: {self.get_current_state().joint_positions}")

    def step_gripper(self):
        self.gripper.open()
        time.sleep(1.0)
        self.gripper.close()

    def step1(self):
        # 1. Use pre-defined robot configurations
        self.arm.set_goal_state(configuration_name="home")
        self.plan_and_execute()

    def step3(self):
        # 3. Plan in joint space
        robot_state = RobotState(self.robot_model)  # robot state of the whole model

        robot_state.set_joint_group_positions(
            self.group_name,
            self.joints_ex,  # np.array([0.0, -0.789, 0.0, 0.0, 0.0, 0.0])
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()

    def step2(self):
        # 2. Plan in working space
        pose_goal = PoseStamped()  # define a pose of the end effector
        pose_goal.header.frame_id = self.ref_frame
        pose_goal.pose.position.x = 0.342616
        pose_goal.pose.position.y = -0.4
        pose_goal.pose.position.z = 0.424932
        pose_goal.pose.orientation.x = 0.90883
        pose_goal.pose.orientation.y = 0.32485
        pose_goal.pose.orientation.z = 0.175742
        pose_goal.pose.orientation.w = -0.193948

        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link=self.tool_name)
        self.plan_and_execute()


def main():
    rclpy.init()
    rclpy.spin(MyNode())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
