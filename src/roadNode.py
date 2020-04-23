import yaml
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import shapely
from softmaxModels import Softmax
from copy import deepcopy
import warnings
import sys
warnings.filterwarnings("ignore", category=RuntimeWarning)


# undirected graph

# Ok we want a graph structure of a road network,
# where edge weights are distances, and edges are roads, nodes are intersections
# a point should traverse an edge at a proportional rate to the edges weight
# when it reaches the next node, randomly choose another edge to follow that is not
# the one it just came from


class RoadNode:

    def __init__(self, loc, ident=None):
        self.ident = ident  # Can be none
        self.loc = loc  # [x,y] cooridinate
        self.neighbors = []  # set of road nodes

    def addEdge(self, n):
        if(n not in self.neighbors):
            self.neighbors.append(n)
            n.neighbors.append(self)


def addNewRoad(a, b):
    a.addEdge(b)


def populatePoints(g, N=100):

    s = [0 for i in range(0, N)]
    curs = [0 for i in range(0, N)]
    goals = [0 for i in range(0, N)]
    for i in range(0, N):
        a = np.random.choice(g)
        # print(a.loc);
        # s[i] = deepcopy(a.loc);
        curs[i] = a
        goals[i] = np.random.choice(curs[i].neighbors)
        tmp = [0, 0]
        tmp[0] = (goals[i].loc[0]-curs[i].loc[0]) * \
            np.random.random() + curs[i].loc[0]
        tmp[1] = (goals[i].loc[1]-curs[i].loc[1]) * \
            np.random.random() + curs[i].loc[1]
        s[i] = tmp

    return np.array(s), curs, goals


def specifyPoint(g, N=100):
    s = [0 for i in range(0, N)]
    curs = [0 for i in range(0, N)]
    goals = [0 for i in range(0, N)]

    a = np.random.choice(g)
    c = a
    g = np.random.choice(c.neighbors)
    tmp = [0, 0]
    tmp[0] = (g.loc[0]-c.loc[0])*np.random.random() + c.loc[0]
    tmp[1] = (g.loc[1]-c.loc[1])*np.random.random() + c.loc[1]
    for i in range(0, N):
        curs[i] = c
        goals[i] = g
        s[i] = tmp

    return np.array(s), curs, goals


def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)


def propogatePoints(g, s, curs, goals):

    speed = 0.1
    dev = 2

    # for each point
    for i in range(0, len(s)):
        p = s[i]
        c = curs[i].loc
        g = goals[i].loc

        # move along vector to goal
        p[0] += (g[0]-c[0])*speed + np.random.normal(0, dev)
        p[1] += (g[1]-c[1])*speed + np.random.normal(0, dev)

        # if point has reached goal choose new goal
        # note: You'll want to make this not perfect equivalence
        # if(p[0] == g[0] and p[1] == g[1]):
        if(dist(p, c) > dist(c, g)):
            # print("Goal Reached!!!");
            l = [i for i in range(0, len(goals[i].neighbors))]
            if(len(l) > 1):
                l.remove(goals[i].neighbors.index(curs[i]))
            curs[i] = goals[i]
            p[0] = curs[i].loc[0]
            p[1] = curs[i].loc[1]
            tmp = np.random.choice(l)
            goals[i] = curs[i].neighbors[tmp]

        # print(curs[i].loc,goals[i].loc);


def measurementUpdate(meas, sm, s, curs, goals):

    origLen = len(s)

    s = np.array(s)
    curs = np.array(curs)
    goals = np.array(goals)
    sm = Softmax()
    # sm.buildRectangleModel([[1,5],[3,7]],steepness=7);
    sm.buildOrientedRecModel([2000, -2000], 0, 1, 1, steepness=7)

    weights = [sm.pointEvalND(meas, s[i]) for i in range(0, len(s))]

    weights /= np.sum(weights)

    csum = np.cumsum(weights)
    csum[-1] = 1

    indexes = np.searchsorted(csum, np.random.random(len(s)))
    s[:] = s[indexes]
    curs[:] = curs[indexes]
    goals[:] = goals[indexes]

    return s, curs, goals


def simProp(netFile, N=100, T=100, populate=True):

    # a = buildTestNetwork();
    a = readInNetwork(netFile)
    if(populate):
        s, curs, goals = populatePoints(a, N)
    else:
        s, curs, goals = specifyPoint(a, N)

    # fig, ax = plt.subplots()
    # fig.canvas.mpl_connect('button_press_event', onclick)
    # ax1 = fig.add_subplot(111, label='background')

    allStates = []

    for i in range(0, T):

        propogatePoints(a, s, curs, goals)
        # if(meas[i] is not None):
        #     s, curs, goals = measurementUpdate(meas[i], s, curs, goals)
        #     print("Measurement at time: {}".format(i+1))
        sp = np.array(s).T
        allStates.append(sp)

    return allStates


def readInNetwork(fileName):

    with open(fileName, 'r') as stream:
        f = yaml.safe_load(stream)

    allNodes = []

    for key in f['Nodes'].keys():
        allNodes.append(RoadNode(ident=key, loc=f['Nodes'][key]['loc']))

    for key in f['Nodes'].keys():

        for key2 in f['Nodes'][key]['neighbors']:
            allNodes[key].addEdge(allNodes[key2])
    global globalAllNodes
    globalAllNodes = allNodes

    return globalAllNodes


def displayNetworkMap(netFile, fig=None, ax=None, vis=True, redraw=False):
    global globalAllNodes

    if(redraw):
        net = globalAllNodes
        plt.cla()
    else:
        net = readInNetwork(netFile)

    with open(netFile, 'r') as stream:
        fil = yaml.safe_load(stream)

    allHighNodes = []
    if('HighNodes' in fil.keys()):
        highNodes = fil['HighNodes']

        for i in range(0, len(highNodes)):
            for j in range(0, len(highNodes)):
                allHighNodes.append([highNodes[i], highNodes[j]])

    cs = {"HighRoad": "#FFF2AF", "HighEdge": "#F6CF65", "Road": "#FFFFFF",
          "RoadEdge": "#D5D8DB", "Empty": "#E8E8E8", "Forest": "#C3ECB2", "Water": "#AADAFF", "Deserts": "#DBD1B4"}
    roadSize = 3
    riverSize = 4

    # plt.plot([1,2],[1,3],color=cs['HighEdge'],linewidth=roadSize+2);
    # plt.plot([1,2],[1,3],color=cs['HighRoad'],linewidth=roadSize);

    if(vis is True):
        fig, ax = plt.subplots()

    # Background
    # ------------------------------
    if('Extent' in fil.keys()):
        e = fil['Extent']
        # ax.add_patch(
        # Rectangle((-.2, -.2), e[0]+.2, e[1]+.2, fill=True, color=cs['Empty']))
        ax.add_patch(
            Rectangle((0, 0), e[0], e[1], fill=True, color=cs['Empty']))

    # Forest
    # ------------------------------
    if('Forests' in fil.keys()):
        forests = fil['Forests']

        for f in forests.keys():
            ax.add_patch(Rectangle(forests[f]['lowLeft'], forests[f]['width'],
                                   forests[f]['height'], fill=True, color=cs['Forest']))

    if('Deserts' in fil.keys()):
        forests = fil['Deserts']

        for f in forests.keys():
            ax.add_patch(Rectangle(forests[f]['lowLeft'], forests[f]['width'],
                                   forests[f]['height'], fill=True, color=cs['Deserts']))

    # Water
    # ------------------------------
    if("Water" in fil.keys()):
        waters = fil['Water']
        lakes = waters['Lakes']
        rivers = waters['Rivers']
        for r in rivers.keys():
            ax.plot([rivers[r]['start'][0], rivers[r]['end'][0]], [
                    rivers[r]['start'][1], rivers[r]['end'][1]], linewidth=riverSize, color=cs['Water'])

        for l in lakes.keys():
            ax.add_patch(
                Circle(lakes[l]['loc'], radius=lakes[l]['rad'], fill=True, color=cs['Water']))

    # Roads
    # ------------------------------
    for node in net:
        # for every neighbor
        for nei in node.neighbors:
            if([node.ident, nei.ident] in allHighNodes):
                # plot as high road
                ax.plot([node.loc[0], nei.loc[0]], [node.loc[1], nei.loc[1]],
                        linewidth=roadSize+2, color=cs['HighEdge'])
                ax.plot([node.loc[0], nei.loc[0]], [node.loc[1],
                                                    nei.loc[1]], linewidth=roadSize, color=cs['HighRoad'])
            else:
                ax.plot([node.loc[0], nei.loc[0]], [node.loc[1], nei.loc[1]],
                        linewidth=roadSize+2, color=cs['RoadEdge'])
                ax.plot([node.loc[0], nei.loc[0]], [node.loc[1],
                                                    nei.loc[1]], linewidth=roadSize, color=cs['Road'])

    ax.axis('off')

    if(vis):
        ax.set_aspect("equal")
        plt.show()
    else:
        return fig, ax


def displaySim(allStates):
    fig, ax = plt.subplots()
    # print(allStates[0].shape)
    #axSke = ax.scatter(-500, -500, color='red')
    for s in allStates:
        # ax.scatter(s[0], s[1])
        ax.clear()
        ax.scatter(s[0], s[1], color='red', alpha=0.15, edgecolor='none')
        ax.set_ylim([0, 1000])
        ax.set_xlim([0, 1000])
        plt.axis('off')
        plt.pause(0.1)
    # plt.show()


if __name__ == '__main__':

    file = '../yaml/flyovertonShift.yaml'
    # displayNetworkMap(file)
    allStates = simProp(netFile=file, N=1000, T=100, populate=True)
    displaySim(allStates)
