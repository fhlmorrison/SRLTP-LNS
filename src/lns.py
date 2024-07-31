from gurobipy import Model, GRB, quicksum

import random


distances = {
    (0, 1): 5.8,
    (0, 2): 20,
    (0, 3): 20.4,
    (0, 4): 18.7,
    (0, 5): 15.3,
    (0, 6): 6.3,
    (0, 7): 13.6,
    (1, 2): 19.5,
    (1, 3): 19.9,
    (1, 4): 20.9,
    (1, 5): 18.6,
    (1, 6): 14.4,
    (1, 7): 10.9,
    (2, 3): 5.1,
    (2, 4): 14.3,
    (2, 5): 26.3,
    (2, 6): 19.9,
    (2, 7): 28.5,
    (3, 4): 13.9,
    (3, 5): 25.9,
    (3, 6): 25.2,
    (3, 7): 28.1,
    (4, 5): 20.9,
    (4, 6): 24.2,
    (4, 7): 27,
    (5, 6): 8.1,
    (5, 7): 22.6,
    (6, 7): 18
}

COST_PER_KM = 1.605

V = [1, 2, 3, 4, 5, 6, 7]
V_0 = [0] + V  # List of nodes including the depot

V_plus = [1, 5, 6]  # List of surplus nodes
V_minus = [2, 3, 4, 7]  # List of deficit nodes
Q_max = 44  # Vehicle capacity
T_max = 8400  # Maximum tour duration
p = {1: 156, 2: 102, 3: 219, 4: 100, 5: 91, 6: 200, 7: 91}
q = {i: 0 for i in V_0}
for i in V_plus:
    q[i] = random.randint(1, 12)
for i in V_minus:
    q[i] = -random.randint(1, 12)

edge_costs = {x: y*COST_PER_KM for x, y in distances.items()}

def heuiristic(node, ):
    
    return

# Code translated from the original pseudocode in the paper

# eta = p + p/(1+d)

DAMPING_FACTOR = 0.9

AVERAGE_DELETION_RATE = 0.1

def calculate_pis(etas):
    q = AVERAGE_DELETION_RATE
    k = DAMPING_FACTOR
    
    eta_min = min(etas)
    eta_max = max(etas)
    eta_mean = sum(etas) / len(etas)
    
    eta_star = max(eta_mean - eta_max, eta_mean - eta_min)
    
    q_star = min(q, 1 - q)
    
    pis = [q + (k * (eta_mean - eta) / eta_star) * q_star for eta in etas]
    

# Tour = list of nodes in order
    
def optimize_local(V, q, p, Q_max, name):
    # gurobi model
    
    model = Model(name)
    
    Q = model.addVars(V, vtype=GRB.CONTINUOUS, name="Q")
    y = model.addVars(V, vtype=GRB.CONTINUOUS, name="y")
    
    model.setObjective(quicksum(p[i] * y[i] for i in V), GRB.MAXIMIZE)
    
    model.addConstrs((Q[i] <= Q[i+1] for i in range(len(V) - 1)), name="sequence_feasibility")
    
    model.addConstr(Q[0] == 0, name="initial_load")
    
    model.addConstrs((Q[i] >= 0 for i in V), name="vehicle_capacity_min")
    model.addConstrs((Q[i] <= Q_max for i in V), name="vehicle_capacity_max")
    
    model.addConstrs((y[i] <= 1 for i in V), name="quantity_shipped")
    model.addConstrs((y[i] >= 0 for i in V), name="quantity_shipped")
    
    model.optimize()
    
    return model

# TODO: Add two nodes and solve neighborhood search problem
def MIPNeighborhood(N, N_prime, x):
    return x

def local_search_with_mip_neighborhood(x0, f, MIP_neighborhood, set_CP, set_CP_prime, swap, max_iterations=100):
    
    # Initialization
    i = 0
    N = 2
    x = x0
    T0 = 0.50
    
    while f(x) > f(x0) or i <= 3:
        if f(x) > f(x0):
            x = x0
        else:
            x0 = x
        
        # Perform MIP neighborhood search
        x = MIP_neighborhood(N, N-1, x)
        
        # Check for improvement
        if f(x) >= f(x0):
            i += 1
            if i == 1:
                set_CP(1, T0)
            elif i == 2:
                set_CP_prime(3 * T0)
            elif i == 3:
                set_CP_prime(6 * T0)
                swap(i-1, N)
                i = 0
            elif i > 3:
                break
        else:
            i = 0

    return x

# Example usage
# Define the necessary functions (f, MIP_neighborhood, set_CP, set_CP_prime, swap)
# and initial values (x0) before calling the function
