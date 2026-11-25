// SPDX-License-Identifier: Apache-2.0
#pragma once
#include "nav2_navfn_planner/navfn_planner.hpp"

namespace service_navfn
{
// Use cell-centred coordinates. A* mode falls back to Dijkstra for failed
// extraction and goal-tolerance search.
class CellCenteredNavfn : public nav2_navfn_planner::NavfnPlanner
{
public:
  nav_msgs::msg::Path createPlan(
    const geometry_msgs::msg::PoseStamped & start,
    const geometry_msgs::msg::PoseStamped & goal) override;
};
}  // namespace service_navfn
