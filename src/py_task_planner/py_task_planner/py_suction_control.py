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
from .utils.gripper import XarmGripper, SuctionGripper, FrankaGripper, AdaptiveSuctionGripper
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

from sensor_msgs.msg import Joy


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
        # self.run()
        # -------------------------------------

        self.joy_sub = self.create_subscription(Joy, 'joy', self.joystick_callback, 10)
        self.joy_sub

        self.pumpe_an = False

        self.demo()


    def _load_params(self):
        self.group_name = self.get_parameter("group_name").value
        self.tool_name = self.get_parameter("tool_name").value
        self.ref_frame = self.get_parameter("ref_frame").value
        self.use_sim_time = self.get_parameter("use_sim_time").value
        if self.group_name == "xarm6":
            self.gripper = XarmGripper(self, self.moveit)
            self.joints_ex = np.array([0.0, -0.789, 0.0, 0.0, 0.0, 0.0])
        elif self.group_name == "ur_manipulator":
            self.gripper = AdaptiveSuctionGripper(self, use_sim_time=self.use_sim_time)
            self.gripper.setup()
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

    def step1(self):
        # 1. Use pre-defined robot configurations
        self.arm.set_goal_state(configuration_name="home")
        self.plan_and_execute()

    def step2(self):
        # 2. Plan in working space
        pose_goal = PoseStamped()  # define a pose of the end effector
        pose_goal.header.frame_id = self.ref_frame
        pose_goal.pose.position.x = 0.5
        pose_goal.pose.position.y = 0.0
        pose_goal.pose.position.z = 0.5
        pose_goal.pose.orientation.x = 0.0
        pose_goal.pose.orientation.y = 1.0
        pose_goal.pose.orientation.z = 0.0
        pose_goal.pose.orientation.w = 0.0

        self.gripper.setAllAngles(10,10,10,10)

        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link=self.tool_name)
        self.plan_and_execute()

    def joystick_callback(self, msg):
        axes = msg.axes
        buttons = msg.buttons

        neue_Pose = False

        for x in (0,1,3,4):
            if axes[x] != 0.0:
                neue_Pose = True
                break

        if buttons[8] == 1:
            if self.pumpe_an:
                self.gripper.open()
                self.pumpe_an = False
            else:
                self.gripper.close()
                self.pumpe_an = True

        if neue_Pose:
            pose_current = self.get_current_state().get_pose(self.tool_name)
            # alternativ: pose_current = self.get_current_state().get_pose('wrist_3_link')
            pose_goal = PoseStamped()  # define a pose of the end effector
            pose_goal.header.frame_id = self.ref_frame
            pose_goal.pose.position.x = (axes[0] * -0.05) + pose_current.position.x
            pose_goal.pose.position.y = (axes[1] * 0.05) + pose_current.position.y
            pose_goal.pose.position.z = (axes[4] * 0.05) + pose_current.position.z
            pose_goal.pose.orientation.x = pose_current.orientation.x
            pose_goal.pose.orientation.y = pose_current.orientation.y
            # pose_goal.pose.orientation.z = (axes[3] * -0.1) + pose_current.orientation.z
            pose_goal.pose.orientation.z = pose_current.orientation.z
            pose_goal.pose.orientation.w = pose_current.orientation.w

            self.arm.set_start_state_to_current_state()
            self.arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link=self.tool_name)
            self.plan_and_execute()

    def demo(self):
        robot_state = RobotState(self.robot_model)  # robot state of the whole model
        
        """Grosse Kiste"""

        joints = np.array([135.08, -74.40, 46.90, -62.66, -88.10, 6.6]) #Angles in Degree
        joints_rad = np.deg2rad(joints) #Convert to Rad
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.setAllAngles(120,120,120,120)

        joints = np.array([142.08, -53.40, 55.90, -93.66, -92.10, 6.6])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.close()
        time.sleep(2)

        joints = np.array([141.22, -58.40, 50.30, -83.66, -92.10, 6.6])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        joints = np.array([141, -80, 42, -144, -92, 7])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        joints = np.array([141, -80, 43, -83, -92, -90])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        joints = np.array([130.74, -90.40, 104.42, -103.20, -88.71, -90.38])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.open()

        """Kleine Kiste"""

        joints = np.array([130.74, -105.40, 80.42, -103.20, -88.71, -90.38])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------


        joints = np.array([84.0, -47.0, 51.0, -97.0, -88.0, -90.0])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.setAllAngles(30,30,30,30)
        time.sleep(1)

        joints = np.array([84.75, -44.09, 51.60, -97.25, -88.88, -92.94])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.close()
        time.sleep(2)

        joints = np.array([84.75, -62.09, 51.60, -93.25, -88.88, -92.94])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        joints = np.array([130.75, -77.09, 55.60, -75.25, -90.88, -48.94])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        joints = np.array([130.60, -77.52, 67.17, -78.46, -90.88, -47.86])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.open()

        """RAD"""

        joints = np.array([183.75, -98.09, 66.60, -65.25, -90.88, -48.94])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.setAllAngles(5,5,5,5)
        time.sleep(1)

        joints = np.array([189.18, -64.58, 105.75, -131.28, -88.60, -48.76])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.close()
        time.sleep(2)

        joints = np.array([172.75, -81.09, 55.60, -75.25, -88.88, -48.94])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        joints = np.array([130.75, -77.09, 61.60, -75.25, -90.88, -65.94])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------
        
        self.gripper.open()

        joints = np.array([132.58, -73.77, 53.56, -69.92, -90.53, -65.20])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------


        """FIGRUEN MACHEN"""
        joints = np.array([132.75, -76.09, 32.60, -46.25, -90.88, -48.94])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        joints = np.array([132.60, -74.64, 32.53, -45.72, 0.0, -90.0])  
        joints_rad = np.deg2rad(joints) 
        robot_state.set_joint_group_positions(
            self.group_name,
            joints_rad,
        )
        self.arm.set_start_state_to_current_state()
        self.arm.set_goal_state(robot_state=robot_state)
        self.plan_and_execute()
        # -----------------------------------

        self.gripper.setAllAngles(180,180,180,180)
        self.gripper.setAllAngles(0,180,180,180)
        self.gripper.setAllAngles(0,0,180,180)
        self.gripper.setAllAngles(0,0,0,180)
        self.gripper.setAllAngles(0,0,0,0)    
        self.gripper.setAllAngles(65,160,70,150)
        self.gripper.setAllAngles(150,70,160,80)    

def main():
    rclpy.init()
    rclpy.spin(MyNode())
    rclpy.shutdown()

if __name__ == "__main__":
    main()
