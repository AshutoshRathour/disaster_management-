#include "resources.hpp"
#include "dijkstra.hpp"
#include <climits>
#include <algorithm>

ResourceManager::ResourceManager() : next_id(1) {}

int ResourceManager::add_request(int city_id, int priority, int required_resources) {
    DisasterRequest req;
    req.id = next_id++;
    req.city_id = city_id;
    req.priority = priority;
    req.required_resources = required_resources;
    req.status = "pending";

    // Insert sorted by priority (higher first)
    auto it = requests.begin();
    while (it != requests.end() && it->priority >= priority) {
        ++it;
    }
    requests.insert(it, req);

    return req.id;
}

std::vector<AllocationResult> ResourceManager::process_allocations(Graph& graph) {
    std::vector<AllocationResult> results;

    for (auto& req : requests) {
        if (req.status != "pending") continue;

        int best_support_id = -1;
        int best_distance = INT_MAX;

        for (auto& potential : graph.cities) {
            if (potential.id != req.city_id &&
                potential.resources >= req.required_resources &&
                potential.damage_level < 5) {

                PathResult path = dijkstra(graph, req.city_id, potential.id);
                if (path.success && path.total_distance >= 0 &&
                    path.total_distance < best_distance) {
                    best_distance = path.total_distance;
                    best_support_id = potential.id;
                }
            }
        }

        AllocationResult res;
        res.request_id = req.id;
        res.affected_city_id = req.city_id;
        res.support_city_id = best_support_id;
        res.distance = best_distance;

        if (best_support_id != -1) {
            City* support = graph.find_city_by_id(best_support_id);
            if (support) {
                support->resources -= req.required_resources;
            }
            res.allocated_resources = req.required_resources;
            res.status = "allocated";
            req.status = "allocated";
        } else {
            res.allocated_resources = 0;
            res.status = "no_resources";
        }

        results.push_back(res);
    }

    return results;
}

const std::vector<DisasterRequest>& ResourceManager::get_all_requests() const {
    return requests;
}

void ResourceManager::clear() {
    requests.clear();
    next_id = 1;
}
