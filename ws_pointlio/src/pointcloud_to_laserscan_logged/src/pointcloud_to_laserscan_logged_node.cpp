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

    min_height_ = this->declare_parameter<double>("min_height", -0.2);
    max_height_ = this->declare_parameter<double>("max_height", 0.2);

    angle_min_ = this->declare_parameter<double>("angle_min", -M_PI);
    angle_max_ = this->declare_parameter<double>("angle_max", M_PI);
    angle_increment_ = this->declare_parameter<double>("angle_increment", M_PI / 180.0);

    range_min_ = this->declare_parameter<double>("range_min", 0.0);
    range_max_ = this->declare_parameter<double>("range_max", 100.0);

    scan_time_ = this->declare_parameter<double>("scan_time", 0.1);
    use_inf_ = this->declare_parameter<bool>("use_inf", true);
    inf_epsilon_ = this->declare_parameter<double>("inf_epsilon", 1.0);
    print_per_message_ = this->declare_parameter<bool>("print_per_message", true);

    pub_ = this->create_publisher<sensor_msgs::msg::LaserScan>(output_topic_, 10);

    sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
      input_topic_,
      rclcpp::SensorDataQoS(),
      std::bind(&PointCloudToLaserScanLoggedNode::cloudCallback, this, std::placeholders::_1));

    RCLCPP_INFO(this->get_logger(), "angle_inc to: %f", angle_increment_);
    RCLCPP_INFO(this->get_logger(), "Subscribed to: %s", input_topic_.c_str());
    RCLCPP_INFO(this->get_logger(), "Publishing scan to: %s", output_topic_.c_str());
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
    size_t zbad_points = 0;
    size_t rangebad_points = 0;
    size_t anglebad_points = 0;
    size_t indexbad_points = 0;
    size_t converted_points = 0;

    sensor_msgs::PointCloud2ConstIterator<float> iter_x(*cloud_msg, "x");
    sensor_msgs::PointCloud2ConstIterator<float> iter_y(*cloud_msg, "y");
    sensor_msgs::PointCloud2ConstIterator<float> iter_z(*cloud_msg, "z");

    for (; iter_x != iter_x.end(); ++iter_x, ++iter_y, ++iter_z) {
      ++total_points;

      const float x = *iter_x;
      const float y = *iter_y;
      const float z = *iter_z;

      if (std::isnan(x) || std::isnan(y) || std::isnan(z)) {
        ++nanbad_points;
        continue;
      }

      if (z < min_height_ || z > max_height_) {
        ++zbad_points;
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

      ++converted_points;

      if (range < scan_msg->ranges[static_cast<size_t>(index)]) {
        scan_msg->ranges[static_cast<size_t>(index)] = static_cast<float>(range);
      }
    }

    size_t filled_bins = 0;
    for (const auto & r : scan_msg->ranges) {
      if (std::isfinite(r) || (!use_inf_ && r <= (range_max_ + inf_epsilon_ - 1e-6))) {
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
    }

    if (print_per_message_) {
      RCLCPP_INFO(
        this->get_logger(),
        "cloud points=%zu converted=%zu filled_bins=%zu nanbad %zu zbad %zu rangebad %zu anglebad %zu indexbad %zu",
        total_points,
        converted_points,
        filled_bins,
	nanbad_points,
	zbad_points,
	rangebad_points,
	anglebad_points,
	indexbad_points);
    }

    pub_->publish(std::move(scan_msg));
  }

  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr sub_;
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr pub_;

  std::string input_topic_;
  std::string output_topic_;

  double min_height_;
  double max_height_;
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
