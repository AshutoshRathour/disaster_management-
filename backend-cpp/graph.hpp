#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <string>
#include <vector>
#include <unordered_map>

struct City {
    int id;
    std::string name;
    int population;
    int damage_level;
    int resources;
    double latitude;
    double longitude;
};

struct Edge {
    int dest_id;
    int distance;
};

class Graph {
public:
    std::vector<City> cities;
    std::unordered_map<int, std::vector<Edge>> adj_list;
    int city_count;

    Graph();
    int add_city(const std::string& name, int pop, int damage, int res, double lat, double lon);
    void add_road(int src, int dest, int dist);
    City* find_city_by_id(int id);
    City* find_city_by_name(const std::string& name);
    const std::vector<Edge>& get_edges(int city_id) const;
    void clear();
};

#endif
