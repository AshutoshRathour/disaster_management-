#ifndef DIJKSTRA_HPP
#define DIJKSTRA_HPP

#include <vector>
#include "graph.hpp"

struct PathResult {
    std::vector<int> path;
    int total_distance;
    bool success;
};

PathResult dijkstra(const Graph& graph, int src, int dest);

#endif
