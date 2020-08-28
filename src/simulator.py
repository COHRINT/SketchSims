import sys
import numpy as np
from POMCPSolver import POMCP
from roadNode import RoadNode, readInNetwork, populatePoints, specifyPoint, dist
from treeNode import Node
import matplotlib.pyplot as plt 
from sketchGen import Sketch
from collections import deque
import math
from shapely.geometry import Polygon, Point
import yaml
import os
from scipy.stats import expon

def computeTheta(a,b):
    #a is agent, b is goal
    vec = [b[0]-a[0],b[1]-a[1]]; 
    theta = np.arctan2(vec[1],vec[0])
    theta = np.degrees(theta); 
    return theta
 

def simulate(verbosity = 0):

    # Initialize network
    # ------------------------------------------------------
    network = readInNetwork('../yaml/flyovertonShift.yaml')
    h = Node()
    solver = POMCP('graphSpec')

    maxFlightTime = 600 #10 minutes
    human_sketch_chance = 1/60; #about once a minute
    pmean = 3; #poisson mean
    amult = 10; #area multiplier
    #human_sketch_chance = 0; 

    # Initialize belief and state
    # ------------------------------------------------------
    target, curs, goals = populatePoints(network, solver.sampleCount)
    pickInd = np.random.randint(0, len(target))
    trueNode = np.random.choice(network); 
    solver.buildActionSet(trueNode)

    trueS = [trueNode.loc[0], trueNode.loc[1], target[pickInd][0], target[pickInd][1], curs[pickInd], goals[pickInd], 0, trueNode];

    sSet = []
    for i in range(0, len(target)):
        sSet.append([trueS[0], trueS[1], target[i][0],target[i][1], curs[i], goals[i], 0, trueS[7]])

    fig,ax = plt.subplots();



    # DEBUG: Add initial sketch
    # ------------------------------------------------------
    # params = {'centroid': [500, 500], 'dist_nom': 50,'angle_noise': .3,'dist_noise': .25, 'pois_mean': 4, 'area_multiplier': 5, 'name': "Test", 'steepness': 20}
    # ske = Sketch(params)
    # solver.addSketch(trueS[7],ske);


    # Set up sketches
    # ------------------------------------------------------
    with open("../yaml/landmarks.yaml", 'r') as stream:
        fi = yaml.safe_load(stream)

    params = {'centroid': [4, 5], 'dist_nom': 2, 'dist_noise': .25,
              'angle_noise': .2, 'pois_mean': pmean, 'area_multiplier': amult, 'name': "Test", 'steepness': 7}
    allSketches = []
    #seedCount = 0
    for k, v in fi['Landmarks'].items():
    #for k in fi.keys:
        v = fi['Landmarks'][k]
        params['name'] = k
        params['dist_nom'] = v['radius']
        params['centroid'] = v['loc']
        params['dist_noise'] = v['radius']/4
        allSketches.append(Sketch(params))
        #seedCount += 1
    np.random.shuffle(allSketches); 
    sketchQueue = deque(allSketches)

    sketchTimes = []; 
    expCount = 0; 
    for i in range(0,len(sketchQueue)):
        expCount += expon.rvs(scale=1/human_sketch_chance)
        sketchTimes.append(expCount);  

    # print(sketchTimes); 
    # sketchTimes.pop(0); 
    # print(sketchTimes);  


    # Set up data collection
    # ----------------------------------------------------------
    # Note: Beliefs should only be s[2:4] 
    # to capture target state beliefs and s[6] to capture mode 
    data = {'States':[],'Actions':[],'Human_Obs':[],'Drone_Obs':[],'Beliefs':[],'ModeBels':[],'TotalTime':0,'DecisionTimes':[],'GivenTimes':[],'Sketches':[]};
    data['maxDepth'] = solver.maxDepth; 
    data['c'] = solver.c; 
    data['maxTreeQueries'] = solver.maxTreeQueries; 
    data['maxTime'] = solver.maxTime; 
    data['gamma'] = solver.gamma; 
    data['agentSpeed'] = solver.agentSpeed; 
    data['sampleCount'] = solver.sampleCount; 
    data['human_class_thresh'] = solver.human_class_thresh
    data['human_accuracy'] = solver.human_accuracy; 
    data['capture_length'] = solver.capture_length
    data['detect_length'] = solver.detect_length; 
    data['drone_falseNeg'] = solver.drone_falseNeg; 
    data['drone_falsePos'] = solver.drone_falsePos; 
    data['targetSpeed'] = solver.targetSpeed; 
    data['targetDev'] = solver.targetDev; 
    data['offRoadSpeed'] = solver.offRoadSpeed; 
    data['offRoadDev']= solver.offRoadDev; 
    data['leaveRoadChance'] = solver.leaveRoadChance; 
    data['human_availability'] = solver.human_availability
    data['maxFlightTime'] = maxFlightTime; 
    data['human_sketch_chance'] = human_sketch_chance; 
    data['assumed_availability'] = solver.assumed_availability
    data['assumed_accuracy'] = solver.assumed_accuracy;
    data['Captured'] = False; 
    data['pois_mean'] = pmean; 
    data['area_multiplier'] = amult; 
    #print(data['maxTime']); 


    endFlag = False; 
    totalTime = 0; 
    step = 0; 
    curDecTime = 5; 
    decCounts = 0; 
    # Simulate until captured or out of time
    # ------------------------------------------------------
    #for step in range(0, maxSteps):
    newSet = sSet; 
    while(totalTime < maxFlightTime):
        data['States'].append(trueS); 
        bel = np.array(sSet)[:,2:4]; 
        modebel = np.array(sSet)[:,7]; 

        data['Beliefs'].append(bel); 
        data['ModeBels'].append(modebel)

        # POMCP makes decision
        decisionFlag = False; 
        # -----------------------------------------------------

        if(trueS[0] == trueS[7].loc[0] and trueS[1] == trueS[7].loc[1]):
            if(verbosity > 0):
                print("Starting step: {} with Decision Time: {:0.2f}s at Total Time: {:0.2f}s".format(step+1, min(solver.maxTime,curDecTime),totalTime))
            decCounts = 0; 
            decisionFlag = True;
            #act,info = solver.search(sSet, h, depth=min(solver.maxDepth, maxSteps-step+1), maxTime = min(curDecTime,solver.maxTime),inform=True)
            act,info = solver.search(newSet, h, depth=solver.maxDepth, maxTime = min(curDecTime,solver.maxTime),inform=True)
            newSet = sSet; 

            solver.buildActionSet(trueS[7]);
            if(verbosity > 1):
                print("Action: {}".format(solver.actionSet[act]));

            try:
                data['Actions'].append(solver.actionSet[act]);
            except Exception:
                #print("FAILURE")
                #print(len(solver.actionSet),act);
                #raise; 
                act = 0; 


            #Disable To Blind Plan
            ########################################################
            if(solver.actionSet[act][1][0] is not None):
                o = solver.generate_o(trueS,solver.actionSet[act]);
                if(verbosity > 1):
                    [o1,o2] = o.split(); 
                    print("Human observation: {}".format(o2)); 
                [o1,o2] = o.split(); 
                data['Human_Obs'].append(o2); 
                newSet = np.array(newSet);
                newSet = solver.measurementUpdate(newSet,solver.actionSet[act],o); 
                newSet = solver.measurementUpdate_time(newSet,solver.actionSet[act],o); 
                newSet = solver.resampleSet(newSet); 
                sSet = newSet; 



             

            curDecTime = dist(trueS,solver.actionSet[act][0].loc)/solver.agentSpeed; 
            totalTime += curDecTime; 

            data['GivenTimes'].append(min(curDecTime,solver.maxTime)); 
            data['DecisionTimes'].append(totalTime); 
            step += 1; 
            for i in range(0,int(np.ceil(curDecTime))):
                newSet = solver.dynamicsUpdate(newSet,solver.actionSet[act]);

        decCounts += 1; 
        if(decCounts + totalTime > maxFlightTime):
            totalTime += decCounts; 
            endFlag = True
        fakeAct = [solver.actionSet[act][0],[None,None]]; 

        #if(verbosity > 1):
            #print("Action: {}".format(solver.actionSet[act])); 

        # propagate state
        # ------------------------------------------------------
        #solver.buildActionSet(trueS[7]); 
        trueS = solver.generate_s(trueS,solver.actionSet[act]);
        r = solver.generate_r(trueS,solver.actionSet[act]);

        sSet = solver.dynamicsUpdate(sSet,solver.actionSet[act]);
        #o = solver.generate_o(trueS,solver.actionSet[act]); 
        o = solver.generate_o(trueS,fakeAct); 
        #o = solver.generate_o(trueS,[solver.actionSet[act][0],[solver.actionSet[act][1][0],None]]); 
        #o = "Null No"
        [o1,o2] = o.split();
        data['Drone_Obs'].append(o1);  
        o = o1 + " Null"; 
        if("Captured" in o):
            endFlag = True; 
            data['Captured'] = True; 

        if(verbosity > 1):
            print("Drone Observation: {}".format(o1)); 



        # if question was asked, see if human answered
        # ------------------------------------------------------
        sSet = solver.measurementUpdate(sSet,fakeAct,o); 
        sSet = solver.resampleSet(sSet); 

        if(decisionFlag):
            tmpHAct = h.getChildByID(act); 
            tmpHObs = tmpHAct.getChildByID(o); 

            if(tmpHObs != -1 and len(tmpHObs.data) > 0):
                h = tmpHObs; 
                #sSet = solver.resampleNode(h); 
            else:
                h = tmpHAct[0]; 



     

        if(verbosity == 2):
            ax.clear(); 
            sSetNp = np.array(sSet); 
            sSetOff = sSetNp[sSetNp[:,6] == 1]; 
            sSetOn = sSetNp[sSetNp[:,6] == 0]; 
            ax.scatter(sSetOn[:,2],sSetOn[:,3], color = 'magenta', alpha=0.1, edgecolor='none'); 
            ax.scatter(sSetOff[:,2],sSetOff[:,3], color = 'red', alpha = 0.3, edgecolor='none'); 
            ax.scatter(trueS[0],trueS[1], color = 'blue', alpha = 1, s=100)
            ax.scatter(trueS[2],trueS[3], color = 'black', alpha = 1, s=100)


            # if(solver.actionSet[act][0] is not None):
            #     #theta_options = [180,0,90,270,135,45,315,225]
            #     theta = theta_options[solver.actionSet[act][0]]; 
            # else:
            #     theta = 90;
            #theta = np.arctan2(trueS[7].loc[1],trueS[7].loc[0])-np.arctan2(trueS[1],trueS[0])
            # theta = np.arctan2(trueS[7].loc[1],trueS[7].loc[0])-np.arctan2(trueS[1],trueS[0])
            # theta = np.degrees(theta); 
            theta = computeTheta([trueS[0],trueS[1]],trueS[7].loc); 
            #print(theta)

            detect_length = solver.detect_length;
            detect_points = [[trueS[0], trueS[1]], [trueS[0]+detect_length*math.cos(2*-0.261799+math.radians(theta)), trueS[1]+detect_length*math.sin(2*-0.261799+math.radians(
                theta))], [trueS[0]+detect_length*math.cos(2*0.261799+math.radians(theta)), trueS[1]+detect_length*math.sin(2*0.261799+math.radians(theta))]]
            detect_poly = Polygon(detect_points); 
            x,y = detect_poly.exterior.xy
            ax.plot(x,y,color='blue');

            capture_length = solver.capture_length
            capture_points = [[trueS[0], trueS[1]], [trueS[0]+capture_length*math.cos(2*-0.261799+math.radians(theta)), trueS[1]+capture_length*math.sin(2*-0.261799+math.radians(
                theta))], [trueS[0]+capture_length*math.cos(2*0.261799+math.radians(theta)), trueS[1]+capture_length*math.sin(2*0.261799+math.radians(theta))]]
            capture_poly = Polygon(capture_points); 

            x,y = capture_poly.exterior.xy
            ax.plot(x,y,color='gold');

            #plt.axis('equal')
            ax.set_xlim([0,1000]); 
            ax.set_ylim([0,1000]); 

            plt.pause(0.1); 


        # check if human volunteered anything
        # ------------------------------------------------------
        # checkVolunteer()

        # check if human sketched anything
        # ------------------------------------------------------
        if(decisionFlag):
            # coin = np.random.random(); 
            # cTest = expon.cdf(min(curDecTime,solver.maxTime), scale=1/human_sketch_chance)
            # #print(coin,cTest); 
            if(len(sketchTimes) > 0 and totalTime > sketchTimes[0]):
                sketchTimes.pop(0); 
                #print("Sketch Made: {}".format(ske.name)); 
                ske = sketchQueue.pop(); 
                solver.addSketch(trueS[7],ske);
                if(verbosity > 1):
                    print("Sketch Made: {}".format(ske.name)); 
                data['Sketches'].append(ske); 


        # save everything
        # ------------------------------------------------------
        


        # repeat
        # ------------------------------------------------------
        h = Node(); 
        
        # repeat
        if(verbosity > 1):
            print(""); 
        if(endFlag):
            break; 

    data['TotalTime'] = totalTime;

    return data; 

def runSims(numRuns,tag):

    #Dictionary with sims and meta data
    #Sims is list of dictionaries, 1 per run

    if(not os.path.exists('../data/{}'.format(tag))):
        print("Creating Data Directory: /data/{}".format(tag)); 
        os.mkdir('../data/{}'.format(tag)); 

    print("Beginning Data Collection: {}".format(tag)); 


    #for i in range(0,numRuns):
    run = 0; 
    allCatchTimes = []; 
    while(run < numRuns):
        print('Simulation: {} of {}'.format(run+1,numRuns)); 
        breakFlag = False; 
        try:
            dataRun = simulate(verbosity=2); 
        except Exception:
            continue;
        #dataRun = simulate(verbosity=0); 

        
        #dataPackage['sims'].append(dataRun);
        dataPackage = dataRun
        dataPackage['numRuns'] = numRuns;
        dataPackage['tag'] = tag; 
        if(dataPackage['Captured']):
            print("Time to Capture: {}s".format(dataPackage['TotalTime']))
            allCatchTimes.append(dataPackage['TotalTime']);
        else:
            print("Agent failed after {}s".format(dataPackage['TotalTime'])); 

        print("Ratio of Captures: {}".format(len(allCatchTimes)/(run+1))); 
        print("Average Capture Time: {}".format(np.mean(allCatchTimes))); 
        print(""); 

        np.save('../data/{}/{}_{}'.format(tag,tag,run),dataPackage); 

        run += 1; 
    print("Simulation Set Complete, Data Saved"); 

if __name__ == '__main__':


    #simulate(verbosity=2)
    ar = sys.argv; 
    if(len(ar)>1):
        runSims(int(ar[1]),ar[2]); 
    else:
        runSims(2,'Test'); 


