"""Pure Python backend for Disaster Management System"""
import json
from collections import defaultdict, deque
import heapq


class Graph:
    def __init__(self):
        self.cities = {}  # id -> City
        self.adj_list = defaultdict(list)  # city_id -> [(dest_id, distance), ...]
        self.city_count = 0
        self.next_city_id = 0

    def add_city(self, name, pop, damage, res, lat, lon):
        city_id = self.next_city_id
        self.cities[city_id] = {
            'id': city_id,
            'name': name,
            'population': pop,
            'damage_level': damage,
            'resources': res,
            'latitude': lat,
            'longitude': lon
        }
        self.next_city_id += 1
        self.city_count += 1
        return city_id

    def add_road(self, src, dest, dist):
        self.adj_list[src].append((dest, dist))
        self.adj_list[dest].append((src, dist))

    def find_city_by_id(self, city_id):
        return self.cities.get(city_id)

    def find_city_by_name(self, name):
        for city in self.cities.values():
            if city['name'] == name:
                return city
        return None

    def get_edges(self, city_id):
        return self.adj_list.get(city_id, [])

    def get_all_cities(self):
        return list(self.cities.values())

    def dijkstra(self, src, dest):
        """Dijkstra's shortest path algorithm"""
        if src not in self.cities or dest not in self.cities:
            return None

        dist = {cid: float('inf') for cid in self.cities}
        parent = {cid: -1 for cid in self.cities}
        dist[src] = 0

        pq = [(0, src)]  # (distance, city_id)

        while pq:
            d, u = heapq.heappop(pq)

            if d > dist[u]:
                continue

            if u == dest:
                break

            for v, weight in self.get_edges(u):
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    parent[v] = u
                    heapq.heappush(pq, (dist[v], v))

        if dist[dest] == float('inf'):
            return None

        # Reconstruct path
        path = []
        curr = dest
        while curr != -1:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

        return {
            'path': path,
            'distance': int(dist[dest]),
            'success': True
        }

    def to_json(self):
        cities = list(self.cities.values())
        
        roads = []
        seen = set()
        for src, edges in self.adj_list.items():
            for dest, dist in edges:
                if (min(src, dest), max(src, dest)) not in seen:
                    roads.append({'src': src, 'dest': dest, 'distance': dist})
                    seen.add((min(src, dest), max(src, dest)))

        return {'cities': cities, 'roads': roads}


class ResourceManager:
    def __init__(self):
        self.requests = {}  # id -> request
        self.next_id = 1
        self.request_list = []  # sorted list of requests

    def add_request(self, city_id, priority, required_resources):
        req_id = self.next_id
        self.requests[req_id] = {
            'id': req_id,
            'city_id': city_id,
            'priority': priority,
            'required_resources': required_resources,
            'status': 'pending'
        }
        self.request_list.append(self.requests[req_id])
        self.request_list.sort(key=lambda r: -r['priority'])
        self.next_id += 1
        return req_id

    def get_all_requests(self):
        return self.request_list

    def allocate_resources(self, graph):
        """Allocate resources using Dijkstra's algorithm"""
        results = []

        for req in self.request_list:
            if req['status'] != 'pending':
                continue

            affected_city = graph.find_city_by_id(req['city_id'])
            best_support_id = -1
            best_distance = float('inf')

            for potential_city in graph.get_all_cities():
                if (potential_city['id'] != req['city_id'] and
                    potential_city['resources'] >= req['required_resources'] and
                    potential_city['damage_level'] < 5):

                    path_result = graph.dijkstra(req['city_id'], potential_city['id'])
                    if path_result and path_result['distance'] < best_distance:
                        best_distance = path_result['distance']
                        best_support_id = potential_city['id']

            result = {
                'request_id': req['id'],
                'affected_city': affected_city['name'] if affected_city else 'unknown',
                'support_city': 'none',
                'allocated': 0,
                'distance': best_distance if best_distance != float('inf') else 0,
                'status': 'no_resources'
            }

            if best_support_id != -1:
                support_city = graph.find_city_by_id(best_support_id)
                result['support_city'] = support_city['name']
                result['allocated'] = req['required_resources']
                result['status'] = 'allocated'
                support_city['resources'] -= req['required_resources']
                req['status'] = 'allocated'

            results.append(result)

        return results


# Global instances
backend = None


def init():
    global backend
    backend = {
        'graph': Graph(),
        'resource_manager': ResourceManager()
    }


def backend_init():
    init()


def backend_add_city(name, pop, damage, res, lat, lon):
    return backend['graph'].add_city(name, pop, damage, res, lat, lon)


def backend_add_road(src, dest, dist):
    backend['graph'].add_road(src, dest, dist)


def backend_shortest_path_json(src, dest):
    result = backend['graph'].dijkstra(src, dest)
    if result is None:
        return json.dumps({'success': False, 'error': 'No path found'})
    return json.dumps(result)


def backend_graph_json():
    return json.dumps(backend['graph'].to_json())


def backend_add_request(city_id, priority, required_resources):
    return backend['resource_manager'].add_request(city_id, priority, required_resources)


def backend_get_requests_json():
    requests = []
    for req in backend['resource_manager'].get_all_requests():
        city = backend['graph'].find_city_by_id(req['city_id'])
        requests.append({
            'id': req['id'],
            'city_id': req['city_id'],
            'city_name': city['name'] if city else 'unknown',
            'priority': req['priority'],
            'required': req['required_resources'],
            'status': req['status']
        })
    return json.dumps({'requests': requests})


def backend_allocate_resources():
    results = backend['resource_manager'].allocate_resources(backend['graph'])
    return json.dumps({'allocations': results})
