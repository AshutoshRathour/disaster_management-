#ifndef RESOURCES_HPP
#define RESOURCES_HPP

#include <string>
#include <vector>
#include "graph.hpp"

struct DisasterRequest {
    int id;
    int city_id;
    int priority;
    int required_resources;
    std::string status;
};

struct AllocationResult {
    int request_id;
    int affected_city_id;
    int support_city_id;
    int allocated_resources;
    int distance;
    std::string status;
};

class ResourceManager {
public:
    std::vector<DisasterRequest> requests;
    int next_id;

    ResourceManager();
    int add_request(int city_id, int priority, int required_resources);
    std::vector<AllocationResult> process_allocations(Graph& graph);
    const std::vector<DisasterRequest>& get_all_requests() const;
    void clear();
};

#endif
