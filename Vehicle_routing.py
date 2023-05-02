import numpy as np
import random as r
import math
import copy
import matplotlib.pyplot as plt

class VRP():
    
    def __init__(self, consumers, epoch, wage, tot_cost, fixed_cost, 
                 fuel_discharge_cost, vehicle_capacity, num_vehicles, **kwargs):
        self.consumerX = consumers[0]
        self.consumerY = consumers[1]
        self.epoch = epoch
        self.wage = wage
        self.tot_cost = wage*60
        self.fixed_cost = tot_cost
        self.fuel_discharge_cost = fuel_discharge_cost
        self.v_c = vehicle_capacity
        self.L = num_vehicles
        self.lim = 410
        
    def consumer_pos(self):        
        #generate_consumer_position
        path_x = [r.randint(self.consumerX, self.consumerY) for i in range(self.consumerX, self.consumerY)]
        path_y = [r.randint(self.consumerX, self.consumerY) for i in range(self.consumerX, self.consumerY)]
    
        #consumer_position
        self.consumer_range = np.stack((path_x, path_y), axis=1) 
        return self.consumer_range
    
    def depot(self):
        #depot_position
        self.depot = sum(self.consumer_range[:,0])/len(self.consumer_range), sum(self.consumer_range[:,1])/len(self.consumer_range)
        return self.depot
   
    def find_cluster(self):
        #clustering (Robust deep_Kmeans)
        from sklearn_extra.robust import RobustWeightedKMeans
        RDKMeans = RobustWeightedKMeans(n_clusters=6, weighting='mom', max_iter=100).fit(self.consumer_range)
         
        #clustered_consumer_position
        self.zone_path_x, self.zone_path_y = list(), list()
        for cen_ in range(len(RDKMeans.cluster_centers_)):
            clus = self.consumer_range[RDKMeans.labels_ == cen_].T
            self.zone_path_x.append(clus[0])
            self.zone_path_y.append(clus[1])
        self.zone = (self.zone_path_x, self.zone_path_y)
       
        return self.zone_path_x, self.zone_path_y
   
    def make_group(self):
        #consumer_count_@each_zone
        labels = list(); self.consumer_count = list(); zone_count=1
        print("\nCollecting consumer count ...")
        plt.pause(0.8)
        for zX, zY in zip(self.zone_path_x,self.zone_path_y):
            name = "zone"
            cons_count=1; cons = list()
            for l1, l2 in zip(zX, zY):
                labels.append(name+str(zone_count)+"_"+str(cons_count))
                cons.append(cons_count)
                cons_count+=1 
            print(f"Consumer count at zone {zone_count} : {len(cons)}")
            plt.pause(0.3)
            self.consumer_count.append(cons)
            zone_count+=1
        return self.consumer_count
         
    def create_demand(self):
        #consumer_demand
        demands = list() 
        a=1 
        for cons in self.consumer_count:
            b=1; dem=list()
            for i in cons:
                sel_demand = r.randrange(self.v_c)
                sel_demand = round(sel_demand/5)
                print(f"Demand of consumer {b} at zone_{a} : {sel_demand}")
                dem.append(sel_demand)
                b+=1
            demands.append(dem)
            a+=1
        
        #copy_of_original_demand    
        self.demand_ = copy.deepcopy(demands)
        #copy_of_original_vehicle_capacity
        self.v_c_ = copy.deepcopy(self.v_c) 
        return self.demand_, self.v_c_
   
    def find_distance(self):
        self.dist=list(); s2=1
        print("\nCalculating consumer distance ...\n")
        plt.pause(2)
        for x, y in zip(self.zone_path_x,self.zone_path_y):
            s1=0; ds = list()
            for d1 ,d2 in zip(x, y):
                p1 = self.depot
                p2 = [d1, d2]
                distance = math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))    
                ds.append(distance)
                s1+=1
                print(f"Distance of consumer {s1} at zone {s2} is {distance}")
                plt.pause(0.02)
                p1=p2
            self.dist.append(ds)
            s2+=1
        
    def dispatch_order(self,dep,xy):
        x,y = dep[0],dep[1]
        x1,y1 = xy[0],xy[1]
        dist = []
        for i in range(len(x1)):
            xx = x-x1[i]
            yy = y-y1[i]
            xy = xx**2 + yy**2
            dist.append(np.sqrt(xy))
        min_dit = min(dist)
        ind  = np.where(dist == min_dit )[0][0]
        return ind

    def update_dispatch_order(self):
        self.dispatch_order_=list()
        for x, y in zip(self.zone_path_x,self.zone_path_y):
            index = []
            x_ = list(x.copy()) ; y_ = list(y.copy()) ;
            x = list(x) ; y = list(y) ;
            dep = self.dispatch_order(self.depot, [x,y]);
            index.extend([i for i,j in enumerate(zip(x_,y_)) if x[dep] == x_[i] and y[dep] == y_[i] ])
            ytemp = y[dep] ; xtemp = x[dep]
            x = [x[i] for i in range(len(x)) if i != dep];
            y = [y[i] for i in range(len(y)) if i != dep]
            while len(x)>0:
                dit = self.dispatch_order([xtemp,ytemp], [x,y])
                ytemp = y[dit] ; xtemp = x[dit]
                index.extend([i for i,j in enumerate(zip(x_,y_)) if x[dit]==x_[i] and y[dit] == y_[i] ])
                x = [x[i] for i in range(len(x)) if i != dit]
                y = [y[i] for i in range(len(y)) if i != dit]
                # index.append(dit)
            self.dispatch_order_.append(index)
            
        return self.dispatch_order_
            
    def plot_truck(self):
        #plot
        self.v1=self.v2=self.v3=self.v4=self.v5=self.v6=self.depot 
        cols = ["red","blue","#964B00","green","orange","cyan"]
        fig, self.ax = plt.subplots(figsize = (8, 6))
        for i,j,k,l in zip(self.zone_path_x,self.zone_path_y,cols,self.dispatch_order_):
            a = [self.depot[0],i[l[0]]]; b=[self.depot[1],j[l[0]]]
            c = [self.depot[0],i[l[-1]]]; d=[self.depot[1],j[l[-1]]]
            plt.scatter(i[l], j[l],linewidths = 0.5,marker ="o",color=k,edgecolor ="g",s = 25)
            plt.plot(i[l], j[l], linewidth=0.5, alpha=0.5, c=k)
            plt.scatter(self.depot[0], self.depot[1], linewidths = 10, marker ="s", s = 50, c ="black")
            plt.plot(a, b, linewidth=0.5, alpha=0.5, c =k)
            plt.plot(c, d, linewidth=0.5, alpha=0.5, c =k)

        self.red_truck, = self.ax.plot(self.v1[0], self.v1[1], color='red', marker='^', linestyle='None',markersize=10)
        self.blue_truck, = self.ax.plot(self.v2[0], self.v2[1], color='blue', marker='^', linestyle='None',markersize=10)
        self.brown_truck, = self.ax.plot(self.v3[0], self.v3[1], color='#964B00', marker='^', linestyle='None',markersize=10)
        self.green_truck, = self.ax.plot(self.v4[0], self.v4[1], color='green', marker='^', linestyle='None',markersize=10)
        self.orange_truck, = self.ax.plot(self.v5[0], self.v5[1], color='orange', marker='^', linestyle='None',markersize=10)
        self.cyan_truck, = self.ax.plot(self.v6[0], self.v6[1], color='cyan', marker='^', linestyle='None',markersize=10)
        
    def update_truck_movement(self,dispatch_order,demand_,zone_path_x,zone_path_y,consumer_count,truck,v,z,s):
        print(f'\n{s} truck started to dispatch !')
        truck_avail = 0; 
        for i,j in enumerate(range(len(dispatch_order))):

                if demand_[i] <= self.v_c_:
                    dispatched_truck = (zone_path_x[dispatch_order[i]], zone_path_y[dispatch_order[i]])
                    truck.set_data(*dispatched_truck)            
                    self.ax.scatter(*dispatched_truck, s=25, fc='gray', zorder=3)
                    self.ax.xaxis.set_label_position('top')
                    self.ax.annotate('dispatched', xy = dispatched_truck, fontsize=6)
                    plt.pause(0.05)
                    print(f"\nDispatched to Zone {z} Consumer : {consumer_count[dispatch_order[i]]}")
                    self.v_c_ -= demand_[i]            
                    if i != len(demand_)-1:
                        print(f'products remaining : {self.v_c_} , next_dispatch : {demand_[i+1]}')            
                    plt.pause(0.5)
                           
                if len(demand_)-1 == truck_avail:
                    truck.set_data(v[0], v[1])
                    reload_truck = (v[0], v[1])
                    self.ax.scatter(*reload_truck, s=25, fc="None", zorder=3)
                    print(f"\n{s} truck completed the dispatch !")
                    pass
                               
                else:
                    if demand_[i] > self.v_c_:
                        truck.set_data(v[0], v[1])
                        reload_truck = (v[0], v[1])
                        self.ax.scatter(*reload_truck, s=25, fc="None", zorder=3)
                        annote=self.ax.text(*reload_truck, "     refilling", fontsize = 6, color = 'black')
                        print(f"\n{s} truck returning to refill ...")           
                        self.v_c_ = self.v_c
                        plt.pause(3)
                        annote.remove()
                    
                truck_avail += 1
                plt.pause(2)
    
    def track_dispatch(self):
        self.update_truck_movement(self.dispatch_order_[0],self.demand_[0],self.zone_path_x[0],
                                self.zone_path_y[0],self.consumer_count[0],self.red_truck,self.v1,'1','Red')
        self.update_truck_movement(self.dispatch_order_[1],self.demand_[1],self.zone_path_x[1],
                                self.zone_path_y[1],self.consumer_count[1],self.blue_truck,self.v2,'2','Blue')
        self.update_truck_movement(self.dispatch_order_[2],self.demand_[2],self.zone_path_x[2],
                                self.zone_path_y[2],self.consumer_count[2],self.brown_truck,self.v3,'3','Brown')
        self.update_truck_movement(self.dispatch_order_[3],self.demand_[3],self.zone_path_x[3],
                                self.zone_path_y[3],self.consumer_count[3],self.green_truck,self.v4,'4','Green')
        self.update_truck_movement(self.dispatch_order_[4],self.demand_[4],self.zone_path_x[4],
                                self.zone_path_y[4],self.consumer_count[4],self.orange_truck,self.v5,'5','Orange')
        self.update_truck_movement(self.dispatch_order_[5],self.demand_[5],self.zone_path_x[5],
                                self.zone_path_y[5],self.consumer_count[5],self.cyan_truck,self.v6,'6','Cyan')
        
    def drive(self):
        self.consumer_pos(); self.depot(); self.find_cluster(); self.make_group(); self.create_demand(); self.find_distance(); self.update_dispatch_order(); self.plot_truck(); self.track_dispatch() 
        
