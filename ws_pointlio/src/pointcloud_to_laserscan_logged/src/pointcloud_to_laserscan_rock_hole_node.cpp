#include <cmath>
#include <limits>
#include <memory>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/point_cloud2_iterator.hpp"

class PointCloudToLaserScanLoggedNode : public rclcpp::Node
{
public:
  PointCloudToLaserScanLoggedNode()
  : Node("pointcloud_to_laserscan_logged")
  {
    input_topic_ = this->declare_parameter<std::string>("input_topic", "/cloud_in");
    output_topic_ = this->declare_parameter<std::string>("output_topic", "/scan");

    // Legacy height band. These are now interpreted relative to the expected floor plane.
    // Points in this band are treated as normal scan/floor returns.
    min_height_ = this->declare_parameter<double>("min_height", -0.2);
    max_height_ = this->declare_parameter<double>("max_height", 0.2);

    // Expected floor plane in the cloud frame:
    //   expected_floor_z = floor_z_offset + floor_slope_x * x + floor_slope_y * y
    // If your cloud is already in base_link/map with Z up, leave slopes at 0.
    // If your cloud is still in a tilted lidar frame, use floor_slope_x to compensate.
    // For a lidar pitched down 15 deg, a first guess is floor_slope_x = -tan(15 deg) = -0.268.
    floor_z_offset_ = this->declare_parameter<double>("floor_z_offset", 0.0);
    floor_slope_x_ = this->declare_parameter<double>("floor_slope_x", 0.0);
    floor_slope_y_ = this->declare_parameter<double>("floor_slope_y", 0.0);

    // Include rocks as positive obstacles above the estimated floor.
    detect_rocks_ = this->declare_parameter<bool>("detect_rocks", true);
    rock_min_height_ = this->declare_parameter<double>("rock_min_height", 0.15);
    rock_max_height_ = this->declare_parameter<double>("rock_max_height", 1.00);

    // Include holes/drop-offs as negative obstacles below the estimated floor.
    // A 30 cm hole should be detected with hole_min_depth around 0.15-0.25.
    detect_holes_ = this->declare_parameter<bool>("detect_holes", true);
    hole_min_depth_ = this->declare_parameter<double>("hole_min_depth", 0.15);
    hole_max_depth_ = this->declare_parameter<double>("hole_max_depth", 1.00);

    angle_min_ = this->declare_parameter<double>("angle_min", -M_PI);
    angle_max_ = this->declare_parameter<double>("angle_max", M_PI);
    angle_increment_ = this->declare_parameter<double>("angle_increment", M_PI / 180.0);

    range_min_ = this->declare_parameter<double>("range_min", 0.0);
    range_max_ = this->declare_parameter<double>("range_max", 100.0);

    scan_time_ = this->declare_parameter<double>("scan_time", 0.1);
    use_inf_ = this->declare_parameter<bool>("use_inf", true);
    inf_epsilon_ = this->declare_parameter<double>("inf_epsilon", 1.0);
    print_per_message_ = this->declare_parameter<bool>("print_per_message", true);

    filtered_cloud_pub_ = this->create_publisher<sensor_msgs::msg::PointCloud2>(
    "scan_points_cloud", 10);
    pub_ = this->create_publisher<sensor_msgs::msg::LaserScan>(output_topic_, 10);

    sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      input_topic_,
      rclcpp::SensorDataQoS(),
      std::bind(&PointCloudToLaserScanLoggedNode::cloudCallback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "angle_inc: %f", angle_increment_);
    RCLCPP_INFO(this->get_logger(), "Subscribed to: %s", input_topic_.c_str());
    RCLCPP_INFO(this->get_logger(), "Publishing scan to: %s", output_topic_.c_str());
    RCLCPP_INFO(
      this->get_logger(),
      "floor_z = %.3f + %.3f*x + %.3f*y, normal=[%.3f, %.3f], rock=[%.3f, %.3f], hole_depth=[%.3f, %.3f]",
      floor_z_offset_, floor_slope_x_, floor_slope_y_, min_height_, max_height_,
      rock_min_height_, rock_max_height_, hole_min_depth_, hole_max_depth_);
  }

private:
  void cloudCallback(const sensor_msgs::msg::PointCloud2::SharedPtr cloud_msg)
  {
    auto scan_msg = std::make_unique<sensor_msgs::msg::LaserScan>();

    scan_msg->header = cloud_msg->header;
    scan_msg->angle_min = static_cast<float>(angle_min_);
    scan_msg->angle_max = static_cast<float>(angle_max_);
    scan_msg->angle_increment = static_cast<float>(angle_increment_);
    scan_msg->time_increment = 0.0f;
    scan_msg->scan_time = static_cast<float>(scan_time_);
    scan_msg->range_min = static_cast<float>(range_min_);
    scan_msg->range_max = static_cast<float>(range_max_);

    const uint32_t ranges_size = static_cast<uint32_t>(
      std::ceil((angle_max_ - angle_min_) / angle_increment_));

    if (use_inf_) {
      scan_msg->ranges.assign(ranges_size, std::numeric_limits<float>::infinity());
    } else {
      scan_msg->ranges.assign(ranges_size, static_cast<float>(range_max_ + inf_epsilon_));
    }

    size_t total_points = 0;
    size_t nanbad_points = 0;
    size_t heightbad_points = 0;
    size_t rangebad_points = 0;
    size_t anglebad_points = 0;
    size_t indexbad_points = 0;
    size_t normal_points = 0;
    size_t rock_points = 0;
    size_t hole_points = 0;
    size_t converted_points = 0;

    sensor_msgs::PointCloud2ConstIterator<float> iter_x(*cloud_msg, "x");
    sensor_msgs::PointCloud2ConstIterator<float> iter_y(*cloud_msg, "y");
    sensor_msgs::PointCloud2ConstIterator<float> iter_z(*cloud_msg, "z");

    pcl::PointCloud<pcl::PointXYZ>::Ptr scan_points(
		    new pcl::PointCloud<pcl::PointXYZ>());

    scan_points->header = pcl_conversions::toPCL(input->header);

    for (; iter_x != iter_x.end(); ++iter_x, ++iter_y, ++iter_z) {
      bool use_point = false;
      ++total_points;

      const float x = *iter_x;
      const float y = *iter_y;
      const float z = *iter_z;

      if (!std::isfinite(x) || !std::isfinite(y) || !std::isfinite(z)) {
        ++nanbad_points;
        continue;
      }

      const double expected_floor_z = floor_z_offset_ + floor_slope_x_ * x + floor_slope_y_ * y;
      const double relative_z = z - expected_floor_z;
      const double hole_depth = -relative_z;

      const bool is_normal = relative_z >= min_height_ && relative_z <= max_height_;
      const bool is_rock = detect_rocks_ &&
        relative_z >= rock_min_height_ && relative_z <= rock_max_height_;
      const bool is_hole = detect_holes_ &&
        hole_depth >= hole_min_depth_ && hole_depth <= hole_max_depth_;

      if (!is_normal && !is_rock && !is_hole) {
        ++heightbad_points;
        continue;
      }

      const double range = std::hypot(x, y);
      if (range < range_min_ || range > range_max_) {
        ++rangebad_points;
        continue;
      }

      const double angle = std::atan2(y, x);
      if (angle < angle_min_ || angle > angle_max_) {
        ++anglebad_points;
        continue;
      }

      const int index = static_cast<int>((angle - angle_min_) / angle_increment_);
      if (index < 0 || index >= static_cast<int>(scan_msg->ranges.size())) {
        ++indexbad_points;
        continue;
      }

      if (is_rock) {
        ++rock_points;
      } else if (is_hole) {
        ++hole_points;
      } else {
        ++normal_points;
      }

      ++converted_points;
      scan_points->points.push_back(pcl::PointXYZ(x, y, z));
      // Put the nearest accepted return into the 2D scan. This makes rocks and hole bottoms/edges
      // visible to Nav2/local costmap as occupied scan returns.
      if (range < scan_msg->ranges[static_cast<size_t>(index)]) {
        scan_msg->ranges[static_cast<size_t>(index)] = static_cast<float>(range);
      }
    }

    size_t filled_bins = 0;
    for (const auto & r : scan_msg->ranges) {
      if (use_inf_) {
        if (std::isfinite(r)) {
          ++filled_bins;
        }
      } else {
        if (r < range_max_ + inf_epsilon_) {
          ++filled_bins;
        }
      }
    }

    if (print_per_message_) {
      RCLCPP_INFO(
        this->get_logger(),
        "cloud points=%zu converted=%zu filled_bins=%zu normal=%zu rock=%zu hole=%zu nanbad=%zu heightbad=%zu rangebad=%zu anglebad=%zu indexbad=%zu",
        total_points,
        converted_points,
        filled_bins,
        normal_points,
        rock_points,
        hole_points,
        nanbad_points,
        heightbad_points,
        rangebad_points,
        anglebad_points,
        indexbad_points);
    }

    pub_->publish(std::move(scan_msg));
    sensor_msgs::msg::PointCloud2 output_cloud;
    pcl::toROSMsg(*scan_points, output_cloud);
    output_cloud.header = input->header;
    filtered_cloud_pub_->publish(output_cloud);
  }

  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr sub_;
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr pub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr filtered_cloud_pub_;

  std::string input_topic_;
  std::string output_topic_;

  double min_height_;
  double max_height_;
  double floor_z_offset_;
  double floor_slope_x_;
  double floor_slope_y_;
  bool detect_rocks_;
  double rock_min_height_;
  double rock_max_height_;
  bool detect_holes_;
  double hole_min_depth_;
  double hole_max_depth_;
  double angle_min_;
  double angle_max_;
  double angle_increment_;
  double range_min_;
  double range_max_;
  double scan_time_;
  bool use_inf_;
  double inf_epsilon_;
  bool print_per_message_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PointCloudToLaserScanLoggedNode>());
  rclcpp::shutdown();
  return 0;
}
