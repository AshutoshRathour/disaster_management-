#include "graph.hpp"

static const std::vector<Edge> empty_edges;

Graph::Graph() : city_count(0) {}

int Graph::add_city(const std::string& name, int pop, int damage, int res, double lat, double lon) {
    City city;
    city.id = city_count;
    city.name = name;
    city.population = pop;
    city.damage_level = damage;
    city.resources = res;
    city.latitude = lat;
    city.longitude = lon;

    cities.push_back(city);
    adj_list[city.id] = std::vector<Edge>();
    city_count++;
    return city.id;
}

void Graph::add_road(int src, int dest, int dist) {
    adj_list[src].push_back({dest, dist});
    adj_list[dest].push_back({src, dist});
}

City* Graph::find_city_by_id(int id) {
    for (auto& city : cities) {
        if (city.id == id) return &city;
    }
    return nullptr;
}

City* Graph::find_city_by_name(const std::string& name) {
    for (auto& city : cities) {
        if (city.name == name) return &city;
    }
    return nullptr;
}

const std::vector<Edge>& Graph::get_edges(int city_id) const {
    auto it = adj_list.find(city_id);
    if (it != adj_list.end()) return it->second;
    return empty_edges;
}

void Graph::clear() {
    cities.clear();
    adj_list.clear();
    city_count = 0;
}
