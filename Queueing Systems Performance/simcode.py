# =========================
# M/M/1 Queue Simulation
# =========================

import random
import math
import matplotlib.pyplot as plt

# --- Helper functions ---
def exp_rv(rate):
    """Generate an exponential random variable using uniform [0,1]."""
    return -math.log(random.random()) / rate

def compute_ccdf_int(data):
    """Compute CCDF for integer data."""
    max_val = int(max(data))
    ccdf = []
    N = len(data)
    for n in range(max_val + 1):
        count = sum(1 for x in data if x >= n)
        ccdf.append(count / N)
    return list(range(max_val + 1)), ccdf

def compute_ccdf_float(data, num_bins=50):
    """Compute CCDF for float data by binning."""
    min_val = min(data)
    max_val = max(data)
    if max_val == min_val:
        return [min_val], [1.0]
    
    bin_width = (max_val - min_val) / num_bins
    bins = [min_val + i * bin_width for i in range(num_bins + 1)]
    N = len(data)
    ccdf = [sum(1 for x in data if x >= b)/N for b in bins]
    return bins, ccdf

# --- M/M/1 simulation ---
def mm1_simulation(lam, mu=1.0, N=10000, seed=None):
    if seed is not None:
        random.seed(seed)

    t = 0.0
    n = 0
    N_dep = 0
    next_arrival = exp_rv(lam)
    next_departure = float('inf')

    arrival_times, waiting_times = [], []
    X_arrivals, D_departures = [], []
    B_periods, I_periods = [], []

    busy = False
    current_busy_start = 0.0
    queue = []

    while N_dep < N:
        if next_arrival < next_departure:
            # Arrival
            t = next_arrival
            X_arrivals.append(n)
            arrival_times.append(t)
            queue.append(t)
            n += 1
            next_arrival = t + exp_rv(lam)

            if n == 1:
                busy = True
                next_departure = t + exp_rv(mu)
                current_busy_start = t
        else:
            # Departure
            t = next_departure
            N_dep += 1
            n -= 1
            a_time = queue.pop(0)
            waiting_times.append(t - a_time)
            D_departures.append(n)

            if n > 0:
                next_departure = t + exp_rv(mu)
            else:
                next_departure = float('inf')
                busy = False
                B_periods.append(t - current_busy_start)

        # Idle periods
        if n == 0 and not busy:
            I_periods.append(next_arrival - t)

    return X_arrivals, D_departures, B_periods

# --- Run simulation ---
lambdas = [0.7, 0.8, 0.9]
K = 10
N = 10000
mu = 1.0

# Store results for plotting
results_X = {}
results_D = {}
results_B = {}

for lam in lambdas:
    all_X, all_D, all_B = [], [], []
    for k in range(K):
        X, D, B = mm1_simulation(lam, mu, N, seed=1234 + k)
        all_X.append(X)
        all_D.append(D)
        all_B.append(B)

    # Merge results
    merged_X = [x for sublist in all_X for x in sublist]
    merged_D = [d for sublist in all_D for d in sublist]
    merged_B = [b for sublist in all_B for b in sublist]

    results_X[lam] = compute_ccdf_int(merged_X)
    results_D[lam] = compute_ccdf_int(merged_D)
    results_B[lam] = compute_ccdf_float(merged_B, num_bins=50)

# --- Plot CCDF of arrivals, departures, and theoretical ---
plt.figure(figsize=(10,6))
for lam in lambdas:
    n_vals_X, ccdf_X = results_X[lam]
    n_vals_D, ccdf_D = results_D[lam]

    # Theoretical CCDF: ρ^n
    rho = lam / mu
    ccdf_theory = [rho**n for n in n_vals_X]

    plt.semilogy(n_vals_X, ccdf_X, label=f'X arrivals λ={lam}')
    plt.semilogy(n_vals_D, ccdf_D, '--', label=f'D departures λ={lam}')
    plt.semilogy(n_vals_X, ccdf_theory, 'k:', linewidth=2, label=f'Theory λ={lam}')

plt.xlabel('Number of customers (n)')
plt.ylabel('CCDF (log scale)')
plt.title('CCDF of Customers in System (Arrivals, Departures, Theory)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Plot CCDF of busy periods ---
plt.figure(figsize=(10,6))
for lam in lambdas:
    bins_B, ccdf_B = results_B[lam]
    plt.semilogy(bins_B, ccdf_B, label=f'λ={lam}')

plt.xlabel('Busy period length')
plt.ylabel('CCDF (log scale)')
plt.title('CCDF of Busy Periods')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
