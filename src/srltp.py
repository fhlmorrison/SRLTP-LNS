from gurobipy import Model, GRB, quicksum

# Example data (you will need to provide actual data)
V = [1, 2, 3]  # List of retailer nodes
V_0 = [0] + V  # List of nodes including the depot

V_plus = [1]  # List of surplus nodes
V_minus = [2, 3]  # List of deficit nodes
Q_max = 10  # Vehicle capacity
T_max = 100  # Maximum tour duration
c = {(i, j): 1 for i in V_0 for j in V_0}  # Cost matrix (example values)
p = {i: 1 for i in V}  # Profit or loss per unit at location i
q = {i: 5 for i in V_0}  # Quantity balance at location i

M = 1000  # Big M value

# Create a new model
model = Model("SRLTP")


# Decision variables
x = model.addVars(V_0, V_0, vtype=GRB.BINARY, name="x") # Arc between nodes i and j
z_all = model.addVar(vtype=GRB.BINARY, name="z_all") # Profitable route exists
z = model.addVars(V_0, vtype=GRB.BINARY, name="z")    # Node i visited
y = model.addVars(V_0, vtype=GRB.CONTINUOUS, name="y")# Portion of quantity to pickup/deliver at node i
Q = model.addVars(V_0, vtype=GRB.CONTINUOUS, name="Q")# Load of vehicle when leaving node i
s = model.addVars(V_0, vtype=GRB.CONTINUOUS, name="s")# Time when leaving node i
t = model.addVars(V_0, V_0, vtype=GRB.BINARY, name="t")  # Time spent between nodes i and j

# Objective function (1)
model.setObjective(quicksum(p[i] * y[i] for i in V) - quicksum(c[i, j] * x[i, j] for i in V for j in V), GRB.MAXIMIZE)

# Constraints

# Flow balance (2)
model.addConstrs((quicksum(x[i, j] for j in V_0 if j != i) == z[i] for i in V_0), name="flow_balance_out")
model.addConstrs((quicksum(x[j, i] for j in V_0 if j != i) == z[i] for i in V_0), name="flow_balance_in")

# Profitable route exists if nodes are visited (3)
model.addConstr(quicksum(z[i] for i in V) <= M*z_all, name="profitable_route_exists")

# Start and end at the depot (node 0) (4)
model.addConstr(quicksum(x[0, j] for j in V) == 1, name="start_at_depot")
model.addConstr(quicksum(x[j, 0] for j in V) == 1, name="end_at_depot")

# Quantity shipped only if route exists (5)
model.addConstrs((y[i] <= z[i] for i in V), name="quantity_shipped")

# Subtour elimination (6')
model.addConstrs(s[i] + t[i, j] <= s[j] + M*(1-x[i, j]) for i in V_0 for j in V)

# Sequence feasibility (7a' + 7b')
model.addConstrs((Q[j] <= Q[i] for i in V for j in V_0), name="sequence_feasibility")
model.addConstrs((Q[i] + q[j]*y[j] <= Q[j] + M*(1-x[i, j]) for i in V for j in V_0), name="sequence_feasibility")

# Initial load is empty (8)
model.addConstr(Q[0] == 0, name="initial_load")

# Vehicle capacity (9)
model.addConstrs((Q[i] <= 0 for i in V_0), name="vehicle_capacity_max")
model.addConstrs((Q[i] >= 0 for i in V_0), name="vehicle_capacity_min")

# Time limit (10)
model.addConstr((quicksum(t[i, j] * x[i, j] for i in V_0 for j in V_0) <= T_max ), name="time_limit")

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
