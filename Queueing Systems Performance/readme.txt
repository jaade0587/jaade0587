-----PART 1----------


This Python script simulates an M/M/1 queue system and computes empirical distributions for:

Number of customers in the system at arrival and departure instants (X arrivals and D departures).

Busy periods of the server.

The script computes CCDFs (Complementary Cumulative Distribution Functions) from simulation data and compares the number of customers in the system against theoretical values (ρ^n, where ρ = λ/μ).

The simulation uses exponentially distributed interarrival and service times and repeats each scenario K times to obtain averaged results.


Requirements:

-Python 

-Matplotlib

Install dependencies using 'pip install matplotlib' in command-line terminal.

To run the simulation, input 'python simcode.py' into a command-line terminal, then wait for a few seconds. This will run the M/M/1 simulation for λ ∈ {0.7, 0.8, 0.9} and repeat each simulation K = 10 times for averaging.

The script will also generate two simultaneous figures:

Figure 1: CCDF of the number of customers in the system at arrivals and departures, with theoretical comparison.

Figure 2: CCDF of busy periods for the server.

All plots use a logarithmic y-axis to better visualize tail probabilities.


-----PART 2----------


The following contains Python simulations for an m-queue system with three scheduling policies:

Uniform-Random – jobs are assigned randomly to any queue.

Join-the-Shortest-Queue (JSQ) – jobs are assigned to the queue with the fewest jobs.

Power-of-Two-Choices (Po2C) – jobs are assigned to the shorter of two randomly selected queues.

The scripts generate CCDF plots of total waiting time for different arrival rates (λ = 7, 8, 9) and compare simulated results with theoretical predictions for the uniform-random policy.


Requirements:

-Python 

-Matplotlib

You can install dependencies using 'pip install matplotlib' in command-line terminal.

To run the script, input 'python simcode2.py' in a command-line terminal, then wait for a few seconds. The script will generate CCDF plots for all three scheduling policies and overlay the theoretical uniform-random CCDF. Three figures will be displayed sequentially.

