

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
import numpy as np
from sketchGen import Sketch
from softmaxModels import Softmax


def main(args):

    # x and y sketch points
    points = np.zeros((int((len(args)-1)/2),2),dtype=float)
    eval_point = [float(args[-2]),float(args[-1])]
    # get points of sketch from argvs
    for i in range(1,9):
        if i<=(len(args)-1)/2:

            points[i-1,0] = float(args[i])
        else:
            idx = i-int((len(args)-1)/2)-1
            points[idx,1] = float(args[i])

    c = centeroidnp(points)
    # sketch params
    params = {'steepness': 1}
    # create sketch
    mySketch = Sketch(params, tuple(points))
    out = mySketch.giveProbabilities(eval_point)
    # sm = fullPipeline(points)
    # out = giveProbabilities(sm, eval_point)
    print(out)
    # build a model from the sketch
    #mySoftmax.buildPointsModel([x,y],steepness=5)
    # test
    #mySoftmax.plot2D(low=[-10, -10], high=[10, 10], delta=0.1, vis=True)
    #val = mySoftmax.pointEvalND(2,[10,10])
    #print(val)


def fullPipeline(points):
    #np.random.seed(5)

    soft = Softmax()
    soft.buildPointsModel(points, steepness=5)
    joint, pclass, plabs = labelClasses(soft, points)
    # labelClasses_Example(soft, points)
    return soft


def giveProbabilities(sm,point):
    class_test = np.zeros(shape=(sm.size))
    for i in range(1, len(class_test)):
        class_test[i] = sm.pointEvalND(i, point)

        # print(class_test)

    ans = {}
    for l in labels:
        ans[l] = 0
        for i in range(1, len(class_test)):
            te = con_label[i]
            ans[l] += con_label[i][l]*class_test[i]
    ans['Inside'] = sm.pointEvalND(0,point); 

    suma = sum(ans.values())
    for k in ans.keys():
        ans[k] /= suma

    return ans; 

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