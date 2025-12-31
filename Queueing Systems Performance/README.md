**Queue Dynamics and Load Balancing Simulations**

This project explores queueing behavior and load-balancing strategies in single- and multi-server systems through discrete-event simulation. It combines theoretical results from queueing theory with empirical analysis to illustrate how system performance evolves under different traffic intensities and routing policies.

The first part of the project focuses on an M/M/1 queue, analyzing system occupancy and busy periods under varying arrival rates. Simulated results are compared against theoretical predictions, validating properties such as PASTA (Poisson Arrivals See Time Averages) and demonstrating how busy-period distributions change as load increases.

The second part examines multi-server systems with parallel queues, comparing three routing policies:

-Uniform Random

-Join-the-Shortest-Queue (JSQ)

-Power-of-Two-Choices (Po2C)

Using complementary cumulative distribution functions (CCDFs) of waiting times, the simulations highlight the performance trade-offs between these policies. Results show that JSQ minimizes waiting times, while Po2C achieves near-optimal performance with significantly lower overhead, making it well-suited for large-scale systems.

Overall, the project demonstrates how informed routing decisions dramatically improve performance and provides practical insight into scalable load-balancing techniques used in real-world server farms and cloud systems.

**Simulation Code**

This repository also includes two Python scripts that reproduce the simulation results mentioned above.

**simcode.py — M/M/1 Queue Simulation**

This script simulates a single-server M/M/1 queue and is used to study queue occupancy and busy-period behavior.

Key features:

Discrete-event simulation of arrivals and departures

Tracks:

Number of customers seen at arrivals

Number of customers seen at departures

Busy-period durations

Empirical results are compared against theoretical predictions

Outputs:

CCDF of customers in the system at arrivals and departures

CCDF of busy-period lengths

Overlay of theoretical CCDF 
P(X≥n)=ρn
P(X≥n)=ρ
n

This script validates the PASTA property and illustrates how busy periods grow as traffic intensity increases.

**simcode2.py — Multi-Server Load-Balancing Simulation**

This script simulates a multi-server system with parallel queues, focusing on load-balancing strategies and waiting-time distributions.

Routing policies implemented:

Uniform Random

Join-the-Shortest-Queue (JSQ)

Power-of-Two-Choices (Po2C)

Key features:

Supports configurable arrival rates, number of servers, and simulation runs

Computes CCDFs of total waiting time

Compares empirical results across routing policies

Includes theoretical CCDF for uniform-random routing as a baseline

Outputs:

Log-scale CCDF plots showing the performance gap between policies

Clear demonstration of JSQ optimality and Po2C’s near-optimal behavior
