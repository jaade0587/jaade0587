# =========================
# Multi-Queue Simulation
# =========================

import random
import math
import matplotlib.pyplot as plt

# --- Helper functions ---
def exp_rv(rate):
    """Generate exponential random variable using uniform [0,1]."""
    return -math.log(random.random()) / rate

def compute_ccdf_float(data, num_bins=50):
    """Compute CCDF for float data by binning."""
    min_val = min(data)
    max_val = max(data)
    if max_val == min_val:
        bins = [min_val]
        ccdf = [1.0]
        return bins, ccdf

    bin_width = (max_val - min_val) / num_bins
    bins = [min_val + i * bin_width for i in range(num_bins + 1)]
    ccdf = []
    N = len(data)
    for b in bins:
        count = 0
        for x in data:
            if x >= b:
                count += 1
        ccdf.append(count / N)
    return bins, ccdf

# --- Multi-queue M/M/1 simulation ---
def multi_queue_simulation(lam, m=10, mu=1.0, N=10000, policy="jsq", seed=None):
    if seed is not None:
        random.seed(seed)

    # Initialize queues
    queues = [[] for _ in range(m)]
    t = 0.0
    waiting_times = []

    for _ in range(N):
        # Arrival time
        t += exp_rv(lam)

        # Choose a queue based on policy
        if policy == "uniform":
            q_idx = random.randint(0, m - 1)
        elif policy == "jsq":
            # Join the shortest queue
            lengths = [len(q) for q in queues]
            min_len = min(lengths)
            q_idx = lengths.index(min_len)
        elif policy == "p2c":
            # Pick two queues randomly
            i, j = random.sample(range(m), 2)
            q_idx = i if len(queues[i]) <= len(queues[j]) else j
        else:
            raise ValueError("Unknown policy")

        # Determine service start
        queue = queues[q_idx]
        if queue:
            last_departure = queue[-1]
            start_service = max(last_departure, t)
        else:
            start_service = t

        # Departure time
        dep_time = start_service + exp_rv(mu)
        queue.append(dep_time)
        waiting_times.append(dep_time - t)

    return waiting_times

# --- Run simulation ---
lambdas = [7, 8, 9]
m = 10
mu = 1.0
N = 10000
K = 10

policies = ["jsq", "p2c", "uniform"]

for lam in lambdas:
    plt.figure(figsize=(8, 5))
    for policy in policies:
        all_waiting = []
        for k in range(K):
            w_times = multi_queue_simulation(lam, m, mu, N, policy=policy, seed=1234 + k)
            all_waiting.extend(w_times)
        bins, ccdf = compute_ccdf_float(all_waiting, num_bins=100)
        plt.semilogy(bins, ccdf, label=f"{policy.upper()} policy")

        # Add theoretical uniform-random CCDF
        if policy == "uniform":
            # Total waiting time ~ Exponential(μ - λ/m)
            rate = mu - lam / m
            ccdf_theory = [math.exp(-rate * x) for x in bins]
            plt.semilogy(bins, ccdf_theory, 'k--', linewidth=2, label="Theory (Uniform)")

    plt.xlabel("Total waiting time")
    plt.ylabel("CCDF (log scale)")
    plt.title(f"Multi-Queue CCDF, λ={lam}, m={m}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
