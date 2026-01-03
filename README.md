# Multi-Robot Manipulator Control with MoveIt

This repository provides a framework for controlling multiple robot manipulators, specifically the XArm6 and Universal Robots UR5, using MoveIt. It includes configurations and launch files for real robot operation, fake robot setups for development purposes, and simulation environments.

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
- [General Information](#general-information)
    - [How to use git](#how-to-use-git)
- [Integrating and Documenting your Code](#integrating-and-documenting-your-code)
    - [Rules and Preparation](#rules-and-preparation)
    - [Submission](#submission)

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
  This package contains all the configuration and launch files required to run robotic simulations in Ignition.

### Git Submodules

The following submodules are included in the repository and provide additional resources and drivers for the robots:

- **Universal_Robots_ROS2_Description**:  
  Provides the URDFs and meshes for the Universal Robots series, specifically tailored for ROS 2.

- **Universal_Robots_ROS2_Driver**:  
  ROS 2 driver for Universal Robots manipulators. It handles communication between the robot and ROS.

- **franka_description**:  
  Provides the URDFs and meshes for the Franka Robots series, specifically tailored for ROS 2.

- **xarm_ros2**:  
  Contains simulation models, and corresponding motion planning and controlling demos of the xArm series from UFACTORY..

# Getting Started

## Create your feature branch

1. **Clone the repository:**
    ```bash
    git clone https://gitlab.lrz.de/lasim/robot_manipulators_moveit2.git
    cd robot_manipulators_moveit2
    ```

2. **Configure your git**
    ```bash
    git config --global user.email "your_hm_email@hm.edu"
    git config --global user.name "your_name"
    ```

3. **Create and Chekout to your assigned Branch:**
    Checkout to the Branch of the project
    ```bash
    git remote add origin https://gitlab.lrz.de/lasim/robot_manipulators_moveit2.git
    git checkout develop
    git pull origin develop
    git checkout -b feature/put_your_feature_branch_name_here
    ```
    This will be your main working branch where you push your changes.
    ```

We advise you to **delegate** tasks within your group instead of doing everything together.

### Important Note:
Don't create a merge request everytime you push some changes. If you work as a group on one branch only, create a merge request at the end of your term. If you work issue based, create a merge request after you have solved the task completely. For more information see section "Integrating and Documenting your Code".


4. **Init and clone the submodules:** 

    ```bash
    git submodule update --init --recursive
    ```

5. **Update the submodules from remote:** 

    ```bash
    git submodule update --remote
    ```

6. **Build the workspace robot_manipulators_moveit2:**
    ```bash
    cd ~/robot_manipulators_moveit2
    colcon build --packages-ignore realsense_gazebo_plugin xarm_gazebo
    source install/setup.bash
    ```

# Usage

## Starting XArm6

### Real Robot XArm6

1. **Launch MoveIt with the real XArm6:**
    ```bash
    ros2 launch robot_bringup xarm6_bringup.launch.py fake_controllers:=false
    ```

2. **Launch PY Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_example.launch.py use_sim_time:=false
    ```

### Fake Robot XArm6

1. **Launch MoveIt with a fake XArm6:**
    ```bash
    ros2 launch robot_bringup xarm6_bringup.launch.py fake_controllers:=true
    ```
2. **Launch PY Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_example.launch.py use_sim_time:=false robot:=xarm6_fake
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
    ros2 launch robot_bringup ur5_bringup.launch.py fake_controllers:=false
    ```
2. **Launch Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_example.launch.py robot:=ur5 ref_frame:=base_link tool_name:=tool0 group_name:=ur_manipulator use_sim_time:=false
    ```

### Fake Robot UR5

1. **Launch MoveIt with a fake UR5:**
    ```bash
    ros2 launch robot_bringup ur5_bringup.launch.py fake_controllers:=true
    ```
2. **Launch PY Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_example.launch.py robot:=ur5 ref_frame:=base_link tool_name:=tool0 group_name:=ur_manipulator use_sim_time:=false
    ```

### Simulation UR5

1. **Launch Gazebo with UR5 and MoveIt:**
    ```bash
    ros2 launch robot_bringup ur5_simulation.launch.py
    ```
2. **Control the simulated UR5 in Gazebo with PY Task Planner:**
    ```bash
    ros2 launch py_task_planner moveitpy_example.launch.py robot:=ur5 ref_frame:=base_link tool_name:=tool0 group_name:=ur_manipulator use_sim_time:=true
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
    ros2 launch robot_bringup franka_simulation.launch.py
    ```
2. **Launch PY Task Planner Algorithm:**
    ```bash
    ros2 launch py_task_planner moveitpy_example.launch.py use_sim_time:=true robot:=franka group_name:=fer_manipulator tool_name:=fer_hand ref_frame:=fer_link0
    ```

# General Information
## How to use git
You are encouraged to document your whole workflow by continuously pushing to your feature branch. This makes it easier for us (and your teammates :wink:) to understand what you are doing.
Your most used commands will be:
```bash
git add file1 file2 # stage specific files 
git add . # stage all files under the current directory
git commit -m "your commit message" # commit your changes. "-m" directly appends the commit message
git push # push your changes to your branch
git pull # pull changes from remote repository
git branch # shows all branches, asteriks marks the branch you're on
git checkout branch1 # switch to a different branch
git checkout -b new_feature # create a new branch and switch to it
git status # show the current state of your branch
```
Following might be of use, but you probably already know what you're doing by then:
```bash
git stash push # stash uncommited changes and revert your repo
git stash pop # merge changes saved in your latest stash with current branch. Your stash gets deleted
git reflog # show your git workflow
git reset # reset your branch to a specific state
```
For more indepth information, please see https://git-scm.com/docs/gittutorial

# Integrating and Documenting your Code 
## Rules and Preparation
- Only push **unbuilt!** code i.e. only "git add" the changes located in `robot_manipulators_moveit2/src`
- Make useful commit messages, stating what you've done or changed
- Python: make sure your code is well documented and adheres to the [PEP8](https://peps.python.org/pep-0008/) conventions 
- C++: use a [clang formatter](https://clang.llvm.org/docs/ClangFormat.html), which can be installed via Marketplace when using VS Code.
- Make sure to include a `README.md` under your package folder explaining how your package works. Include third party requirements as well. Either as a requirements.txt or in the `README.md` directly via pip install commands. The documentation will be part of your grading.
## Submission
Push your final changes to your feature branch and create a merge request. Merge requests will be retargeted to the "develop" branch. If "develop" is not chosen automatically, please do so manually. Git will check for merge conflicts, which you will have to resolve manually. If you've created a new package, there shouldn't be any conflicts at all, since it's contained in a new folder in `/src/`.

Use your project and group name as merge commit e.g **"robot_manipulators_abgabe_gruppeX_WS2024"**.

Don't push on main.