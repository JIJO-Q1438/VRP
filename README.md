================Vehicle Routing Problem=========================

The problem of finding the optimal path for delivery trucks is 
analyzed and created solution. 

---> Number of trucks used : 6 (can be changed)
---> Delivery routes : 6 

If the truck runs out of delivery items they return to the depot, 
fill stocks and continue delivering to consumers.

Execute the code == run.py
check routing process == Vehicle_routing.py

Source flow
-----------
1. Generate consumers (here we used 100) and their locations.
2. Cluster them to groups or zones (we split to 6)
3. Allot depot position.
4. Find the maximum and minimum distance between consumers and depot.
5. Create demand for each consumers.
6. Dispatch and follow each delivery items.
7. Update each delivery with the remaining stocks.

