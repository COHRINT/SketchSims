import rospy
from geometry_msgs.msg import PoseStamped
from harps_interface.msg import *
from std_msgs.msg import String, Int16
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped, Point

import sys
import numpy as np
from POMCPSolver import POMCP
from roadNode import RoadNode, readInNetwork, populatePoints, specifyPoint, dist
from treeNode import Node
import matplotlib.pyplot as plt 
from sketchGen import Sketch
from collections import deque
import math
#from shapely.geometry import Polygon, Point
import yaml
import os
from scipy.stats import expon


def computeTheta(a,b):
    #a is agent, b is goal
    vec = [b[0]-a[0],b[1]-a[1]]; 
    theta = np.arctan2(vec[1],vec[0])
    theta = np.degrees(theta); 
    return theta


class ROSPOM():

	def __init__(self, condition = "Both"):

		print("Initializing Planner"); 
		
		self.sendBelief = False; 
		self.showBelief = False; 

		self.goal_pub = rospy.Publisher("Drone1/Goal", path, queue_size=1)

		rospy.init_node('planner'); 
		
		#self.goal_pub.publish([50],[100],0);

		reached_sub = rospy.Subscriber("/GoalReached", Int16, self.action_callback); 
		self.reached_pub = rospy.Publisher("/GoalReached", Int16, queue_size=1)
		self.question_pub = rospy.Publisher("/Pull", pull,queue_size=1); 
		answer_sub = rospy.Subscriber("/PullAnswer",Int16, self.answer_callback); 
		sketch_sub = rospy.Subscriber('/Sketch', sketch, self.sketch_callback); 
		push_sub = rospy.Subscriber("/Push",push,self.push_callback)
		state_sub = rospy.Subscriber("/Drone1/pose", PoseStamped, self.state_callback)
		#self.belief_pub = rospy.Publisher("/image_raw", Image, queue_size=1)
		self.belief_pub = rospy.Publisher("/belief_map", GMPoints, queue_size=1)


		self.offset_x = 173.7
		self.offset_y = 845.6

		self.nextGoal = [0,-145]; 

		print("Building Road Network"); 
		network = readInNetwork('../yaml/flyovertonShift.yaml')

		if(condition == "Push"):
			self.solver = POMDP('graphSpec',False); 
		else:
			self.solver = POMCP('graphSpec',True)

		maxFlightTime = 600 #10 minutes
		human_sketch_chance = 1/90; #about once a minute
		pmean = 3; #poisson mean
		amult = 3; #area multiplier

		target, curs, goals = populatePoints(network, self.solver.sampleCount)
		pickInd = np.random.randint(0, len(target))
		trueNode = network[51]; 
		self.solver.buildActionSet(trueNode)

		self.trueS = [trueNode.loc[0], trueNode.loc[1], target[pickInd][0], target[pickInd][1], curs[pickInd], goals[pickInd], 0, trueNode];

		self.sSet = []
		for i in range(0, len(target)):
			self.sSet.append([self.trueS[0], self.trueS[1], target[i][0],target[i][1], curs[i], goals[i], 0, self.trueS[7]])

		self.endFlag = False; 
		self.totalTime = 0; 
		self.step = 0; 
		self.curDecTime = 5; 
		self.decCounts = 0; 

		self.lastAct = 0; 

		print("Starting Drone Movement")
		msg = Int16(); 
		msg.data = 1; 
		self.action_callback(msg); 






	def action_callback(self,msg):


		if(msg.data==1):
			
			rospy.sleep(3); 
			print("Publishing goal: [{},{}]".format(self.nextGoal[0],self.nextGoal[1])); 
			self.goal_pub.publish([int(self.nextGoal[0])],[int(self.nextGoal[1])],0);
			print("Goal Published"); 
			h = Node()
			act,info = self.solver.search(self.sSet, h, depth=self.solver.maxDepth, maxTime = min(self.curDecTime,self.solver.maxTime),inform=True)
			self.solver.buildActionSet(self.trueS[7]);

			if(self.solver.actionSet[act][1][0] is not None):
				self.lastAct = act; 
				self.question_pub.publish("Is the target {} of {}".format(self.solver.actionSet[act][1][1],self.solver.actionSet[act][1][0].name)); 
				

			self.curDecTime = dist(self.trueS,self.solver.actionSet[act][0].loc)/(self.solver.agentSpeed); 
			self.totalTime += self.curDecTime;


			self.step += 1; 

			for i in range(0,int(np.ceil(self.curDecTime))):
				self.sSet = self.solver.dynamicsUpdate(self.sSet,self.solver.actionSet[act]);

			try:
			
				self.sSet = self.solver.measurementUpdate_time(self.sSet,self.solver.actionSet[act],'Null Null'); 
				self.trueS[7] = self.solver.actionSet[act][0];
				self.trueS[0] = self.trueS[7].loc[0]; 
				self.trueS[1] = self.trueS[7].loc[1]; 

				self.nextGoal = [self.trueS[7].loc[0]-self.offset_x,1000-self.trueS[7].loc[1]-self.offset_y]; 
				print("Action Ready"); 
				print("");
			except Exception as e:
				print("Belief Update Issue Raised"); 
				pass; 


	def answer_callback(self,msg):
		print("Question Answered: {}".format(msg.data)); 

		obs = 'Null '; 
		if(msg.data == 1):
			obs += ' Yes'; 
		elif(msg.data == 0):
			obs += ' No'; 
		else:
			obs += ' Null'; 

		# plt.figure(); 
		# sSetNp = np.array(self.sSet); 
		# sSetOff = sSetNp[sSetNp[:,6] == 1]; 
		# sSetOn = sSetNp[sSetNp[:,6] == 0]; 
		# plt.scatter(sSetOn[:,2],sSetOn[:,3], color = 'magenta', alpha=0.1, edgecolor='none'); 
		# plt.scatter(sSetOff[:,2],sSetOff[:,3], color = 'red', alpha = 0.3, edgecolor='none'); 



		self.sSet = np.array(self.sSet);
		self.sSet = self.solver.measurementUpdate(self.sSet,self.solver.actionSet[self.lastAct],obs); 
		self.sSet = self.solver.measurementUpdate_time(self.sSet,self.solver.actionSet[self.lastAct],obs); 
		self.sSet = self.solver.resampleSet(self.sSet);

		if(self.sendBelief):
			bel_msg = GMPoints(); 
			for p in self.sSet:
				ps = Point(); 
				ps.x = p[2]; 
				ps.y = p[3]; 
				bel_msg.points.append(ps); 
			self.belief_pub.publish(bel_msg); 

		if(self.showBelief):
			plt.figure(); 
			sSetNp = np.array(self.sSet); 
			sSetOff = sSetNp[sSetNp[:,6] == 1]; 
			sSetOn = sSetNp[sSetNp[:,6] == 0]; 
			plt.scatter(sSetOn[:,2],sSetOn[:,3], color = 'green', alpha=0.1, edgecolor='none'); 
			plt.scatter(sSetOff[:,2],sSetOff[:,3], color = 'black', alpha = 0.3, edgecolor='none'); 
			plt.show();


	def sketch_callback(self,msg):
		print("Sketch Made: {}".format(msg.name)); 
		#print(msg); 
		params = {'centroid': [4, 5], 'dist_nom': 2, 'dist_noise': .25,
          'angle_noise': .2, 'pois_mean': 3, 'area_multiplier': 3, 'name': "Test", 'steepness': 7}

		points = []; 
		for p in msg.points:
			points.append([p.x,1000-p.y]); 
		points = np.array(points); 
		#calculate centroid
		cent_x = 0; 
		cent_y = 0; 
		for p in msg.points:
			cent_x += p.x/len(msg.points); 
			cent_y += p.y/len(msg.points); 

		params['centroid'] = [cent_x,1000-cent_y]; 
		params['points'] = points; 
		params['name'] = msg.name; 



		ske=Sketch(params); 
		self.solver.addSketch(self.trueS[7],ske);

	def push_callback(self,msg):
		print("Push Made"); 
		print(msg); 



		if(msg.parts[2] == "You"):
			return; 

		act = [self.solver.actionSet[self.lastAct][0], [None, None]]; 
		obs = 'Null Null'
		if(msg.parts[0] == 'Is'):
			obs = 'Null Yes'; 
		else:
			obs = 'Null No'; 
		act[1][1] = msg.parts[1].split()[0]; 

		for ske in self.solver.sketchSet:
			if(ske.name == msg.parts[2]):
				act[1][0] = ske; 
				break; 


		print(act,obs); 

		self.sSet = np.array(self.sSet);
		self.sSet = self.solver.measurementUpdate(self.sSet,act,obs); 
		self.sSet = self.solver.resampleSet(self.sSet);


		#Should beleifs be sent to interface? 
		if(self.sendBelief):
			bel_msg = GMPoints(); 
			for p in self.sSet:
				ps = Point(); 
				ps.x = p[2]; 
				ps.y = p[3]; 
				bel_msg.points.append(ps); 
			self.belief_pub.publish(bel_msg); 

		if(self.showBelief):
			plt.figure(); 
			sSetNp = np.array(self.sSet); 
			sSetOff = sSetNp[sSetNp[:,6] == 1]; 
			sSetOn = sSetNp[sSetNp[:,6] == 0]; 
			plt.scatter(sSetOn[:,2],sSetOn[:,3], color = 'green', alpha=0.1, edgecolor='none'); 
			plt.scatter(sSetOff[:,2],sSetOff[:,3], color = 'black', alpha = 0.3, edgecolor='none'); 
			plt.scatter(act[1][0].centroid[0],act[1][0].centroid[1],color='gold',marker='*',s=150); 
			plt.show();


	def state_callback(self,msg):
		#print("State Updated"); 
		#print(msg); 
		pass; 





	


if __name__ == '__main__':

	#Conditions: Pull, Push, Both
	condition = "Pull"; 
	planner = ROSPOM(condition); 

	while not rospy.is_shutdown():
		rospy.spin()
