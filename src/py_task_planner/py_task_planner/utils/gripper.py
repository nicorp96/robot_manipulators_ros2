import rclpy
import rclpy.node
import ur_msgs
import ur_msgs.srv
from moveit.planning import (
    MultiPipelinePlanRequestParameters,
    MoveItPy,
)
import time


class GripperBase:
    def __init__(self, node: rclpy.node.Node, use_sim_time) -> None:
        self._node = node
        self.use_sim_time = use_sim_time
        self.logger = self._node.get_logger()
        self.setup()

    def setup(self):
        raise NotImplemented

    def open(self):
        raise NotImplemented

    def close(self):
        raise NotImplemented


class SuctionGripper(GripperBase):
    def __init__(self, node: rclpy.node.Node, use_sim_time=False) -> None:
        super().__init__(node, use_sim_time)
        self._io_client = self._node.create_client(
            srv_type=ur_msgs.srv.SetIO, srv_name="io_and_status_controller/set_io"
        )

    def setup(self):
        self.logger.info("Setting up Suction Gripper")

    def open(self):
        if self.use_sim_time:
            self.logger.info("Suction Gripper SIMULATION ON")
        else:
            self.logger.info("Suction Gripper ON ...")
            io_request = ur_msgs.srv.SetIO.Request()
            io_request.fun = 1
            io_request.pin = 4
            io_request.state = 1.0
            while not self._io_client.wait_for_service():
                if not rclpy.ok():
                    self.logger.error(
                        "Interrupted while waiting for the service. Exiting."
                    )
                self.logger.info("Service not available, waiting again..")

            result = self._io_client.call_async(io_request)

    def close(self):
        if self.use_sim_time:
            self.logger.info("Suction Gripper SIMULATION ON")
        else:
            self.logger.info("Suction Gripper OFF ...")
            io_request = ur_msgs.srv.SetIO.Request()
            io_request.fun = 1
            io_request.pin = 4
            io_request.state = 0.0
            while not self._io_client.wait_for_service():
                if not rclpy.ok():
                    self.logger.error(
                        "Interrupted while waiting for the service. Exiting."
                    )
                self.logger.info("Service not available, waiting again..")

            result = self._io_client.call_async(io_request)


class XarmGripper(GripperBase):
    def __init__(
        self, node: rclpy.node.Node, moveit: MoveItPy, use_sim_time=False
    ) -> None:
        super().__init__(node, use_sim_time)
        self.moveit = moveit
        self.gripper_moveit = self.moveit.get_planning_component("xarm_gripper")

    def setup(self):
        self.logger.info("Setting up XarmGripper Gripper")
        self.sleep_time = 2.0

    def open(self):
        self.gripper_moveit.set_goal_state(configuration_name="open")
        plan_result = self.gripper_moveit.plan()
        if plan_result:
            self.logger.info("Executing Gripper plan")
            robot_trajectory = plan_result.trajectory
            self.moveit.execute(robot_trajectory, controllers=[])
        else:
            self.logger.error("Planning Gripper failed")
        time.sleep(self.sleep_time)

    def close(self):
        self.gripper_moveit.set_goal_state(configuration_name="close")
        plan_result = self.gripper_moveit.plan()
        if plan_result:
            # self.logger.info("Executing plan")
            robot_trajectory = plan_result.trajectory
            self.moveit.execute(robot_trajectory, controllers=[])
        else:
            self.logger.error("Planning Gripper failed")
        time.sleep(self.sleep_time)


class FrankaGripper(GripperBase):
    def __init__(
        self, node: rclpy.node.Node, moveit: MoveItPy, use_sim_time=False
    ) -> None:
        super().__init__(node, use_sim_time)
        self.moveit = moveit
        self.gripper_moveit = self.moveit.get_planning_component("hand")

    def setup(self):
        self.logger.info("Setting up FrankaGripper Gripper")
        self.sleep_time = 2.0

    def open(self):
        self.gripper_moveit.set_goal_state(configuration_name="open")
        plan_result = self.gripper_moveit.plan()
        if plan_result:
            self.logger.info("Executing Gripper plan")
            robot_trajectory = plan_result.trajectory
            self.moveit.execute(robot_trajectory, controllers=[])
        else:
            self.logger.error("Planning Gripper failed")
        time.sleep(self.sleep_time)

    def close(self):
        self.gripper_moveit.set_goal_state(configuration_name="close")
        plan_result = self.gripper_moveit.plan()
        if plan_result:
            # self.logger.info("Executing plan")
            robot_trajectory = plan_result.trajectory
            self.moveit.execute(robot_trajectory, controllers=[])
        else:
            self.logger.error("Planning Gripper failed")
        time.sleep(self.sleep_time)
