import Vehicle_routing

consumers = (0,100)
epoch = 10
wage = 240
tot_cost = 600
fixed_cost = 200
fuel_discharge_cost = 34
vehicle_capacity = 1200
num_vehicles = 6

a = Vehicle_routing.VRP(consumers,epoch,wage,tot_cost,fixed_cost,fuel_discharge_cost,vehicle_capacity,num_vehicles)
a.drive()

