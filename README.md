# UE22CS351B-CC Raft3D

The Raft3D project implements a distributed 3D printing management system with a mock Raft algorithm, Dockerized deployment, RESTful APIs, Prometheus metrics, fault tolerance, and snapshot persistence. The system supports leader election, resource management, and monitoring, with a complete set of commands to demonstrate its functionality. It serves as a practical example of distributed systems concepts, with robust features for operation, recovery, and debugging, ready to showcase fault-tolerant behavior and API-driven resource management.

---------

## Implementation

- **Architecture:** Mock Raft nodes interact over Docker network; each node exposes REST APIs and participates in leader election.
- **Leader Election:** Uses randomized timers and heartbeats to simulate Raft leadership behavior.
- **Snapshot Persistence:** Each node stores its data in `/raft/data`, preserved across restarts.
- **Metrics:** Exposed via `/metrics` endpoint for each node, including `raft3d_is_leader` flag.

## Limitations

Implements only mock consensus without full log replication or quorum enforcement.

## Use cases

To demonstrate distributed coordination, simulate failures, and build fault-tolerant APIs with metrics.

**1. Simulating Fault Tolerance:**  
Stop a leader node and observe re-election in real-time via metrics.

**2. API-based Resource Management:**  
Manage virtual 3D printers, filaments, and jobs across a cluster.

**3. Metrics Integration:**  
Scrape node metrics using Prometheus to monitor leadership and API behavior.

**4. Educational Tool:**  
Ideal for teaching concepts like Raft, REST APIs, container orchestration, and failure recovery.

---------

## Steps to run

**1. Clone this repo and Navigate to directory**
```
git clone <repo-url>
cd raft3d
```

**2. Launch the cluster**
```
sudo docker-compose up --build -d
```

**3. View running containers**
```
sudo docker ps
```

**4. Check who is leader**
```
curl http://localhost:8080/metrics | grep raft3d_is_leader
curl http://localhost:8081/metrics | grep raft3d_is_leader
curl http://localhost:8082/metrics | grep raft3d_is_leader
```

**5. API Interactions:**

**5.1 Add Printer**
```
curl -X POST http://localhost:8080/api/v1/printers \
  -H "Content-Type: application/json" \
  -d '{"id": "p1", "company": "Creality", "model": "Ender 3"}'
```

**5.2 Add filament**
```
curl -X POST http://localhost:8080/api/v1/filaments \
  -H "Content-Type: application/json" \
  -d '{"id": "f1", "type": "PLA", "color": "Blue", "total_weight_in_grams": 1000, "remaining_weight_in_grams": 1000}'
```

**5.3 Create Print Job**
```
curl -X POST http://localhost:8080/api/v1/print_jobs \
  -H "Content-Type: application/json" \
  -d '{"id": "j1", "printer_id": "p1", "filament_id": "f1", "filepath": "prints/sword/hilt.gcode", "print_weight_in_grams": 100, "status": "Queued"}'
```

**5.4 Update jobs**
```
curl -X POST http://localhost:8080/api/v1/print_jobs/j1/status?status=Running
```

**6. Fault Tolerance Simulation, Stop the leader node (assume node1 is leader):
     Use Container ID of that node if the name resolution dont work**
```
sudo docker stop raft3d_raft3d-node1_1
```


**7. Verify a new leader is elected:**
```
curl http://localhost:8081/metrics | grep raft3d_is_leader
curl http://localhost:8082/metrics | grep raft3d_is_leader
```

**8. Snapshot Inspection:**
```
sudo docker exec raft3d_raft3d-node2_1 ls /raft/data
```

<br>

---

<br>

```
We Love CC ❤️
```
