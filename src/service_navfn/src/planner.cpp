// SPDX-License-Identifier: Apache-2.0
// Adapted from ros-navigation/navigation2 humble nav2_navfn_planner,
// Copyright 2018 Intel Corporation, 2018 Simbe Robotics, 2019 Samsung Research
// America. Same installed NavFn solver, tolerance search and goal smoothing.
// https://github.com/ros-navigation/navigation2/blob/humble/nav2_navfn_planner/src/navfn_planner.cpp
#include "service_navfn/planner.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include "nav2_costmap_2d/cost_values.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace service_navfn
{
nav_msgs::msg::Path CellCenteredNavfn::createPlan(
  const geometry_msgs::msg::PoseStamped & start,
  const geometry_msgs::msg::PoseStamped & goal)
{
  nav_msgs::msg::Path path;
  path.header.frame_id = global_frame_;
  path.header.stamp = clock_->now();
  const auto & s = start.pose.position;
  const auto & g = goal.pose.position;
  if (!std::isfinite(s.x) || !std::isfinite(s.y) ||
    !std::isfinite(g.x) || !std::isfinite(g.y)) {return path;}
  unsigned int sx, sy, gx, gy;
  std::unique_lock<nav2_costmap_2d::Costmap2D::mutex_t> lock(*costmap_->getMutex());
  // Costmap2D::worldToMap uses floor, not the inherited NavFn round helper.
  if (!costmap_->worldToMap(s.x, s.y, sx, sy) ||
    !costmap_->worldToMap(g.x, g.y, gx, gy)) {return path;}
  if (s.x == g.x && s.y == g.y) {
    if (costmap_->getCost(sx, sy) == nav2_costmap_2d::LETHAL_OBSTACLE) {return path;}
    auto pose = goal;
    pose.header = path.header;
    if (use_final_approach_orientation_) {pose.pose.orientation = start.pose.orientation;}
    path.poses.push_back(pose);
    return path;
  }
  planner_->setNavArr(costmap_->getSizeInCellsX(), costmap_->getSizeInCellsY());
  // Retain upstream's start-cell handling; no entire-layer clearing.
  clearRobotCell(sx, sy);
  planner_->setCostmap(costmap_->getCharMap(), true, allow_unknown_);
  const double resolution = costmap_->getResolution();
  const double ox = costmap_->getOriginX(), oy = costmap_->getOriginY();
  const int max_cycles = 4 * std::max(costmap_->getSizeInCellsX(), costmap_->getSizeInCellsY());
  lock.unlock();
  int map_start[2] = {static_cast<int>(sx), static_cast<int>(sy)};
  int map_goal[2] = {static_cast<int>(gx), static_cast<int>(gy)};
  planner_->setStart(map_goal);
  planner_->setGoal(map_start);

  auto potential = [&](const geometry_msgs::msg::Pose & p) {
      // Geometry is fixed while the global planner is running (map costmap).
      if (p.position.x < ox || p.position.y < oy) {return static_cast<double>(POT_HIGH);}
      const auto x = static_cast<unsigned int>((p.position.x - ox) / resolution);
      const auto y = static_cast<unsigned int>((p.position.y - oy) / resolution);
      if (x >= static_cast<unsigned int>(planner_->nx) || y >= static_cast<unsigned int>(planner_->ny)) {
        return static_cast<double>(POT_HIGH);
      }
      return static_cast<double>(planner_->potarr[y * planner_->nx + x]);
    };
  auto best = goal.pose;
  int count = 0;
  if (use_astar_ && planner_->calcNavFnAstar() && potential(best) < POT_HIGH) {
    count = planner_->calcPath(max_cycles);
  }
  // A blocked goal or failed extraction needs the settled Dijkstra field
  // before selecting a reachable point in the goal tolerance window.
  if (count == 0) {
    planner_->calcNavFnDijkstra(true);
    bool found = potential(best) < POT_HIGH;
    if (!found) {
      double distance = std::numeric_limits<double>::max();
      auto p = goal.pose;
      for (p.position.y = g.y - tolerance_; p.position.y <= g.y + tolerance_; p.position.y += resolution) {
        for (p.position.x = g.x - tolerance_; p.position.x <= g.x + tolerance_; p.position.x += resolution) {
          const double d = squared_distance(p, goal.pose);
          if (potential(p) < POT_HIGH && d < distance) {distance = d; best = p; found = true;}
        }
      }
    }
    if (!found) {return path;}
    map_goal[0] = static_cast<int>((best.position.x - ox) / resolution);
    map_goal[1] = static_cast<int>((best.position.y - oy) / resolution);
    planner_->setStart(map_goal);
    count = planner_->calcPath(max_cycles);
  }
  if (count == 0) {return path;}
  const auto px = planner_->getPathX(), py = planner_->getPathY();
  for (int i = count - 1; i >= 0; --i) {
    geometry_msgs::msg::PoseStamped pose;
    pose.header = path.header;
    // Fractional NavFn indices refer to cell centres, as Costmap2D does.
    pose.pose.position.x = ox + (px[i] + .5) * resolution;
    pose.pose.position.y = oy + (py[i] + .5) * resolution;
    pose.pose.orientation.w = 1.;
    path.poses.push_back(pose);
  }
  smoothApproachToGoal(best, path);
  if (use_final_approach_orientation_) {
    auto previous = start.pose.position;
    for (auto it = path.poses.rbegin() + 1; it != path.poses.rend(); ++it) {
      if (std::hypot(it->pose.position.x - best.position.x, it->pose.position.y - best.position.y) > 1e-4) {
        previous = it->pose.position;
        break;
      }
    }
    path.poses.back().pose.orientation = nav2_util::geometry_utils::orientationAroundZAxis(
      std::atan2(best.position.y - previous.y, best.position.x - previous.x));
  }
  return path;
}
}  // namespace service_navfn
PLUGINLIB_EXPORT_CLASS(service_navfn::CellCenteredNavfn, nav2_core::GlobalPlanner)
