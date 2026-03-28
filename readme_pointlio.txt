
----------------3/26/26 point_lio drift with bag4 data---
bag4 recorded with use_system_time=True, might skew time due to the heavy traffic

------------------------------------------
For Point-LIO, I would try this first:

set use_system_timestamp: false

restart everything

keep the sensor absolutely still for the first several seconds

Because with an internal IMU, if you still get immediate “drift away” behavior, bad timestamping is a more likely cause than extrinsic rotation.

Why this is more likely than extrinsic in your setup
Because with Unitree L2 internal IMU:

LiDAR and IMU come from the same hardware path 
GitHub
+1

the coordinate axes are already aligned in hardware for L2 
GitHub

So if it still drifts badly, the likely failure modes mov


