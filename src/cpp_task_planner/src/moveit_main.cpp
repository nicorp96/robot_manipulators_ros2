#include <rclcpp/rclcpp.hpp>
#include "../include/moveit_base.h"

const std::string node_name = "moveitcpp_first_node";

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::Node::SharedPtr node = rclcpp::Node::make_shared(node_name,
                                                             rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));

    // We spin up a SingleThreadedExecutor for the current state monitor to get information
    // about the robot's state.
    rclcpp::executors::SingleThreadedExecutor executor;
    executor.add_node(node);
    std::thread([&executor]()
                { executor.spin(); })
        .detach();

    auto const logger = rclcpp::get_logger(node_name);
    auto manager = MyManager(node, logger);
    manager.run();

    rclcpp::shutdown();
    return 0;
}