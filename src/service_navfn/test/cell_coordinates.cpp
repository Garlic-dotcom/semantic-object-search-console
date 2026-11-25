// SPDX-License-Identifier: Apache-2.0
#include "service_navfn/planner.hpp"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>

template<class Base> class Harness : public Base
{
public:
  explicit Harness(nav2_costmap_2d::Costmap2D & grid, bool astar = false)
  {
    this->costmap_ = &grid;
    this->clock_ = std::make_shared<rclcpp::Clock>();
    this->global_frame_ = "map";
    this->tolerance_ = .5;
    this->allow_unknown_ = false;
    this->use_astar_ = astar;
    this->use_final_approach_orientation_ = false;
    this->planner_ = std::make_unique<nav2_navfn_planner::NavFn>(grid.getSizeInCellsX(), grid.getSizeInCellsY());
  }
};
geometry_msgs::msg::PoseStamped pose(double x, double y)
{
  geometry_msgs::msg::PoseStamped p;
  p.header.frame_id = "map";p.pose.position.x = x;p.pose.position.y = y;p.pose.orientation.w = 1.;
  return p;
}
void require(bool value, const char * message) {if (!value) {throw std::runtime_error(message);}}
void benchmark(const char * fixture)
{
  std::ifstream in(fixture);
  unsigned width, height;
  double resolution, ox, oy;
  require(static_cast<bool>(in >> width >> height >> resolution >> ox >> oy), "Invalid grid");
  nav2_costmap_2d::Costmap2D grid(width, height, resolution, ox, oy, 0);
  for (unsigned y = 0; y < height; ++y) {
    for (unsigned x = 0; x < width; ++x) {
      unsigned cost;
      require(static_cast<bool>(in >> cost) && cost <= 255, "Invalid grid cost");
      grid.setCost(x, y, cost);
    }
  }
  Harness<service_navfn::CellCenteredNavfn> dijkstra(grid), astar(grid, true);
  std::string name;
  double sx, sy, gx, gy;
  while (in >> name >> sx >> sy >> gx >> gy) {
    std::vector<double> timings[2];
    double lengths[2] = {};
    unsigned peak_cost[2] = {};
    for (int i = 0; i < 55; ++i) {
      for (int j = 0; j < 2; ++j) {
        const int a = (i + j) % 2;
        const auto before = std::chrono::steady_clock::now();
        auto path = (a ? astar : dijkstra).createPlan(pose(sx, sy), pose(gx, gy));
        const auto elapsed = std::chrono::steady_clock::now() - before;
        require(!path.poses.empty(), "Benchmark route missing");
        const auto & end = path.poses.back().pose.position;
        require(std::hypot(end.x - gx, end.y - gy) < 1e-8, "Benchmark goal shifted");
        if (i >= 5) {
          timings[a].push_back(std::chrono::duration<double, std::micro>(elapsed).count());
        }
        if (i != 0) {continue;}
        auto previous = pose(sx, sy).pose.position;
        for (const auto & point : path.poses) {
          const auto & next = point.pose.position;
          const double distance = std::hypot(next.x - previous.x, next.y - previous.y);
          lengths[a] += distance;
          const int steps = std::max(1, static_cast<int>(std::ceil(distance / (resolution / 4))));
          for (int step = 0; step <= steps; ++step) {
            const double t = static_cast<double>(step) / steps;
            unsigned x, y;
            require(grid.worldToMap(previous.x + t * (next.x - previous.x),
              previous.y + t * (next.y - previous.y), x, y), "Path outside the grid");
            peak_cost[a] = std::max(peak_cost[a], static_cast<unsigned>(grid.getCost(x, y)));
          }
          previous = next;
        }
      }
    }
    std::cout << name;
    for (int a = 0; a < 2; ++a) {
      auto & t = timings[a];
      std::sort(t.begin(), t.end());
      std::cout << ',' << (t[24] + t[25]) / 2 << ',' << t[47] << ',' << lengths[a] << ',' << peak_cost[a];
    }
    std::cout << '\n';
  }
}

int main(int argc, char ** argv)
{
  if (argc == 2) {benchmark(argv[1]); return 0;}
  nav2_costmap_2d::Costmap2D grid(80, 80, .05, -1., -1., 0);
  for (unsigned y = 0; y < 80; ++y) {grid.setCost(40, y, 254);}
  Harness<nav2_navfn_planner::NavfnPlanner> original(grid);
  Harness<service_navfn::CellCenteredNavfn> fixed(grid);
  const auto start = pose(.25, .25), goal = pose(.976, .326);
  auto old = original.createPlan(start, goal), corrected = fixed.createPlan(start, goal);
  require(!old.poses.empty() && !corrected.poses.empty(), "Both solvers must find a path");
  const auto endpoint = corrected.poses.back().pose.position;
  require(std::hypot(endpoint.x - goal.pose.position.x, endpoint.y - goal.pose.position.y) < 1e-8,
    "Reachable requested endpoint must not move to neighbour cell");
  require(std::hypot(old.poses.back().pose.position.x - goal.pose.position.x,
    old.poses.back().pose.position.y - goal.pose.position.y) > .04, "Fixture must reproduce native round fallback");
  for (const auto & p : corrected.poses) {
    unsigned x, y;
    require(grid.worldToMap(p.pose.position.x, p.pose.position.y, x, y), "Every path point stays in bounds");
    require(grid.getCost(x, y) < 253, "Corrected path must not enter wall");
  }
  const auto blocked = pose(1.025, .326);
  Harness<service_navfn::CellCenteredNavfn> candidate(grid, true);
  auto fallback = candidate.createPlan(start, blocked);
  require(!fallback.poses.empty() && fallback.poses.back().pose.position.x < 1.,
    "A* must fall back to a reachable Dijkstra tolerance goal");
  require(candidate.createPlan(start, pose(1.8, .326)).poses.empty(),
    "A* fallback must not cross an impassable wall");
  require(!candidate.createPlan(start, goal).poses.empty(), "A* must reach a free goal");
  require(fixed.createPlan(start, pose(100., 0.)).poses.empty(), "Off-map rejected");
  require(fixed.createPlan(start, pose(NAN, 0.)).poses.empty(), "Nonfinite rejected");
  require(fixed.createPlan(pose(-.99, -.99), pose(-.98, -.98)).poses.size() > 0,
    "First half cell is valid");
  std::cout << "native_goal_x=" << old.poses.back().pose.position.x << " corrected_goal_x=" << endpoint.x
    << " path_points=" << corrected.poses.size() << " all_checks=passed\n";
}
