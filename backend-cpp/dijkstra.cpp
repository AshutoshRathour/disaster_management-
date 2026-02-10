#include "dijkstra.hpp"
#include <queue>
#include <climits>
#include <algorithm>
#include <functional>

PathResult dijkstra(const Graph& graph, int src, int dest) {
    PathResult result;
    result.total_distance = -1;
    result.success = false;

    if (graph.city_count == 0) return result;

    int n = graph.city_count;
    std::vector<int> dist(n, INT_MAX);
    std::vector<int> parent(n, -1);
    std::vector<bool> visited(n, false);

    // Min-heap priority queue: (distance, city_id)
    std::priority_queue<std::pair<int,int>, std::vector<std::pair<int,int>>, std::greater<std::pair<int,int>>> pq;

    dist[src] = 0;
    pq.push({0, src});

    while (!pq.empty()) {
        int d = pq.top().first;
        int u = pq.top().second;
        pq.pop();

        if (visited[u]) continue;
        visited[u] = true;

        if (u == dest) break;

        for (const Edge& edge : graph.get_edges(u)) {
            int v = edge.dest_id;
            int weight = edge.distance;

            if (!visited[v] && dist[u] != INT_MAX && dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                parent[v] = u;
                pq.push({dist[v], v});
            }
        }
    }

    if (dist[dest] == INT_MAX) return result;

    // Reconstruct path
    result.total_distance = dist[dest];
    result.success = true;

    int curr = dest;
    while (curr != -1) {
        result.path.push_back(curr);
        curr = parent[curr];
    }
    std::reverse(result.path.begin(), result.path.end());

    return result;
}
