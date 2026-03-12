cmake_minimum_required(VERSION 3.8)
project(pointcloud_to_laserscan_logged)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(pointcloud_to_laserscan_logged_node
  src/pointcloud_to_laserscan_logged_node.cpp
)

ament_target_dependencies(pointcloud_to_laserscan_logged_node
  rclcpp
  sensor_msgs
  std_msgs
)

install(TARGETS
  pointcloud_to_laserscan_logged_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
