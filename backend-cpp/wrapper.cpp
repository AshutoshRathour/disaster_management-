#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <string>
#include <sstream>
#include "graph.hpp"
#include "dijkstra.hpp"
#include "resources.hpp"

// Global instances
static Graph* g_graph = nullptr;
static ResourceManager* g_resource_mgr = nullptr;

// Helper: duplicate a std::string as a C string (caller must free)
static char* str_dup(const std::string& s) {
    char* buf = (char*)malloc(s.size() + 1);
    if (buf) {
        memcpy(buf, s.c_str(), s.size() + 1);
    }
    return buf;
}

// C-compatible exported functions
extern "C" {

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

EXPORT void backend_init() {
    if (g_graph) delete g_graph;
    if (g_resource_mgr) delete g_resource_mgr;
    g_graph = new Graph();
    g_resource_mgr = new ResourceManager();
}

EXPORT int backend_add_city(const char* name, int pop, int damage, int res, double lat, double lon) {
    if (!g_graph) return -1;
    return g_graph->add_city(std::string(name), pop, damage, res, lat, lon);
}

EXPORT void backend_add_road(int src, int dest, int dist) {
    if (!g_graph) return;
    g_graph->add_road(src, dest, dist);
}

EXPORT char* backend_shortest_path_json(int src, int dest) {
    if (!g_graph) {
        return str_dup("{\"success\": false, \"error\": \"Graph not initialized\"}");
    }

    PathResult result = dijkstra(*g_graph, src, dest);

    if (!result.success) {
        return str_dup("{\"success\": false, \"error\": \"No path found\"}");
    }

    std::ostringstream oss;
    oss << "{\"success\": true, \"path\": [";
    for (size_t i = 0; i < result.path.size(); i++) {
        if (i > 0) oss << ", ";
        oss << result.path[i];
    }
    oss << "], \"distance\": " << result.total_distance << "}";

    return str_dup(oss.str());
}

EXPORT char* backend_graph_json() {
    if (!g_graph) {
        return str_dup("{\"cities\": [], \"roads\": []}");
    }

    std::ostringstream oss;
    oss << "{\"cities\": [";

    for (size_t i = 0; i < g_graph->cities.size(); i++) {
        const City& city = g_graph->cities[i];
        if (i > 0) oss << ", ";
        oss << "{\"id\": " << city.id
            << ", \"name\": \"" << city.name << "\""
            << ", \"population\": " << city.population
            << ", \"damage_level\": " << city.damage_level
            << ", \"resources\": " << city.resources
            << ", \"latitude\": " << city.latitude
            << ", \"longitude\": " << city.longitude << "}";
    }

    oss << "], \"roads\": [";

    bool first_road = true;
    for (auto it = g_graph->adj_list.begin(); it != g_graph->adj_list.end(); ++it) {
        int city_id = it->first;
        const std::vector<Edge>& edges = it->second;
        for (const Edge& edge : edges) {
            if (city_id < edge.dest_id) {
                if (!first_road) oss << ", ";
                first_road = false;
                oss << "{\"src\": " << city_id
                    << ", \"dest\": " << edge.dest_id
                    << ", \"distance\": " << edge.distance << "}";
            }
        }
    }

    oss << "]}";
    return str_dup(oss.str());
}

EXPORT char* backend_allocate_resources() {
    if (!g_graph || !g_resource_mgr) {
        return str_dup("{\"allocations\": []}");
    }

    auto results = g_resource_mgr->process_allocations(*g_graph);

    std::ostringstream oss;
    oss << "{\"allocations\": [";

    for (size_t i = 0; i < results.size(); i++) {
        if (i > 0) oss << ", ";

        City* affected = g_graph->find_city_by_id(results[i].affected_city_id);
        City* support = g_graph->find_city_by_id(results[i].support_city_id);

        oss << "{\"request_id\": " << results[i].request_id
            << ", \"affected_city\": \"" << (affected ? affected->name : "unknown") << "\""
            << ", \"support_city\": \"" << (support ? support->name : "none") << "\""
            << ", \"allocated\": " << results[i].allocated_resources
            << ", \"distance\": " << results[i].distance
            << ", \"status\": \"" << results[i].status << "\"}";
    }

    oss << "]}";
    return str_dup(oss.str());
}

EXPORT int backend_add_request(int city_id, int priority, int required_resources) {
    if (!g_resource_mgr) return -1;
    return g_resource_mgr->add_request(city_id, priority, required_resources);
}

EXPORT char* backend_get_requests_json() {
    if (!g_resource_mgr) {
        return str_dup("{\"requests\": []}");
    }

    std::ostringstream oss;
    oss << "{\"requests\": [";

    const auto& reqs = g_resource_mgr->get_all_requests();
    for (size_t i = 0; i < reqs.size(); i++) {
        if (i > 0) oss << ", ";

        City* city = g_graph ? g_graph->find_city_by_id(reqs[i].city_id) : nullptr;

        oss << "{\"id\": " << reqs[i].id
            << ", \"city_id\": " << reqs[i].city_id
            << ", \"city_name\": \"" << (city ? city->name : "unknown") << "\""
            << ", \"priority\": " << reqs[i].priority
            << ", \"required\": " << reqs[i].required_resources
            << ", \"status\": \"" << reqs[i].status << "\"}";
    }

    oss << "]}";
    return str_dup(oss.str());
}

EXPORT void backend_free_string(char* ptr) {
    if (ptr) free(ptr);
}

} // extern "C"
