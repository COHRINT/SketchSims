import importlib
from treeNode import Node
from roadNode import RoadNode, readInNetwork, populatePoints, specifyPoint, dist
import sys
import numpy as np
import time
from sketchGen import Sketch
import matplotlib.pyplot as plt
from copy import deepcopy
import math
from shapely.geometry import Polygon, Point
sys.path.append("../specs")


class POMCP:

    def __init__(self, specFile, pullAllowed=True):
        mod = importlib.import_module(specFile)
        self.generate_s = mod.generate_s
        self.generate_o = mod.generate_o
        self.generate_r = mod.generate_r

        self.generate_s_time = mod.generate_s_time
        self.generate_o_time = mod.generate_o_time
        self.generate_r_time = mod.generate_r_time

        self.rollout = mod.rollout
        self.estimate_value = mod.estimate_value
        self.isTerminal = mod.isTerminal
        self.maxTreeQueries = mod.maxTreeQueries
        self.sampleCount = mod.sampleCount
        self.problemName = mod.problemName
        self.c = mod.c
        self.gamma = mod.gamma
        self.maxTime = mod.maxTime
        self.agentSpeed = mod.agentSpeed
        self.agentDev = mod.agentDev
        self.sketchSet = []; 
        self.drone_falseNeg = mod.drone_falseNeg
        self.drone_falsePos = mod.drone_falsePos
        self.human_class_thresh = mod.human_class_thresh;
        self.maxDepth = mod.maxDepth 
        self.human_availability = mod.human_availability
        self.human_accuracy = mod.human_accuracy; 
        self.capture_length = mod.capture_length; 
        self.detect_length = mod.detect_length; 
        self.targetSpeed = mod.targetSpeed
        self.targetDev = mod.targetDev
        self.offRoadSpeed = mod.offRoadSpeed
        self.offRoadDev = mod.offRoadDev
        self.leaveRoadChance = mod.leaveRoadChance
        self.assumed_accuracy = mod.assumed_accuracy
        self.assumed_availability = mod.assumed_availability

        self.pullAllowed = pullAllowed;  

        #self.buildActionSet(); 


    def getActionSet(self,s):
        actionSet = []; 

        nodeSet = []; 

        #If you start running into mountains
        forbidden = [39,40,41,42,47,46,44];
         # forbidden = []; 

        for n in s.neighbors:
            if(n not in nodeSet):
                nodeSet.append(n); 
            for n2 in n.neighbors:
                if(n2 not in nodeSet and n2 is not s):
                    if(s.loc[0] == n.loc[0] and n.loc[0] == n2.loc[0]):
                        continue; 
                    elif(s.loc[1] == n.loc[1] and n.loc[1] == n2.loc[1]):
                        continue; 
                    elif(n2.ident in forbidden):
                        continue; 
                    nodeSet.append(n2);


        # For conjoined action spaces
        # ------------------------------------------------------
        for i in range(0,len(nodeSet)):
            actionSet.append([nodeSet[i],[None,None]]); 
            if(self.pullAllowed):
                for ske in self.sketchSet:
                    #inside
                    actionSet.append([nodeSet[i],[ske,'Inside']])
                    #near
                    actionSet.append([nodeSet[i],[ske,'Near']])
                    for lab in ske.labels:
                        actionSet.append([nodeSet[i],[ske,lab]]); 
                        #actionSet.append([nodeSet[i],[ske,"Near " + lab]]); 

        return actionSet; 


    def buildActionSet(self,s):
        self.actionSet = []; 

        nodeSet = []; 

        #If you start running into mountains
        forbidden = [39,40,41,42,47,46,44]; 
        # forbidden = []; 

        for n in s.neighbors:
            if(n not in nodeSet):
                nodeSet.append(n); 
            for n2 in n.neighbors:
                if(n2 not in nodeSet and n2 is not s):
                    if(s.loc[0] == n.loc[0] and n.loc[0] == n2.loc[0]):
                        continue; 
                    elif(s.loc[1] == n.loc[1] and n.loc[1] == n2.loc[1]):
                        continue; 
                    elif(n2.ident in forbidden):
                        continue; 
                    nodeSet.append(n2);




        # For conjoined action spaces
        # ------------------------------------------------------
        for i in range(0,len(nodeSet)):
            self.actionSet.append([nodeSet[i],[None,None]]); 
            if(self.pullAllowed):
                for ske in self.sketchSet:
                    #inside
                    self.actionSet.append([nodeSet[i],[ske,'Inside']])
                    #near
                    self.actionSet.append([nodeSet[i],[ske,'Near']])
                    for lab in ske.labels:
                        self.actionSet.append([nodeSet[i],[ske,lab]]); 
                        #self.actionSet.append([nodeSet[i],[ske,"Near " + lab]]); 

        # For separated action spaces
        # ------------------------------------------------------
        # for i in range(0,4):
        #     self.actionSet.append([i,[None,None]]); 

        # for ske in self.sketchSet:
        #     #inside
        #     self.actionSet.append([None,[ske,'Inside']])
        #     #near
        #     self.actionSet.append([None,[ske,'Near']])
        #     for lab in ske.labels:
        #         self.actionSet.append([None,[ske,lab]]); 
        #         self.actionSet.append([None,[ske,"Near " + lab]]); 



    def addSketch(self,s,ske):
        #print("Sketch Added");
        self.sketchSet.append(ske); 
        self.buildActionSet(s); 


    def simulate(self, s, h, depth):

        # check if node is in tree
        # if not, add nodes for each action
        if(depth <= 0):
            return 0

        h.data.append(s)
        actionSet = self.getActionSet(s[7]); 
        #print(h.getChildrenIDs()); 
        if(not h.hasChildren()):
            #for a in range(0,len(self.actionSet)):
                # self.addActionNode(h,a);
            #actionSet = self.getActionSet(s[7])
            for a in range(0,len(actionSet)):
                h.addChildID(a)
        #print(actionSet);

        # find best action acccording to c
        act = np.argmax([ha.Q + self.c*np.sqrt(np.log(h.N)/ha.N) for ha in h])

        # generate s,o,r
        # sprime = self.generate_s(s,actionSet[act])
        # o = self.generate_o(sprime, actionSet[act])
        # r = self.generate_r(s, actionSet[act])
        sprime = self.generate_s_time(s,actionSet[act],dist(s,actionSet[act][0].loc)/self.agentSpeed)
        o = self.generate_o_time(sprime, actionSet[act])
        r = self.generate_r_time(s, actionSet[act])

        # if o not in ha.children
        # add it and estimate value
        # else recurse
        if(o not in h[act].getChildrenIDs()):
            h[act].addChildID(o)
            return self.estimate_value(s, h[act])
            #return self.rollout(s,depth);

        if(self.isTerminal(s, actionSet[act])):
            return r

        q = r + self.gamma * \
            self.simulate(sprime, h[act].getChildByID(o), depth-1)

        # update node values
        h.N += 1
        h[act].N += 1
        h[act].Q += (q-h[act].Q)/h[act].N

        return q

    def resampleSet(self, sSet):

        if(len(sSet) >= self.sampleCount):
            return sSet

        while(len(sSet) < self.sampleCount):
            ind = np.random.randint(0, len(sSet))
            tmp = deepcopy(sSet[ind])
            #tmp[2] += np.random.normal(0,.005);
            #tmp[3] += np.random.normal(0,.005);
            tmp[2] += (tmp[5].loc[0]-tmp[4].loc[0]) * \
                np.random.random()*.25  # + np.random.normal(0,dev);
            tmp[3] += (tmp[5].loc[1]-tmp[4].loc[1])*np.random.random()*.25

            sSet.append(tmp)
        return sSet

    def search(self, b, h, depth, maxTime, inform=False):
        # Note: You can do more proper analytical updates if you sample during runtime
        # but it's much faster if you pay the sampling price beforehand.
        # TLDR: You need to change this before actually using
        #print("Check your sampling before using this in production")

        #sSet = b.sample(maxTreeQueries);
        sSet = b
        count = 0

        startTime = time.clock()

        while(time.clock()-startTime < maxTime and count < min(self.maxTreeQueries,len(sSet))): 
            s = sSet[count]
            count += 1
            self.simulate(s, h, depth)
        if(inform):
            info = {"Execution Time": 0, "Tree Queries": 0, "Tree Size": 0}
            info['Execution Time'] = time.clock()-startTime
            info['Tree Queries'] = count
            #info['Tree Size'] = len(h.traverse());
            #print([a.Q for a in h])
            return np.argmax([a.Q for a in h]), info
            #print([a.Q for a in h])
        else:
            return np.argmax([a.Q for a in h])

    def dynamicsUpdate(self, sSet, act):

        sSetPrime = []

        for s in sSet:
            sSetPrime.append(self.generate_s(s, act))

        s = np.array(sSetPrime)

        return s

    def measurementUpdate_time(self,sSet,act,o):

        weights = np.zeros(shape=(len(sSet))); 
        [drone_o,human_o] = o.split();



        for i in range(0,len(sSet)):
            s = sSet[i]; 
            theta = computeTheta([s[0],s[1]],act[0].loc);
            #make a rectangle representing the total distance swept
            capture_points = []; 
            capture_length = self.capture_length; 
            capture_points.append([s[0]+capture_length*np.cos(theta-90)/2, s[1]+capture_length*np.sin(theta-90)/2]); 
            capture_points.append([s[0]+capture_length*np.cos(theta+90)/2, s[1]+capture_length*np.sin(theta+90)/2]);
            capture_points.append([act[0].loc[0]+capture_length*np.cos(theta-90)/2, act[0].loc[1]+capture_length*np.sin(theta-90)/2])
            capture_points.append([act[0].loc[0]+capture_length*np.cos(theta+90)/2, act[0].loc[1]+capture_length*np.sin(theta+90)/2])

            detect_points = []; 
            detect_length = self.detect_length; 
            detect_points.append([s[0]+detect_length*np.cos(theta-90)/2, s[1]+detect_length*np.sin(theta-90)/2]); 
            detect_points.append([s[0]+detect_length*np.cos(theta+90)/2, s[1]+detect_length*np.sin(theta+90)/2]);
            detect_points.append([act[0].loc[0]+detect_length*np.cos(theta-90)/2, act[0].loc[1]+detect_length*np.sin(theta-90)/2])
            detect_points.append([act[0].loc[0]+detect_length*np.cos(theta+90)/2, act[0].loc[1]+detect_length*np.sin(theta+90)/2])
            #print(detect_points); 
            detect_poly  = Polygon(detect_points); 


            capture_poly = Polygon(capture_points);
            target = Point(s[2],s[3]); 

            if(detect_poly.contains(target) and drone_o == 'Detect'):
                weights[i] = .97; 
            elif(drone_o == 'Detect'):
                weights[i] = 0.03

            if(capture_poly.contains(target) and drone_o == 'Captured'):
                    weights[i] = .99; 
            elif(drone_o == 'Captured'):
                weights[i] = 0.01; 

            if(weights[i] == 0 and drone_o == 'Null'):
                weights[i] = .95; 
            else:
                weights[i] = 0.05; 

        weights /= np.sum(weights)

        csum = np.cumsum(weights)
        csum[-1] = 1

        indexes = np.searchsorted(csum, np.random.random(len(sSet)))
        sSet[:] = sSet[indexes]

        # print(s)

        return sSet




    def measurementUpdate(self, sSet, act, o):

        #sm = Softmax();
        # sm.buildOrientedRecModel([sSetPrime[0][0],sSetPrime[0][1]],0,1,1,steepness=7);

        #measurements = ['Near','West','South','North','East']
        #weights = [sm.pointEvalND(measurements.index(o),[s[i][2],s[i][3]]) for i in range(0,len(s))];
        human_weights = np.ones(shape=(len(sSet))); 
        drone_weights = np.ones(shape=(len(sSet))); 
        weights = np.zeros(shape=(len(sSet))); 


        # upWeight = .99
        # downWeight = .01
        # for i in range(0, len(s)):
        #     if(distance([s[i][0], s[i][1]], [s[i][2], s[i][3]]) < 1):
        #         if(o == 'Near'):
        #             weights[i] = upWeight
        #         else:
        #             weights[i] = downWeight
        #     elif(distance([s[i][0], s[i][1]], [s[i][2], s[i][3]]) >= 1):
        #         if(o == 'Far'):
        #             weights[i] = upWeight
        #         else:
        #             weights[i] = downWeight
        #print("Fix the near weighting")
        #acc = 0.97;
        acc = self.human_accuracy 
        [drone_o,human_o] = o.split(); 
        if(act[1][0] is not None and human_o is not 'Null'):
            ske = act[1][0]; 
            label = act[1][1]; 
            for i in range(0,len(sSet)):
                s = sSet[i]; 
                point = s[2:4]; 
                probs = ske.giveProbabilities(point); 
                maxi = max(probs.values()); 
                for k in probs.keys():
                    probs[k] /= maxi; 
                if(label == "Near"):
                    nearProb = ske.giveNearProb(point); 
                    #nearProb /= max(nearProb); 
                    if(np.argmax(nearProb) == 0):
                        human_weights[i] = acc;
                    else:
                        human_weights[i] = 1-acc;
                    #print(nearProb[0])
                elif("Near" in label):
                    spl = label.split(); 
                    nearProb = ske.giveNearProb(point); 
                    #human_weights[i] = probs[spl[1]]*nearProb[0]; 
                    if(probs[spl[1]] > self.human_class_thresh):
                        human_weights[i] = acc; 
                    else:
                        human_weights[i] = (1-acc);
                    if(np.argmax(nearProb) == 0):
                        human_weights[i] *= acc; 
                    else:
                        human_weights[i] *= (1-acc);  
                else:
                    if(probs[label] > self.human_class_thresh):
                        human_weights[i] = acc;
                        #human_weights[i] = .95;
                    else:
                        human_weights[i] = 1-acc;
                        #human_weights[i] = .05; 
                    #human_weights[i] = probs[label]; 
                if(human_o == 'No'):
                    human_weights[i] = 1-human_weights[i]; 


                    

        for i in range(0,len(sSet)):
            s = sSet[i]; 
            #theta = np.arctan2(act[0].loc[1],act[0].loc[0])-np.arctan2(s[1],s[0])
            theta = computeTheta([s[0],s[1]],act[0].loc); 
            detect_length = self.detect_length
            detect_points = [[s[0], s[1]], [s[0]+detect_length*math.cos(2*-0.261799+math.radians(theta)), s[1]+detect_length*math.sin(2*-0.261799+math.radians(
                theta))], [s[0]+detect_length*math.cos(2*0.261799+math.radians(theta)), s[1]+detect_length*math.sin(2*0.261799+math.radians(theta))]]
            detect_poly = Polygon(detect_points); 


            capture_length = self.capture_length
            capture_points = [[s[0], s[1]], [s[0]+capture_length*math.cos(2*-0.261799+math.radians(theta)), s[1]+capture_length*math.sin(2*-0.261799+math.radians(
                theta))], [s[0]+capture_length*math.cos(2*0.261799+math.radians(theta)), s[1]+capture_length*math.sin(2*0.261799+math.radians(theta))]]
            capture_poly = Polygon(capture_points); 

            target = Point(s[2],s[3]); 

            if(detect_poly.contains(target)):
                #drone_response = "Detect"
                if(capture_poly.contains(target)):
                    #drone_response = "Captured"
                    if(drone_o == 'Captured'):
                        drone_weights[i] = 1-self.drone_falsePos; 
                    else:
                        drone_weights[i] = self.drone_falsePos; 
                else:
                    if(drone_o == 'Detect'):
                        drone_weights[i] = 1-self.drone_falsePos; 
                    else:
                        drone_weights[i] = self.drone_falsePos; 
            else:
                if(drone_o == 'Null'):
                    drone_weights[i] = 1-self.drone_falseNeg; 
                else:
                    drone_weights[i] = self.drone_falseNeg; 


        if(human_o == "Null" or human_o == None):
            weights = drone_weights; 
        else:
            weights = np.multiply(human_weights,drone_weights); 
        #weights = human_weights
        #weights = drone_weights

        weights /= np.sum(weights)

        csum = np.cumsum(weights)
        csum[-1] = 1

        indexes = np.searchsorted(csum, np.random.random(len(sSet)))
        sSet[:] = sSet[indexes]

        # print(s)

        return sSet

def computeTheta(a,b):
    #a is agent, b is goal
    vec = [b[0]-a[0],b[1]-a[1]]; 
    theta = np.arctan2(vec[1],vec[0])
    theta = np.degrees(theta); 
    return theta


def testPOMCP():
    h = Node()
    solver = POMCP('graphSpec')

    params = {'centroid': [500, 500], 'dist_nom': 50, 'dist_noise': .25,
      'angle_noise': .3, 'pois_mean': 4, 'area_multiplier': 5, 'name': "Test", 'steepness': 20}
    ske = Sketch(params)
    #solver.addSketch(ske);


    network = readInNetwork('../yaml/flyovertonShift.yaml')
    maxSteps = 300

    # Initialize belief and state
    # ------------------------------------------------------
    target, curs, goals = populatePoints(network, solver.sampleCount)
    pickInd = np.random.randint(0, len(target))
    # trueS = [np.random.random()*1000, np.random.random()*1000, target[pickInd]
    #          [0], target[pickInd][1], curs[pickInd], goals[pickInd], 0]
    trueS = [500, 500, target[pickInd][0], target[pickInd][1], curs[pickInd], goals[pickInd], 0];
    print(trueS[2:4]); 



    sSet = []
    for i in range(0, len(target)):
        sSet.append([trueS[0], trueS[1], target[i][0],target[i][1], curs[i], goals[i], 0])
        #sSet.append(deepcopy(trueS))
        #sSet.append([trueS[0],trueS[1],trueS[2],trueS[3],trueS[4],trueS[5],trueS[6]])

    sArray = np.array(sSet); 
    plt.scatter(sArray[:,2],sArray[:,3],color='red',alpha=1, s=100);

    act,info = solver.search(sSet, h, depth=solver.maxDepth, inform=True)

    print(info)


    print(solver.actionSet[act]);
    plt.scatter(trueS[0],trueS[1],color='blue'); 
    plt.scatter(trueS[2],trueS[3],color='red'); 
    sArray = np.array(sSet); 
    plt.scatter(sArray[:,2],sArray[:,3],color='blue',alpha=1);

    actMap = ["West","East",'North','South']; 
    plt.xlim([0,1000]); 
    plt.ylim([0,1000]); 
    plt.title(actMap[solver.actionSet[act][0]])
    plt.show();


def testBeliefUpdate():
    h = Node()
    solver = POMCP('graphSpec')

    params = {'centroid': [500, 500], 'dist_nom': 50, 'dist_noise': .25,
      'angle_noise': .3, 'pois_mean': 4, 'area_multiplier': 5, 'name': "Test", 'steepness': 20}
    #ske = Sketch(params, seed=0)
    #np.random.seed(2);

    #solver.addSketch(ske);


    network = readInNetwork('../yaml/flyovertonShift.yaml')
    maxSteps = 300

    # Initialize belief and state
    # ------------------------------------------------------
    target, curs, goals = populatePoints(network, solver.sampleCount)
    pickInd = np.random.randint(0, len(target))
    # trueS = [np.random.random()*1000, np.random.random()*1000, target[pickInd]
    #          [0], target[pickInd][1], curs[pickInd], goals[pickInd], 0]
    #trueS = [35, 815, target[pickInd][0], target[pickInd][1], curs[pickInd], goals[pickInd], 0];
    
    trueNode = np.random.choice(network); 
    #trueNode = network[29]; 
    solver.buildActionSet(trueNode)

    trueS = [trueNode.loc[0], trueNode.loc[1], target[pickInd][0], target[pickInd][1], curs[pickInd], goals[pickInd], 0, trueNode];
    print(trueS[2:4]); 



    sSet = []
    for i in range(0, len(target)):
        sSet.append([trueS[0], trueS[1], target[i][0],target[i][1], curs[i], goals[i], 0, trueS[7]])


    #act,info = solver.search(sSet, h, depth=solver.maxDepth, inform=True)

    #print(info)
    act = 2
    #act = 12
    print(solver.actionSet[act])

    sSet = solver.dynamicsUpdate(sSet,solver.actionSet[act]); 
    print(trueS[0:2]); 
    trueS = solver.generate_s(trueS,solver.actionSet[act]); 
    print(trueS[0:2]); 
    print(solver.actionSet[act][0].loc); 
    o = solver.generate_o(trueS,solver.actionSet[act]);
    print(o); 
    #o = 'Captured No'
    if((solver.actionSet[act][1][0] is not None) and (o is not 'Null Null')):
        sSet = solver.measurementUpdate(sSet,solver.actionSet[act],o); 
        sSet = solver.resampleSet(sSet); 
        # sSet = solver.measurementUpdate(sSet,solver.actionSet[act],o); 
        # sSet = solver.resampleSet(sSet);


    #print(solver.actionSet[act]);
    plt.scatter(trueS[0],trueS[1],color='blue'); 
    
    sArray = np.array(sSet); 
    plt.scatter(sArray[:,2],sArray[:,3],color='red',alpha=0.05);
    plt.scatter(trueS[2],trueS[3],color='black'); 

    actMap = ["West","East",'North','South']; 
    plt.xlim([0,1000]); 
    plt.ylim([0,1000]); 
    #plt.title(actMap[solver.actionSet[act][0]])
    plt.show();

if __name__ == '__main__':

    #print("When last you were here: You were investigating reward functions and estimation of value"); 
    #print("But you really should build the measurement update..."); 

    #testPOMCP(); 
    testBeliefUpdate(); 
