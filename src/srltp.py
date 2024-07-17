from gurobipy import Model, GRB, quicksum

# Example data (you will need to provide actual data)
V = [1, 2, 3]  # List of retailer nodes
V_plus = [1]  # List of surplus nodes
V_minus = [2, 3]  # List of deficit nodes
Q_max = 10  # Vehicle capacity
T_max = 100  # Maximum tour duration
c = {(i, j): 1 for i in V for j in V}  # Cost matrix (example values)
p = {i: 1 for i in V}  # Profit or loss per unit at location i
q = {i: 5 for i in V}  # Quantity balance at location i

# Create a new model
model = Model("SRLTP")

# Decision variables
x = model.addVars(V, V, vtype=GRB.BINARY, name="x") # Arc between nodes i and j
z = model.addVars(V, vtype=GRB.BINARY, name="z")    # Profitable tour exists
y = model.addVars(V, vtype=GRB.CONTINUOUS, name="y")# 
Q = model.addVars(V, vtype=GRB.CONTINUOUS, name="Q")
s = model.addVars(V, vtype=GRB.CONTINUOUS, name="s")

# Objective function
model.setObjective(quicksum(p[i] * y[i] for i in V) - quicksum(c[i, j] * x[i, j] for i in V for j in V), GRB.MAXIMIZE)

# Constraints

# Flow balance
model.addConstrs((quicksum(x[i, j] for j in V if j != i) == z[i] for i in V), name="flow_balance_out")
model.addConstrs((quicksum(x[j, i] for j in V if j != i) == z[i] for i in V), name="flow_balance_in")

# Start and end at the depot (node 0)
model.addConstr(quicksum(x[0, j] for j in V) == 1, name="start_at_depot")
model.addConstr(quicksum(x[j, 0] for j in V) == 1, name="end_at_depot")

# Vehicle capacity
model.addConstrs((Q[i] <= 0 for i in V), name="vehicle_capacity_max")
model.addConstrs((Q[i] >= 0 for i in V), name="vehicle_capacity_min")

# Load balance
model.addConstrs((Q[j] == Q[i] + q[j] * y[j] for i in V for j in V if i != j), name="load_balance")

# Time constraints
model.addConstrs((s[i] + c[i, j] <= s[j] + T_max * (1 - x[i, j]) for i in V for j in V if i != j), name="time_constraints")

# Delivery and pickup quantities
model.addConstrs((0 <= y[i] <= 1 for i in V), name="pickup_delivery_quantities")

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
