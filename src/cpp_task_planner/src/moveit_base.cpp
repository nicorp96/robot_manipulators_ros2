#include "../include/moveit_base.h"

BaseManager::BaseManager(const rclcpp::Node::SharedPtr node, rclcpp::Logger logger) : node_(node),
                                                                                      logger_(logger),
                                                                                      moveit_cpp_ptr(std::make_shared<moveit_cpp::MoveItCpp>(node)),
                                                                                      use_sim_time(node->get_parameter("use_sim_time").as_bool()),
                                                                                      robot_model_loader(node),
                                                                                      kinematic_model(robot_model_loader.getModel()),
                                                                                      planning_scene(kinematic_model),
                                                                                      tf_buffer(std::make_shared<tf2_ros::Buffer>(std::make_shared<rclcpp::Clock>(RCL_ROS_TIME))),
                                                                                      csm(std::make_shared<planning_scene_monitor::CurrentStateMonitor>(node, kinematic_model, tf_buffer, use_sim_time)),
                                                                                      robot_state(std::make_shared<moveit::core::RobotState>(kinematic_model))
{
    moveit_cpp_ptr->getPlanningSceneMonitorNonConst()->providePlanningSceneService();
    csm->startStateMonitor();
    if (!csm->waitForCurrentState(node_->now(), 1.0))
    {
        RCLCPP_ERROR_STREAM(logger_, "Failed to fetch current robot state");
    }
}

MyManager::MyManager(const rclcpp::Node::SharedPtr node, rclcpp::Logger logger) : BaseManager(node, logger)
{
    LoadParams();
    joint_model_group = robot_state->getJointModelGroup(group_name_);
    // planning_scene.getCurrentStateNonConst().setToDefaultValues(joint_model_group, "ready");
    std::shared_ptr<moveit_cpp::PlanningComponent> arm_planning_components = std::make_shared<moveit_cpp::PlanningComponent>(group_name_, moveit_cpp_ptr);
}

void MyManager::LoadParams()
{
    RCLCPP_INFO_STREAM(logger_, "Loading Parameters");
    if (!node_->get_parameter("tool_name", tool_name_))
    {
        RCLCPP_ERROR_STREAM(logger_, "Failed to get end effector name");
        tool_name_ = "link_eef";
    }
    if (!node_->get_parameter("tool_name", ref_frame_))
    {
        RCLCPP_ERROR_STREAM(logger_, "Failed to get Pose Reference Frame");
        ref_frame_ = "link_base";
    }

    if (!node_->get_parameter("group_name", group_name_))
    {
        RCLCPP_ERROR_STREAM(logger_, "Failed to get jump_threshold Warning!!");
        group_name_ = "xarm6";
    }
}

void MyManager::run()
{
    RCLCPP_INFO_STREAM(logger_, "Running Moveit Manager");
}