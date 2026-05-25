# Multi-Robot Manipulator Control with MoveIt

This repository is a ROS 2 workspace showcasing MoveIt2-based robot manipulation configurations for XArm6, UR5, and Franka. It includes robot descriptions, MoveIt configuration, launch files, and task planner examples for real robots, fake controllers, and simulation setups.

# Table of Contents
- [Packages Overview](#packages-overview)
- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Starting XArm6](#starting-xarm6)
    - [Real Robot](#real-robot-xarm6)
    - [Fake Robot](#fake-robot-xarm6)
    - [Simulation](#simulation-xarm6)
  - [Starting UR5](#starting-ur5)
    - [Real Robot](#real-robot-ur5)
    - [Fake Robot](#fake-robot-ur5)
    - [Simulation](#simulation-ur5)
  - [Starting Franka](#starting-franka)
    - [Real Robot](#real-robot-franka)
    - [Fake Robot](#fake-robot-franka)
    - [Simulation](#simulation-franka)

# Packages Overview

## Core Packages

- **robot_bringup**:  
  This package contains all the necessary launch files required to operate the robotic manipulator in both simulation and real-world environments.

- **robot_descriptions**:  
  This package includes the URDF files, configuration files, and other resources essential for the XArm6 and UR5 robots. It provides the robot models and configuration parameters necessary for their operation.

- **py_task_planner**:  
  This package implements the MoveIt2 interface in Python and serves as a reference for developing and executing task planning algorithms to control the robots. Contributors are advised to ensure that any new code added to this package, or any newly created packages, maintains compatibility with all manipulators.

- **robot_moveit_config**:  
  This package comprises all configuration and launch files needed to initialize the MoveIt2 interface for the robots. It supports both real-world operations and simulations.

- **robot_simulation**:  
  This package contains all the configuration and launch files required to run robotic simulations.

### Git Submodules

The following submodules are included in the repository and provide additional resources and drivers for the robots:

- **franka_description**:  
  Provides the URDFs and meshes for the Franka Robots series, specifically tailored for ROS 2.

- **xarm_ros2**:  
  Contains simulation models, and corresponding motion planning and controlling demos of the xArm series from UFACTORY..

# Getting Started

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://gitlab.lrz.de/lasim/robot_manipulators_moveit2.git
    cd robot_manipulators_moveit2
    ```

2. **Configure your git identity if needed:**
    ```bash
    git config --global user.email "your_email@example.com"
    git config --global user.name "Your Name"
    ```

3. **Create a working branch:**
    ```bash
    git checkout develop
    git pull origin develop
    git checkout -b feature/your-feature-name
    ```

4. **Init and clone the submodules:** 

    ```bash
    git submodule update --init --recursive
    ```

5. **Update the submodules from remote:** 

    ```bash
    git pull --recurse-submodules
    ```
6. **Set the workspace robot_manipulators_moveit2:**

    ```bash
    set_ws ~/robot_manipulators_moveit2
    ```

7. **Build the workspace robot_manipulators_moveit2:**
    ```bash
    bld
    ```

# Usage

## Starting XArm6

### Real Robot XArm6

1. **Launch MoveIt with the real XArm6:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=xarm6
    ```

2. **Launch PY Task Planner Algorithm (with all other robots):**
    ```bash
    ros2 launch py_task_planner moveitpy_all_example.launch.py robot:=xarm6
    ```

3. **Launch PY Task Planner Example Algorithm (only xarm):**
    ```bash
    ros2 launch py_task_planner moveitpy_xarm_example.launch.py fake_controller:=false
    ```

### Fake Robot XArm6

1. **Launch MoveIt with a fake XArm6:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=xarm6_fake
    ```
2.  **Launch PY Task Planner Algorithm (with all other robots):**
    ```bash
    ros2 launch py_task_planner moveitpy_all_example.launch.py robot:=xarm6_fake
    ```
    
3. **Launch PY Task Planner Example Algorithm (only xarm):**
    ```bash
    ros2 launch py_task_planner moveitpy_xarm_example.launch.py fake_controller:=true
    ```


### Simple MoveIt example template of a task for UR5.
1. **Launch the real UR5 Driver:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=ur5
    ```
2. **Launch PY Control: (Example)**
    ```bash
    ros2 launch py_task_planner moveitpy_ur5_example.launch.py
    ```
    
**Important Information: Initial Pose**
The initial pose of the robot in simulation setup can be changed within xarm6.ros2_control.xacro, please contact us for guidance.


### Simulation XArm6 (TBD)

1. **Launch Gazebo with XArm6 and MoveIt:**
    ```bash
    TBD
    ```
2. **Control the simulated XArm6 in Gazebo:**
    TBD

## Starting UR5

### Real Robot UR5 (Moveit)

1. **Launch the real UR5 Driver:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=ur5
    ```
2. **Launch Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_all_example.launch.py robot:=ur5
    ```

### Real Robot UR5 with Adaptive Suction Gripper (Moveit)

1. **Launch the real UR5 Driver:**
    ```bash
    ros2 launch robot_bringup ur5_bringup.launch.py fake_controllers:=false
    ```
3. **Launch PY Suction Control: (Example)**
    ```bash
    ros2 launch py_task_planner moveitpy_suction.launch.py robot:=ur5 ref_frame:=base_link tool_name:=tool0 group_name:=ur_manipulator use_sim_time:=false
    ```

### Fake Robot UR5

1. **Launch MoveIt with a fake UR5:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=ur5_fake
    ```
2. **Launch PY Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_all_example.launch.py robot:=ur5
    ```


### Simulation UR5

1. **Launch Gazebo with UR5 and MoveIt:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=ur5_sim
    ```
2. **Control the simulated UR5 in Gazebo with PY Task Planner:**
    ```bash
    ros2 launch py_task_planner moveitpy_all_example.launch.py robot:=ur5_sim
    ```

### Real Robot UR5 with Adaptive Suction Gripper (Moveit)

1. **Launch the real UR5 Driver:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=ur5
    ```
2. **Launch PY Suction Control: (Example)**
    ```bash
    ros2 launch py_task_planner moveitpy_suction.launch.py
    ```

### Simple MoveIt example template of a task for UR5.
1. **Launch the real UR5 Driver:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=ur5
    ```
2. **Launch PY Control: (Example)**
    ```bash
    ros2 launch py_task_planner moveitpy_ur5_example.launch.py
    ```

## Starting Franka

### Real Robot Franka (TBD)

1. **Launch MoveIt with the real Franka:**
    ```bash
    TBD
    ```

2. **Launch PY Task Planner Algorithm:**
    ```bash
    TBD
    ```

### Fake Robot Franka (TBD)

1. **Launch MoveIt with a fake Franka:**
    ```bash
    TBD
    ```
2. **Launch PY Task Planner Algorithm:**
    ```bash
    TBD
    ```

### Simulation Franka (TBD)

1. **Launch Gazebo with Franka and MoveIt:**
    ```bash
    ros2 launch robot_bringup bringup.launch.py robot:=franka_sim
    ```
2. **Launch PY Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_all_example.launch.py robot:=franka_sim
    ```