# Disaster Management System

Maintained by Ashutosh Rathour

A comprehensive web-based disaster management and resource allocation system built with Python Flask backend and vanilla HTML/CSS/JS frontend.

## Features

- **User Authentication** - Signup/Login system with session management
- **City Management** - Add and view cities with population, damage levels, resources, and geographic coordinates
- **Road Network** - Create road connections between cities with distances
- **Disaster Requests** - Log disaster relief requests with priority levels
- **Resource Allocation** - Automated resource allocation using Dijkstra's shortest path algorithm
- **Route Calculation** - Interactive map with shortest path visualization (Leaflet.js)
- **Emergency Numbers** - Quick access to emergency helpline numbers
- **Activity Logs** - Track all system activities

## Tech Stack

- **Backend**: Python Flask with Flask-CORS
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Maps**: Leaflet.js
- **Icons**: Font Awesome 6
- **Algorithms**: Dijkstra's Shortest Path (Python implementation)

## Project Structure

```
├── flask-api/
│   ├── app.py              # Flask application (main server)
│   ├── py_backend.py       # Python backend with Graph, Dijkstra, ResourceManager
│   ├── requirements.txt    # Python dependencies
│   └── disaster_relief.db  # SQLite database (auto-created)
├── frontend/
│   ├── index.html          # Dashboard
│   ├── login.html          # Login page
│   ├── signup.html         # Registration page
│   ├── cities.html         # City management
│   ├── roads.html          # Road network management
│   ├── requests.html       # Disaster requests
│   ├── allocate.html       # Resource allocation
│   ├── map.html            # Interactive map with routing
│   ├── logs.html           # Activity logs
│   └── emergency.html      # Emergency helpline numbers
├── backend-cpp/            # C++ backend source (optional, for compilation)
│   ├── graph.hpp/cpp       # Graph data structure
│   ├── dijkstra.hpp/cpp    # Dijkstra's algorithm
│   ├── resources.hpp/cpp   # Resource allocation engine
│   ├── wrapper.cpp         # C API wrapper for ctypes
│   └── CMakeLists.txt      # CMake build configuration
└── README.md
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/AshutoshRathour/disaster_management.git
   cd disaster_management
   ```

2. **Install dependencies**
   ```bash
   cd flask-api
   pip install flask flask-cors
   ```

3. **Run the server**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

5. **Create an account** and start using the system!

## Usage

1. **Login/Signup** - Create an account or login
2. **Add Cities** - Go to Cities page and add locations with coordinates
3. **Create Roads** - Connect cities via the Roads page
4. **Submit Requests** - Log disaster relief requests from the Requests page
5. **Allocate Resources** - Run allocation algorithm from the Allocate page
6. **View Map** - See cities and calculate shortest routes on the Map page

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/signup` | POST | User registration |
| `/api/login` | POST | User login |
| `/api/logout` | GET | User logout |
| `/api/city/add` | POST | Add a new city |
| `/api/city/list` | GET | List all cities |
| `/api/road/add` | POST | Add a road connection |
| `/api/road/list` | GET | List all roads |
| `/api/request/add` | POST | Submit disaster request |
| `/api/request/list` | GET | List all requests |
| `/api/allocate` | POST | Run resource allocation |
| `/api/shortest-path` | GET | Calculate shortest route |
| `/api/graph-info` | GET | Get full graph data |
| `/api/logs` | GET | Get activity logs |
| `/api/emergency-numbers` | GET | Get emergency contacts |

## Algorithm Details

### Dijkstra's Shortest Path
The system uses Dijkstra's algorithm with a min-heap priority queue to find the shortest path between cities for resource allocation and route planning.

### Resource Allocation
The allocation algorithm:
1. Sorts pending requests by priority (highest first)
2. For each request, finds the nearest city with sufficient resources and low damage level
3. Allocates resources and updates the database

## C++ Backend (Optional)

The repository includes C++ source files for a high-performance backend. To use it:

1. Install a 64-bit C++ compiler (MinGW-w64 or MSVC)
2. Build with CMake or directly:
   ```bash
   cd backend-cpp
   g++ -std=c++14 -shared -o backend.dll graph.cpp dijkstra.cpp resources.cpp wrapper.cpp
   ```
3. The Flask app will automatically detect and use the DLL if available

## License

This project is for educational purposes.

## Author

Ashutosh Rathour - [AshutoshRathour](https://github.com/AshutoshRathour)

