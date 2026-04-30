4/28/26:
hplap, bag:

./start_bagrun_uni.sh /home/student/bag6_systimefalse True

-bag6: wangrobot, lidar no obs, flot, static, hm20, pointlio odom stable

-bag7: wangrobot, lidar no obs, flat, egr lab, hallway, pointlio odom mostly stable

-bag10:

-bag11: rover, lidar on track belt, 15 deg, egr lab, static, pointlio odom stable

-bag12: rover, lidar on track belt, 15 deg, egr lab, static, pointlio odom stable

-bag13: rover, lidar in middle, 15 deg, egr lab, static, pointlio odom stable

-bag14: rover, lidar in middle, 15 deg, egr 113, move inside root teleop, pointlio laser_map messed up, odom is obvious wrong, 
	registered laser point should be stable: it is the raw pc after filtered, removed ceiling, floor points. new frame_id: after_map
	some floor points are sneaked in, these are the floor points at the direction of the lidar rear end. this make sense since lidar is proped up 15 deg, so only the points from behind get picked up. 
	113 is also quite clutted. maybe hall way will be better. esa to run test on hall way...
	to roughly see how the robot move when play bagfile, use base/base and view raw /unilidar/cloud. 
	idea: decerase lidar max range in point lio config? 
		more aggressively remove floor
		blink =1.0 sees right

-bag15: rover, lidar in middle, flat, egr lab, linear forward, backward, one slow rotation, pointlio odom stable

-bag16: rover, lidar in middle, flat, egr lab, two slow rotation, count-clockwise,  pointlio odom stable
	z: 0.07911653816699982
z: 0.0738808810710907
z: 0.0803276002407074
z: 0.0761452242732048

python3 plot_angvel.py
