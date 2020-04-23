import sys
import numpy as np
from POMCPSolver import POMCP
from roadNode import RoadNode, readInNetwork, populatePoints, specifyPoint
from treeNode import Node
import matplotlib.pyplot as plt 


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


    # Simulate until captured or out of time
    # ------------------------------------------------------
    for step in range(0, maxSteps):

        if(verbosity > 0):
            print("Starting step: {} of {}".format(step+1,maxSteps))

        # POMCP makes decision
        # ------------------------------------------------------
        # act,info = solver.search(sSet, h, depth=min(maxDepth, maxSteps-step+1), inform=True)
        act = [0,0]

        # propagate state
        # ------------------------------------------------------
        sSet = solver.dynamicsUpdate(sSet,act[0]); 
        if(verbosity == 2):
            ax.clear(); 
            sSetNp = np.array(sSet); 
            sSetOff = sSetNp[sSetNp[:,6] == 1]; 
            sSetOn = sSetNp[sSetNp[:,6] == 0]; 
            ax.scatter(sSetOn[:,2],sSetOn[:,3], color = 'blue', alpha=0.9, edgecolor='none'); 
            ax.scatter(sSetOff[:,2],sSetOff[:,3], color = 'red', alpha = 0.9, edgecolor='none'); 
            ax.set_xlim([0,1000]); 
            ax.set_ylim([0,1000]); 
            plt.pause(0.1); 

        # if question was asked, see if human answered
        # ------------------------------------------------------
        # if(act[1] != 0):
        # askHuman()

        # check if human volunteered anything
        # ------------------------------------------------------
        # checkVolunteer()

        # check if human sketched anything
        # ------------------------------------------------------
        # checkSketch()

        # save everything
        # ------------------------------------------------------

        # repeat


if __name__ == '__main__':

    #h = Node()
    #solver = POMCP('gridSoloSpec')
    simulate()
