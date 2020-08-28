

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import *
from softmaxModels import Softmax
from scipy.spatial import ConvexHull
from shapely import affinity
from copy import deepcopy


'''
***********************************************************
File: sketchGen.py
Classes: Sketch
Allows for the creation and use of parameterized sketches
emulating humans

***********************************************************
'''


__author__ = "Luke Burks"
__copyright__ = "Copyright 2020, Cohrint"
__credits__ = ["Luke Burks"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Luke Burks"
__email__ = "luke.burks@colorado.edu"
__status__ = "Development"


class Sketch:

    def __init__(self, params, seed=None):
        if(seed is not None):
            np.random.seed(seed)

        self.name = params['name']
        self.centroid = params['centroid']
        if(params['points'] is not None):
            self.points = params['points']; 
        else:
            self.points = self.generateSketch(params)
        self.inflated = self.inflatePoints(params)
        self.labels = ['East', 'NorthEast', 'North', 'NorthWest',
                       'West', 'SouthWest', 'South', 'SouthEast']
        self.sm = Softmax()
        self.sm.buildPointsModel(self.points, steepness=params['steepness'])
        self.sm_inf = Softmax()
        self.sm_inf.buildPointsModel(
            self.inflated, steepness=params['steepness'])
        [self.joint, self.con_class, self.con_label] = self.labelClasses()

    def displayClasses(self, show=True):
        fig = plt.figure()
        [x, y, c] = self.sm.plot2D(low=[0, 0], high=[10, 10], vis=False)
        [x_inf, y_inf, c_inf] = self.sm_inf.plot2D(
            low=[0, 0], high=[10, 10], vis=False)

        c_inf = np.array(c_inf)
        c_inf[c_inf == 0] = 10
        c_inf[c_inf < 10] = 0

        plt.contourf(x_inf, y_inf, c_inf, cmap="Reds", alpha=1)
        plt.contourf(x, y, c, cmap="Blues", alpha=0.5)

        cid = fig.canvas.mpl_connect(
            'button_press_event', self.onclick_classes)

        if(show):
            plt.show()

    def onclick_classes(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        print("Point Selected: [{:.2f},{:.2f}]".format(
            event.xdata, event.ydata))
        point = [event.xdata, event.ydata]
        if(event.dblclick):
            class_test = np.zeros(shape=(self.sm.size))
            for i in range(0, len(class_test)):
                class_test[i] = self.sm.pointEvalND(i, point)

            # print(class_test)

            ans = {}
            for l in self.labels:
                ans[l] = 0
                for i in range(0, len(class_test)):
                    te = self.con_label[i]
                    ans[l] += self.con_label[i][l]*class_test[i]

            suma = sum(ans.values())
            for k in ans.keys():
                ans[k] /= suma

            print("Outputing all label probabilities:")
            for k, v in ans.items():
                if(v > 0.009):
                    print("P: {:0.2f}, L: {}".format(v, k))

        else:
            # Find just most likely class
            # Check all softmax classes

            # Check if it's near
            near = ""
            near_test = np.zeros(shape=(self.sm_inf.size))
            for i in range(0, len(near_test)):
                near_test[i] = self.sm_inf.pointEvalND(i, point)
            if(np.argmax(near_test) == 0):
                near = 'Near'

            # Check other classes
            class_test = np.zeros(shape=(self.sm.size))
            for i in range(0, len(class_test)):
                class_test[i] = self.sm.pointEvalND(i, point)

            best = np.argmax(class_test)
            if(best == 0):
                near = ""
                best_lab = "Inside"
            else:
                te = self.con_label[best]
                best_lab = max(te, key=te.get)

            print("Most Likely Class: {}".format(near + " " + best_lab))
            print("")

    def giveMostLikelyClass(self,point):
        near = ""
        near_test = np.zeros(shape=(self.sm_inf.size))
        for i in range(0, len(near_test)):
            near_test[i] = self.sm_inf.pointEvalND(i, point)
        if(np.argmax(near_test) == 0):
            near = 'Near'

        # Check other classes
        class_test = np.zeros(shape=(self.sm.size))
        for i in range(0, len(class_test)):
            class_test[i] = self.sm.pointEvalND(i, point)

        best = np.argmax(class_test)
        if(best == 0):
            near = ""
            best_lab = "Inside"
        else:
            te = self.con_label[best]
            best_lab = max(te, key=te.get)
        res = near + " " + best_lab; 
        return res

    def giveProbabilities(self,point):
        class_test = np.zeros(shape=(self.sm.size))
        for i in range(1, len(class_test)):
            class_test[i] = self.sm.pointEvalND(i, point)

        # print(class_test)

        ans = {}
        for l in self.labels:
            ans[l] = 0
            for i in range(1, len(class_test)):
                te = self.con_label[i]
                ans[l] += self.con_label[i][l]*class_test[i]
        ans['Inside'] = self.sm.pointEvalND(0,point); 

        suma = sum(ans.values())
        for k in ans.keys():
            ans[k] /= suma

        return ans; 

    def giveNearProb(self,point):
        near_test = np.zeros(shape=(self.sm_inf.size))
        for i in range(0, len(near_test)):
            near_test[i] = self.sm_inf.pointEvalND(i, point)
        return near_test; 


    def answerQuestion(self,point,label,thresh = .8):
        # res = self.giveMostLikelyClass(point)
        # if(res == label):

        ##################################################
        #TODO: Integrate Camera Positions
        ##################################################

        probs = self.giveProbabilities(point); 
        maxi = max(probs.values()); 
        for k in probs.keys():
            probs[k] /= maxi; 

        if(label == "Near"):
            nearProb = self.giveNearProb(point); 
            if(np.argmax(nearProb) == 0):
                return 'Yes'
            else:
                return 'No'
        elif("Near" in label):
            spl = label.split(); 
            nearProb = self.giveNearProb(point); 
            if(probs[spl[1]] > thresh and np.argmax(nearProb) == 0):
                return 'Yes'
            else:
                return 'No'
        elif(probs[label] > thresh):
            
            return 'Yes'; 
        else: 
            return 'No'; 


    def displayProbTables(self, show=True):
        plt.figure()

        matProb = np.zeros(shape=(self.sm.size, len(self.labels)+1))

        # For every class
        for i in range(0, len(self.con_label)):
            # normalize across self.con_label
            c = self.con_label[i]
            for j in range(0, len(self.labels)):
                matProb[i, j+1] = c[self.labels[j]]
        matProb[0, :] = 0
        matProb[0, 0] = 1

        plt.imshow(matProb, cmap='inferno')
        plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ['Inside', 'East', 'NorthEast',
                                                    'North', 'NorthWest', 'West', 'SouthWest', 'South', 'SouthEast'], rotation=90)
        plt.title("Conditional p(label | class)")
        plt.ylabel("Softmax Class")
        plt.colorbar()

        plt.figure()
        matProb = np.zeros(shape=(self.sm.size, len(self.labels)+1))

        # For every class
        for i in range(0, len(self.con_class)):
            # normalize across self.con_class
            c = self.con_class[i]
            for j in range(0, len(self.labels)):
                matProb[i, j+1] = c[self.labels[j]]
        matProb[0, :] = 0
        matProb[0, 0] = 1

        plt.imshow(matProb, cmap='inferno')
        plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ['Inside', 'East', 'NorthEast',
                                                    'North', 'NorthWest', 'West', 'SouthWest', 'South', 'SouthEast'], rotation=90)
        plt.title("Conditional p(class | label)")
        plt.ylabel("Softmax Class")
        plt.colorbar()

        if(show):
            plt.show()

    def displayPoints(self, show=True):
        plt.figure()
        plt.scatter(self.points[:, 0], self.points[:, 1])

        if(show):
            plt.show()

    def generateSketch(self, params):

        # given a point, spread rays out in random directions with semi random distance, and a random number of points

        # Tuning Paramters
        ####################################
        centroid = params['centroid']
        dist_nom = params['dist_nom']
        dist_noise = params['dist_noise']
        angle_noise = params['angle_noise']
        pois_mean = params['pois_mean']
        ####################################

        # Fixed Parameters
        ####################################
        # Has to be at least a triangle
        pois_min = 3
        ####################################

        # Chose Number of Points from Poisson Distribution
        numVerts = np.random.poisson(pois_mean)+pois_min

        # Debugging
        # numVerts = min(numVerts, 5)

        points = []

        # Note: Angles must preserve order
        totalAngle = 0
        # Precompute angles
        allAngles = np.zeros(numVerts)
        for i in range(0, numVerts):
            totalAngle += 2*np.pi/numVerts + np.random.normal(0, angle_noise)
            allAngles[i] = totalAngle

        # Normalize and expand to 2pi
        allAngles /= totalAngle
        allAngles *= 1.999*np.pi

        for i in range(0, numVerts):
            h = dist_nom + np.random.normal(0, dist_noise)
            points.append([h*np.cos(allAngles[i])+centroid[0],
                           h*np.sin(allAngles[i])+centroid[1]])

        points = np.array(points)

        cHull = ConvexHull(points)
        points = points[cHull.vertices]

        return points

    def inflatePoints(self, params):

        # Tuning Paramters
        ####################################
        area_multiplier = params['area_multiplier']
        ####################################

        ske = Polygon(self.points)

        ske2 = affinity.scale(ske, xfact=np.sqrt(
            area_multiplier), yfact=np.sqrt(area_multiplier))

        inflation = np.array(ske2.exterior.coords.xy).T

        return inflation

    def findLabels(self, point, centroid):
        # point must first be normalized with respect to centroid
        pprime = [point[0] - centroid.x, point[1] - centroid.y]

        ang = np.arctan2(pprime[1], pprime[0])*180/np.pi

        if(ang < 0):
            ang += 360

        allLabels = []

        # Off-Axial
        if(ang < 90):
            allLabels.append("NorthEast")
        elif(ang < 180):
            allLabels.append("NorthWest")
        elif(ang < 270):
            allLabels.append("SouthWest")
        elif(ang <= 360):
            allLabels.append("SouthEast")

        # On-Axial
        if(ang < 45):
            allLabels.append("East")
        elif(ang < 135):
            allLabels.append("North")
        elif(ang < 225):
            allLabels.append("West")
        elif(ang < 315):
            allLabels.append("South")
        elif(ang < 360):
            allLabels.append("East")
        return allLabels

    def labelClasses(self):

        # Take a ring of points, around centroid of object
        # For each point, identify it's cardinal direction, can be multiple levels
        # For each class, add together eval at points into direction labels
        # Normalize direction labels, and you have a soft classification of each class
        # Maybe threshold during normalization

        # Returns:
        # Joint probability dirLabs
        # Conditional p(class|labs)
        # Conditional p(labs|class)

        ske = Polygon(self.points)
        # print(ske.centroid)
        cent = ske.centroid
        hfactor = 3
        ra = hfactor*np.sqrt(ske.area/np.pi)

        # Direction Percentages
        dirLabs = []
        for i in range(0, len(self.points)+1):
            dirLabs.append({"West": 0, "East": 0, "North": 0, "South": 0,
                            "SouthWest": 0, "NorthWest": 0, "NorthEast": 0, "SouthEast": 0})

        numDegrees = 360
        testPoints = []
        for i in range(0, numDegrees):
            testPoints.append([ra*np.cos((i/numDegrees)*360 * np.pi/180)+cent.x,
                               ra*np.sin((i/numDegrees)*360 * np.pi/180)+cent.y])

        testPoints = np.array(testPoints)

        suma = 0
        # For each point
        for t in testPoints:
            # Find its labels
            labs = self.findLabels(t, cent)
            # Now apply to each class
            for c in range(0, self.sm.size):
                # eval
                tmp = self.sm.pointEvalND(c, t)
                for l in labs:
                    # add to dirLabs[c][l]
                    dirLabs[c][l] += tmp
                    suma += tmp

        # Normalize dirlabs to obtain p(class,label)
        for c in dirLabs:
            for k in c.keys():
                c[k] /= suma
            # print(c)

        cond_classes = deepcopy(dirLabs)
        labs = self.labels

        # For every class
        for i in range(0, len(cond_classes)):
            # normalize across labels
            c = cond_classes[i]
            suma = 0
            for k, v in c.items():
                suma += v
            for key in c.keys():
                c[key] /= suma

        cond_labs = deepcopy(dirLabs)

        for l in labs:
            suma = 0
            for c in cond_labs:
                suma += c[l]
            for c in cond_labs:
                c[l] /= suma

        return dirLabs, cond_classes, cond_labs


def fullPipeline():
    #np.random.seed(5)

    soft = Softmax()
    points = generateSketch(verbosity=1)
    soft.buildPointsModel(points, steepness=5)
    joint, pclass, plabs = labelClasses(soft, points)
    # labelClasses_Example(soft, points)

    [x, y, c] = soft.plot2D(low=[0, 0], high=[10, 10], vis=False)
    plt.contourf(x, y, c, cmap="Blues")

    plt.figure()
    matProb = np.zeros(shape=(soft.size, 9))
    labs = ['East', 'NorthEast', 'North', 'NorthWest',
            'West', 'SouthWest', 'South', 'SouthEast']

    # For every class
    for i in range(0, len(pclass)):
        # normalize across pclass
        c = pclass[i]
        for j in range(0, len(labs)):
            matProb[i, j+1] = c[labs[j]]
    matProb[0, :] = 0
    # matProb[0, 0] = 1

    plt.imshow(matProb, cmap='inferno')
    plt.xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], ['Inside', 'East', 'NorthEast',
                                                'North', 'NorthWest', 'West', 'SouthWest', 'South', 'SouthEast'], rotation=90)

    plt.show()

def testQuestions():
    params = {'centroid': [500, 500], 'dist_nom': 50, 'dist_noise': .25,
          'angle_noise': .3, 'pois_mean': 4, 'area_multiplier': 3, 'name': "Test", 'steepness': 15}
    ske = Sketch(params,seed=3)
    #ske.displayPoints();


    allX = []; 
    allY = []; 
    allColors = []; 
    label = 'North'

    for i in range(0,40):
        for j in range(0,40):
            x = 300 + i*10; 
            y = 300 + j*10; 
            ans = ske.answerQuestion([x,y],label); 
            #print(ans)
            allX.append(x); 
            allY.append(y); 
            if(ans == 'Yes'):
                allColors.append("green"); 
            else:
                allColors.append("red"); 
    # ans = ske.answerQuestion([500,500],label); 
    # print(ans); 
    plt.scatter(allX,allY,color=allColors); 
    plt.show();

if __name__ == '__main__':
    # np.random.seed(3)

    # params = {'centroid': [4, 5], 'dist_nom': 2, 'dist_noise': .25,
    #           'angle_noise': .3, 'pois_mean': 2, 'area_multiplier': 3, 'name': "Test", 'steepness': 5}
    # ske = Sketch(params)

    # # ske.displayPoints(show=False)
    # # ske.displayProbTables(show=False)
    # ske.displayClasses()

    testQuestions(); 
