from gurobipy import Model, GRB, quicksum
import sys
import random
import numpy as np


V = [1, 2, 3, 4, 5, 6, 7]
V_0 = [0] + V  # List of nodes including the depot

V_plus = [1, 5, 6]  # List of surplus nodes
V_minus = [2, 3, 4, 7]  # List of deficit nodes
Q_max = 44  # Vehicle capacity
T_max = 8400  # Maximum tour duration
c = {
    (0, 0): 0,
    (0, 1): 9.31,
    (1, 0): 9.31,
    (0, 2): 32.10,
    (2, 0): 32.10,
    (0, 3): 32.74,
    (3, 0): 32.74,
    (0, 4): 30.01,
    (4, 0): 30.01,
    (0, 5): 24.56,
    (5, 0): 24.56,
    (0, 6): 10.11,
    (6, 0): 10.11,
    (0, 7): 21.83,
    (7, 0): 21.83,
    (1, 1): 0,
    (1, 2): 31.30,
    (2, 1): 31.30,
    (1, 3): 31.94,
    (3, 1): 31.94,
    (1, 4): 33.54,
    (4, 1): 33.54,
    (1, 5): 29.85,
    (5, 1): 29.85,
    (1, 6): 23.11,
    (6, 1): 23.11,
    (1, 7): 17.49,
    (7, 1): 17.49,
    (2, 2): 0,
    (2, 3): 8.19,
    (3, 2): 8.19,
    (2, 4): 22.95,
    (4, 2): 22.95,
    (2, 5): 42.21,
    (5, 2): 42.21,
    (2, 6): 31.94,
    (6, 2): 31.94,
    (2, 7): 45.74,
    (7, 2): 45.74,
    (3, 3): 0,
    (3, 4): 22.31,
    (4, 3): 22.31,
    (3, 5): 41.57,
    (5, 3): 41.57,
    (3, 6): 40.45,
    (6, 3): 40.45,
    (3, 7): 45.10,
    (7, 3): 45.10,
    (4, 4): 0,
    (4, 5): 33.54,
    (5, 4): 33.54,
    (4, 6): 38.84,
    (6, 4): 38.84,
    (4, 7): 43.34,
    (7, 4): 43.34,
    (5, 5): 0,
    (5, 6): 13,
    (6, 5): 13,
    (5, 7): 36.27,
    (7, 5): 36.27,
    (6, 6): 0,
    (6, 7): 28.89,
    (7, 6): 28.89,
    (7, 7): 0,
}
p = {1: 156, 2: 102, 3: 219, 4: 100, 5: 91, 6: 200, 7: 91}
q = {i: 0 for i in V_0}
for i in V_plus:
    q[i] = random.randint(1, 12)
for i in V_minus:
    q[i] = -random.randint(1, 12)

F = 400  # Fixed cost per vehicle

M = sys.maxsize  # Big M value

# Create a new model
model = Model("SRLTP")


# Decision variables
x = model.addVars(V_0, V_0, vtype=GRB.BINARY, name="x")  # Arc between nodes i and j
z_all = model.addVar(vtype=GRB.BINARY, name="z_all")  # Profitable route exists
z = model.addVars(V_0, vtype=GRB.BINARY, name="z")  # Node i visited
y = model.addVars(
    V_0, vtype=GRB.CONTINUOUS, name="y"
)  # Portion of quantity to pickup/deliver at node i
Q = model.addVars(
    V_0, vtype=GRB.CONTINUOUS, name="Q"
)  # Load of vehicle when leaving node i
s = model.addVars(V_0, vtype=GRB.CONTINUOUS, name="s")  # Time when leaving node i
t = model.addVars(
    V_0, V_0, vtype=GRB.BINARY, name="t"
)  # Time spent between nodes i and j

# Objective function (1)
model.setObjective(
    quicksum(p[i] * y[i] for i in V)
    - quicksum(c[i, j] * x[i, j] for i in V for j in V)
    - F * z_all,
    GRB.MAXIMIZE,
)

# Constraints

# Flow balance (2)
model.addConstrs(
    (quicksum(x[i, j] for j in V_0 if j != i) == z[i] for i in V_0),
    name="flow_balance_out",
)
model.addConstrs(
    (quicksum(x[j, i] for j in V_0 if j != i) == z[i] for i in V_0),
    name="flow_balance_in",
)

# Profitable route exists if nodes are visited (3)
model.addConstr(quicksum(z[i] for i in V) <= M * z_all, name="profitable_route_exists")

# Start and end at the depot (node 0) (4)
model.addConstr(quicksum(x[0, j] for j in V) == 1, name="start_at_depot")
model.addConstr(quicksum(x[j, 0] for j in V) == 1, name="end_at_depot")

# Quantity shipped only if route exists (5)
model.addConstrs((y[i] <= z[i] for i in V), name="quantity_shipped")

# Subtour elimination (6')
model.addConstrs(s[i] + t[i, j] <= s[j] + M * (1 - x[i, j]) for i in V_0 for j in V)

# Sequence feasibility (7a' + 7b')
model.addConstrs((Q[j] <= Q[i] for i in V for j in V_0), name="sequence_feasibility")
model.addConstrs(
    (Q[i] + q[j] * y[j] <= Q[j] + M * (1 - x[i, j]) for i in V for j in V_0),
    name="sequence_feasibility",
)

# Initial load is empty (8)
model.addConstr(Q[0] == 0, name="initial_load")

# Vehicle capacity (9)
model.addConstrs((Q[i] <= 0 for i in V_0), name="vehicle_capacity_max")
model.addConstrs((Q[i] >= 0 for i in V_0), name="vehicle_capacity_min")

# Time limit (10)
model.addConstr(
    (quicksum(t[i, j] * x[i, j] for i in V_0 for j in V_0) <= T_max), name="time_limit"
)

# Binary variables (11)
# x, z_all, z already defined as binary in the variable declaration

# Non-negative start times (12)
model.addConstrs((s[i] >= 0 for i in V_0), name="non_negative_start_times")

# Delivery and pickup quantities (13)
model.addConstrs((0 <= y[i] for i in V), name="pickup_delivery_quantities")
model.addConstrs((y[i] <= 1 for i in V), name="pickup_delivery_quantities")

# Optimize the model
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal objective value:", model.ObjVal)
    for v in model.getVars():
        if v.x > 0:
            print(f"{v.varName}: {v.x}")
else:
    print("No optimal solution found.")
