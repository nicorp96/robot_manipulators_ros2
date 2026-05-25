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
from rclpy.logging import get_logger
import moveit.planning
from moveit.planning import MultiPipelinePlanRequestParameters             # must be included even if not directly used
from moveit.core.kinematic_constraints import construct_joint_constraint   # must be included even if not directly used

from geometry_msgs.msg import Pose
from moveit.core.robot_state import RobotState
from geometry_msgs.msg import PoseStamped

GROUP_NAME= "xarm6"
REF_FRAME = "link_base"
TOOL_NAME= "link_eef"

class MoveItPy(moveit.planning.MoveItPy):
    def plan_and_execute(self, planning_component, logger, single_plan_parameters=None,
                        multi_plan_parameters=None, sleep_time=0.0):
        """Helper function to plan and execute a motion."""
        
        # plan to goal
        logger.info("Planning trajectory")
        if multi_plan_parameters is not None:
            plan_result = planning_component.plan(multi_plan_parameters=multi_plan_parameters)
        elif single_plan_parameters is not None:
            plan_result = planning_component.plan(single_plan_parameters=single_plan_parameters)
        else:
            plan_result = planning_component.plan()

        # execute the plan
        if plan_result:
            logger.info("Executing plan")
            robot_trajectory = plan_result.trajectory
            self.execute(robot_trajectory, controllers=[])
        else:
            logger.error("Planning failed")

        time.sleep(sleep_time)


def main():
    
    # It would be way better to put everything in a class, but we want to stick as close as possible 
    # to the official tutorial.
    
    rclpy.init()
    logger = get_logger(__name__)
    logger.info('MoveItPy template.')
    
    # instantiate MoveItPy and get planning component
    moveit = MoveItPy(node_name='moveitpy')
    arm = moveit.get_planning_component(GROUP_NAME)
    arm.set_workspace(min_x=-1.0, min_y=-1.0, min_z=0.0, max_x=1.0, max_y=1.0, max_z=2.0)
    robot_model = moveit.get_robot_model()
    
    ##############################################################################################
    # Various ways to define a simple plan:
    ##############################################################################################
    # 1. Use pre-defined robot configurations
    arm.set_goal_state(configuration_name="home")
    moveit.plan_and_execute(arm, logger, sleep_time=3.0)
              # the execution process automatically checks if the start state of the plan is very close to the actual state
    
    ##############################################################################################
    # 2. Plan in joint space
    robot_state = RobotState(robot_model)                 # robot state of the whole model
    robot_state.set_joint_group_positions(GROUP_NAME, np.array([0.0, -1.5184, 1.5708, -1.6057, -1.5882, 0.0]))
    arm.set_start_state_to_current_state()
    arm.set_goal_state(robot_state=robot_state)
    moveit.plan_and_execute(arm, logger, sleep_time=5.0)         
    
    ##############################################################################################
    # 3. Plan in working space
    pose_goal = PoseStamped()                             # define a pose of the end effector
    pose_goal.header.frame_id = REF_FRAME
    pose_goal.pose.position.x =  0.342616
    pose_goal.pose.position.y = -0.269653
    pose_goal.pose.position.z =  0.424932
    pose_goal.pose.orientation.x =  0.90883
    pose_goal.pose.orientation.y = 0.32485
    pose_goal.pose.orientation.z =  0.175742
    pose_goal.pose.orientation.w = -0.193948
    arm.set_start_state_to_current_state()
    arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link=TOOL_NAME)
    moveit.plan_and_execute(arm, logger, sleep_time=5.0)
    
    ##############################################################################################
    # Get the current state
    with moveit.get_planning_scene_monitor().read_only() as scene:
        robot_state = scene.current_state
    logger.info(f'current state: {robot_state.joint_positions}')

    
    arm.set_goal_state(configuration_name="home")
    moveit.plan_and_execute(arm, logger, sleep_time=3.0)
    
    # There will be some warnings indicating that we should delete all objects manually 
    # which were constructed in this code.