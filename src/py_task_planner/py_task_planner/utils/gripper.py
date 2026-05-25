import rclpy
import rclpy.node
import ur_msgs
import ur_msgs.srv
from moveit.planning import (
    MultiPipelinePlanRequestParameters,
    MoveItPy,
)
import time
import serial
from serial.tools import list_ports


class GripperBase:
    def __init__(self, node: rclpy.node.Node, use_sim_time) -> None:
        self._node = node
        self.use_sim_time = use_sim_time
        self.logger = self._node.get_logger()
        self.suction_active = False
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
            self.logger.info("Suction Gripper SIMULATION OFF")
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

class AdaptiveSuctionGripper(GripperBase):
    def __init__(self, node: rclpy.node.Node, use_sim_time=False) -> None:
        super().__init__(node, use_sim_time)
        self._io_client = self._node.create_client(
            srv_type=ur_msgs.srv.SetIO, srv_name="io_and_status_controller/set_io"
        )

    def setup(self):
        self.logger.info("Setting up Suction Gripper...")

        if not self.use_sim_time:
            TEENSY_BAUDRATE = 115200
            TEENSY_TIMEOUT = 1.0

            TEENSY_VID = 0x16C0
            TEENSY_PID = 0x0483

            TEENSY_PORT = None
            while(TEENSY_PORT == None):
                for port in list_ports.comports():
                    if port.vid == TEENSY_VID:
                        TEENSY_PORT = port.device
                        break
                self.logger.info("    Searching for Teensy. Check connection.")
                time.sleep(1.0)

            self.teensySerial = serial.Serial(str(TEENSY_PORT), TEENSY_BAUDRATE, timeout=TEENSY_TIMEOUT)
            self.logger.info(f"    Connected to Teensy on \"{TEENSY_PORT}\"")

        self.logger.info("Finished setting up Suction Gripper successfully.")

    # Schaltet die Pumpe AN
    def close(self):
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
            self.suction_active = True
            result = self._io_client.call_async(io_request)

    # Schaltet die Pumpe AUS
    def open(self):
        if self.use_sim_time:
            self.logger.info("Suction Gripper SIMULATION OFF")
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
            self.suction_active = False
            result = self._io_client.call_async(io_request)

    def setAllAngles(self, a1: int, a2: int, a3: int, a4: int):
        if self.suction_active:
            self.logger.warn("Do not change gripper while suction is on!")
        else:
            cmd = f"SET ALL {a1} {a2} {a3} {a4}\n"
            self.teensySerial.write(cmd.encode())
            time.sleep(2.0)
    
    def getAllAngles(self):
        self.ser.write(b"GET ALL\n")

        result = self.ser.readline().decode().strip()

        parts = result.split()
        angles = [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]
                
        return angles


class AdaptiveSuctionGripper(GripperBase):
    def __init__(self, node: rclpy.node.Node, use_sim_time=False) -> None:
        super().__init__(node, use_sim_time)
        self._io_client = self._node.create_client(
            srv_type=ur_msgs.srv.SetIO, srv_name="io_and_status_controller/set_io"
        )

    def setup(self):
        self.logger.info("Setting up Suction Gripper...")

        if not self.use_sim_time:
            TEENSY_BAUDRATE = 115200
            TEENSY_TIMEOUT = 1.0

            TEENSY_VID = 0x16C0
            TEENSY_PID = 0x0483

            TEENSY_PORT = None
            while TEENSY_PORT == None:
                for port in list_ports.comports():
                    if port.vid == TEENSY_VID:
                        TEENSY_PORT = port.device
                        break
                self.logger.info("    Searching for Teensy. Check connection.")
                time.sleep(1.0)

            self.teensySerial = serial.Serial(
                str(TEENSY_PORT), TEENSY_BAUDRATE, timeout=TEENSY_TIMEOUT
            )
            self.logger.info(f'    Connected to Teensy on "{TEENSY_PORT}"')

        self.logger.info("Finished setting up Suction Gripper successfully.")

    # Schaltet die Pumpe AN
    def close(self):
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
            self.suction_active = True
            result = self._io_client.call_async(io_request)

    # Schaltet die Pumpe AUS
    def open(self):
        if self.use_sim_time:
            self.logger.info("Suction Gripper SIMULATION OFF")
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
            self.suction_active = False
            result = self._io_client.call_async(io_request)

    def setAllAngles(self, a1: int, a2: int, a3: int, a4: int):
        if self.suction_active:
            self.logger.warn("Do not change gripper while suction is on!")
        else:
            cmd = f"SET ALL {a1} {a2} {a3} {a4}\n"
            self.teensySerial.write(cmd.encode())
            time.sleep(2.0)

    def getAllAngles(self):
        self.ser.write(b"GET ALL\n")

        result = self.ser.readline().decode().strip()

        parts = result.split()
        angles = [int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])]

        return angles


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
