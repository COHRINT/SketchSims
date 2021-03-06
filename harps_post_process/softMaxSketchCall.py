

""" Calls softmax for matlab post process script"""

__author__ = "Trevor Slack"
__copyright__ = "Copyright 2021, Cohrint"
__credits__ = ["Trevor Slack","Hunter Ray"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Trevor Slack"
__email__ = "trevor.slack@colorado.edu"
__status__ = "Development"

import sys
import math
import numpy as np
from sketchGen import Sketch
from softmaxModels import Softmax


def main(args):

    # x and y sketch points
    points = np.zeros((int((len(args)-3)/2),2),dtype=float)
    eval_point = [float(args[-2]),float(args[-1])]
    # get points of sketch from argvs
    for i in range(1,5):
        points[i-1,0] = float(args[i])
    for i in range(5,9):
        # print(i)
        points[i-5,1] = float(args[i])
        # print(points[i-5,1])
    #print(points)
    #print(eval_point)
    # for i in range(1,9):
    #     if i<=(len(args)-3)/2:

    #         points[i-1,0] = float(args[i])
    #     else:
    #         idx = i-int((len(args)-1)/2)-1
    #         points[idx,1] = float(args[i])

    c = centeroidnp(points)
    # print(points)
    # print(eval_point)
    # sketch params
    params = {'steepness': 7,'area_multiplier': 3}
    # create sketch
    mySketch = Sketch(params, tuple(points))
    out = mySketch.giveProbabilities(eval_point)
    tmp = mySketch.giveNearProb(eval_point)
    # for i in range(0,len(tmp)):
	   #  if math.isnan(tmp[i]):
	   #  	tmp = '[-1.111111e-7,-1.111111e-7,-1.111111e-7,-1.111111e-7,-1.111111e-7,-1.111111e-7]'
	   #  	break
    print(tmp)
    print(out)


# def fullPipeline(points):
#     #np.random.seed(5)

#     soft = Softmax()
#     soft.buildPointsModel(points, steepness=5)
#     joint, pclass, plabs = labelClasses(soft, points)
#     # labelClasses_Example(soft, points)
#     return soft


# def giveProbabilities(sm,point):
#     class_test = np.zeros(shape=(sm.size))
#     for i in range(1, len(class_test)):
#         class_test[i] = sm.pointEvalND(i, point)

#         # print(class_test)

#     ans = {}
#     for l in labels:
#         ans[l] = 0
#         for i in range(1, len(class_test)):
#             te = con_label[i]
#             ans[l] += con_label[i][l]*class_test[i]
#     ans['Inside'] = sm.pointEvalND(0,point); 

#     suma = sum(ans.values())
#     for k in ans.keys():
#         ans[k] /= suma

#     return ans; 


def centeroidnp(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length

if __name__ == "__main__":
    n = len(sys.argv)
    if n<2:
        print("Not enought argv")
    else:
        main(sys.argv)