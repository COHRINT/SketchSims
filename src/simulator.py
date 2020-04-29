import sys
import numpy as np
from POMCPSolver import POMCP
from roadNode import RoadNode, readInNetwork, populatePoints, specifyPoint
from treeNode import Node
import matplotlib.pyplot as plt 
from sketchGen import Sketch
import math
from shapely.geometry import Polygon, Point

def simulate(verbosity = 0):

    # Initialize network
    # ------------------------------------------------------
    network = readInNetwork('../yaml/flyovertonShift.yaml')
    h = Node()
    solver = POMCP('gridSpec')
    maxSteps = 300

    # Initialize belief and state
    # ------------------------------------------------------
    target, curs, goals = populatePoints(network, solver.sampleCount)
    pickInd = np.random.randint(0, len(target))
    trueS = [np.random.random()*1000, np.random.random()*1000, target[pickInd]
             [0], target[pickInd][1], curs[pickInd], goals[pickInd], 0]

    sSet = []
    for i in range(0, len(target)):
        sSet.append([trueS[0], trueS[1], target[i][0],
                     target[i][1], curs[i], goals[i], 0])

    fig,ax = plt.subplots(); 


    # DEBUG: Add initial sketch
    # ------------------------------------------------------
    # params = {'centroid': [500, 500], 'dist_nom': 50, 'dist_noise': .25,
    #   'angle_noise': .3, 'pois_mean': 4, 'area_multiplier': 5, 'name': "Test", 'steepness': 20}
    # ske = Sketch(params)
    # solver.addSketch(ske);



    endFlag = False; 
    # Simulate until captured or out of time
    # ------------------------------------------------------
    for step in range(0, maxSteps):

        if(verbosity > 0):
            print("Starting step: {} of {}".format(step+1,maxSteps))

        # POMCP makes decision
        # ------------------------------------------------------
        act,info = solver.search(sSet, h, depth=min(solver.maxDepth, maxSteps-step+1), inform=True)
        if(verbosity > 1):
            print("Action: {}".format(solver.actionSet[act])); 

        # propagate state
        # ------------------------------------------------------
        trueS = solver.generate_s(trueS,solver.actionSet[act]);
        r = solver.generate_r(trueS,solver.actionSet[act]);

        sSet = solver.dynamicsUpdate(sSet,solver.actionSet[act]);
        o = solver.generate_o(trueS,solver.actionSet[act]); 
        if("Captured" in o):
            endFlag = True; 
        if(verbosity > 1):
            print("Observation: {}".format(o)); 

        # if(verbosity == 2):
        #     ax.clear(); 
        #     sSetNp = np.array(sSet); 
        #     sSetOff = sSetNp[sSetNp[:,6] == 1]; 
        #     sSetOn = sSetNp[sSetNp[:,6] == 0]; 
        #     ax.scatter(sSetOn[:,2],sSetOn[:,3], color = 'blue', alpha=0.9, edgecolor='none'); 
        #     ax.scatter(sSetOff[:,2],sSetOff[:,3], color = 'red', alpha = 0.9, edgecolor='none'); 
        #     ax.set_xlim([0,1000]); 
        #     ax.set_ylim([0,1000]); 
        #     plt.pause(0.1); 


        # if question was asked, see if human answered
        # ------------------------------------------------------
        sSet = solver.measurementUpdate(sSet,solver.actionSet[act],o); 
        sSet = solver.resampleSet(sSet); 

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


            if(solver.actionSet[act][0] is not None):
                theta_options = [180,0,90,270,135,45,315,225]
                theta = theta_options[solver.actionSet[act][0]]; 
            else:
                theta = 90;

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
        # checkSketch()

        # save everything
        # ------------------------------------------------------
        #h = Node(); 

        # repeat
        if(verbosity > 0):
            print(""); 
        if(endFlag):
            break; 


if __name__ == '__main__':

    #h = Node()
    #solver = POMCP('gridSoloSpec')
    simulate(verbosity=2)
