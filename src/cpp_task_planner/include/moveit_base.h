///////////////////////////////////////////////////////////////////////////////////////
// MoveitCpp Templates
//
//          Code is heavily based on the tutorials/examples of the Moveit Documentation
//          https://moveit.picknik.ai/
//
//          University of Applied Sciences, Laboratory of Autonomous Systems (LAS)
///////////////////////////////////////////////////////////////////////////////////////

#include <rclcpp/rclcpp.hpp>
#include <moveit/planning_scene/planning_scene.h>
#include <moveit/robot_model_loader/robot_model_loader.h>
#include <moveit/robot_model/robot_model.h>
#include <moveit/robot_state/robot_state.h>
#include <moveit/planning_scene_monitor/planning_scene_monitor.h>
#include <moveit/moveit_cpp/moveit_cpp.h>
#include <moveit/moveit_cpp/planning_component.h>
#include <moveit/kinematic_constraints/utils.h>

class BaseManager
{
protected:
    const rclcpp::Node::SharedPtr node_;
    rclcpp::Logger logger_;
    const std::shared_ptr<moveit_cpp::MoveItCpp> moveit_cpp_ptr;
    const bool use_sim_time;
    robot_model_loader::RobotModelLoader robot_model_loader;
    const moveit::core::RobotModelPtr &kinematic_model;
    planning_scene::PlanningScene planning_scene;
    std::shared_ptr<tf2_ros::Buffer> tf_buffer;
    planning_scene_monitor::CurrentStateMonitorPtr csm;
    std::shared_ptr<moveit::core::RobotState> robot_state;
    const moveit::core::JointModelGroup *joint_model_group;

    BaseManager(const rclcpp::Node::SharedPtr node, rclcpp::Logger logger);
    virtual void LoadParams() = 0;
};

class MyManager : public BaseManager
{
private:
    const std::vector<std::string> controllers{1, "arm_controller"};
    std::shared_ptr<moveit_cpp::PlanningComponent> arm_planning_components;
    std::string tool_name_, ref_frame_, group_name_;
    const moveit::core::JointModelGroup *joint_model_group;

public:
    MyManager(const rclcpp::Node::SharedPtr node, rclcpp::Logger logger);
    void LoadParams();
    void run();
};
