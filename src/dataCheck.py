import sys
import numpy as np
from POMCPSolver import POMCP
from roadNode import RoadNode, readInNetwork, populatePoints, specifyPoint, dist
from treeNode import Node
import matplotlib.pyplot as plt 
from sketchGen import Sketch
from softmaxModels import Softmax 
from collections import deque
import math
from shapely.geometry import Polygon, Point
import yaml


def check():
    a = np.load('../data/simHARPS_Test.npy').item(); 




if __name__ == '__main__':
    check(); 