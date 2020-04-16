import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.widgets import Slider, Button
import numpy as np
import yaml
from sketchGen import Sketch
from collections import deque


def overlay():
    overhead = mpimg.imread("../img/overhead_mini_fit.png")
    underhead = mpimg.imread("../img/stichedFlyoverton.png")
    fig, ax = plt.subplots()
    imUnder = ax.imshow(underhead, alpha=1, zorder=0)
    imOver = ax.imshow(overhead, alpha=1, zorder=1)
    ax.set_axis_off()

    # print(overhead[:, :, 3])

    def sliderUpdate(idx):
        overhead[:, :, 3] = idx
        imOver.set_data(overhead)
        fig.canvas.draw_idle()

    axslider = plt.axes([0.15, 0.01, 0.7, 0.03])
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
    slider = Slider(axslider, "Alpha", 0, 1, valinit=1)
    slider.on_changed(sliderUpdate)
    plt.show()


def showPoints():
    overhead = mpimg.imread("../img/overhead_mini_fit.png")
    underhead = mpimg.imread("../img/stichedFlyoverton.png")
    fig, ax = plt.subplots()
    imUnder = ax.imshow(underhead, alpha=1, zorder=0)
    imOver = ax.imshow(overhead, alpha=1, zorder=1)
    ax.set_axis_off()

    def sliderUpdate(idx):
        overhead[:, :, 3] = idx
        imOver.set_data(overhead)
        fig.canvas.draw_idle()

    axslider = plt.axes([0.15, 0.01, 0.7, 0.03])
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
    slider = Slider(axslider, "Alpha", 0, 1, valinit=1)
    slider.on_changed(sliderUpdate)

    # load yaml
    with open("../yaml/landmarks.yaml", 'r') as stream:
        fi = yaml.safe_load(stream)

    params = {'centroid': [4, 5], 'dist_nom': 2, 'dist_noise': .25,
              'angle_noise': .3, 'pois_mean': 2, 'area_multiplier': 3, 'name': "Test", 'steepness': 5}
    allSketches = []
    for k, v in fi['Landmarks'].items():
        params['name'] = k
        params['dist_nom'] = v['radius']
        params['centroid'] = v['loc']
        allSketches.append(Sketch(params))
    sketchQueue = deque(allSketches)
    currentSketch = 0

    axSke = ax.scatter(-500, -500, alpha=1, zorder=2, color='red')
    #ax.set_xlim([0, 700])
    #ax.set_ylim([0, 700])
    axText = ax.text(0, 0, "", color='black', zorder=3)

    # print(fi['Landmarks'])
    # for k, v in fi['Landmarks'].items():
    #     #ax.scatter(v['loc'][0], v['loc'][1], color='red', zorder=2)
    #     ax.text(v['loc'][0] - 5*len(k), v['loc'][1], k, color='red', zorder=2)

    def buttonUpdate(event):
        #print("Next Sketch")
        ske = sketchQueue[0]
        sketchQueue.rotate(-1)
        axSke.set_offsets(ske.points)
        axText.set_text(ske.name)
        axText.set_position([ske.centroid[0]-5*len(ske.name), ske.centroid[1]])
        fig.canvas.draw_idle()

    anext = plt.axes([0.85, 0.01, 0.10, 0.03])
    bnext = Button(anext, 'Sketch')
    bnext.on_clicked(buttonUpdate)

    ax.set_xlim([0, 700])
    ax.set_ylim([700, 0])

    plt.show()


def showSketches():
    overhead = mpimg.imread("../img/overhead_mini_fit.png")
    underhead = mpimg.imread("../img/stichedFlyoverton.png")
    fig, ax = plt.subplots()
    imUnder = ax.imshow(underhead, alpha=1, zorder=0)
    imOver = ax.imshow(overhead, alpha=1, zorder=1)
    ax.set_axis_off()

    def sliderUpdate(idx):
        #print("Changing Slider")
        overhead[:, :, 3] = idx
        imOver.set_data(overhead)
        fig.canvas.draw_idle()

    axslider = plt.axes([0.15, 0.01, 0.7, 0.03])
    plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
    slider = Slider(axslider, "Alpha", 0, .99, valinit=.5)
    slider.on_changed(sliderUpdate)

    # load yaml
    with open("../yaml/landmarks.yaml", 'r') as stream:
        fi = yaml.safe_load(stream)

    params = {'centroid': [4, 5], 'dist_nom': 2, 'dist_noise': .25,
              'angle_noise': .3, 'pois_mean': 4, 'area_multiplier': 3, 'name': "Test", 'steepness': 1}
    allSketches = []
    seedCount = 2
    names = ['Pond', 'Neighborhood', 'GrayHouse1', 'Forest', 'Mountains']
    # for k, v in fi['Landmarks'].items():
    for k in names:
        v = fi['Landmarks'][k]
        params['name'] = k
        params['dist_nom'] = v['radius']
        params['centroid'] = v['loc']
        params['dist_noise'] = v['radius']/4
        allSketches.append(Sketch(params, seed=seedCount))
        seedCount += 1
    sketchQueue = deque(allSketches)
    currentSketch = 0

    #axSke = ax.scatter(-500, -500, alpha=1, zorder=2, color='red')
    newAx = fig.add_axes(ax.get_position(), frameon=False)
    newAx.set_axis_off()
    axSke = newAx.contourf(np.zeros(shape=(700, 700)),
                           cmap='Blues', zorder=2, alpha=0)

    # print(axSke.get_array())
    axText = newAx.text(0, 0, "", color='black', zorder=3)

    # print(fi['Landmarks'])
    # for k, v in fi['Landmarks'].items():
    #     #ax.scatter(v['loc'][0], v['loc'][1], color='red', zorder=2)
    #     ax.text(v['loc'][0] - 5*len(k), v['loc'][1], k, color='red', zorder=2)

    def clearOut():
        newAx.clear()
        #imUnder = ax.imshow(underhead, alpha=1, zorder=0)
        #imOver = ax.imshow(overhead, alpha=1, zorder=1)
        newAx.set_axis_off()
        # axslider = plt.axes([0.15, 0.01, 0.7, 0.03])
        # plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
        # slider = Slider(axslider, "Alpha", 0, 1, valinit=1)
        # slider.on_changed(sliderUpdate)

    def buttonUpdate(event):
        #print("Next Sketch")
        ske = sketchQueue[0]
        sketchQueue.rotate(-1)
        # axSke.set_offsets(ske.points)
        [x, y, c] = ske.sm.plot2D(
            low=[0, 0], high=[710, 710], vis=False, delta=10)

        [x_inf, y_inf, c_inf] = ske.sm_inf.plot2D(
            low=[0, 0], high=[710, 710], vis=False, delta=10)

        c_inf = np.array(c_inf)
        c_inf[c_inf == 0] = 20
        c_inf[c_inf < 20] = 0

        clearOut()
        newAx.contourf(x_inf, y_inf, c_inf, cmap="Reds", alpha=0.5)
        axSke = newAx.contourf(x, y, c,
                               cmap='Blues', zorder=2, alpha=0.5)

        newAx.set_ylim([700, 0])
        newAx.set_xlim([0, 700])
        newAx.set_aspect('equal')

        axText = newAx.text(0, 0, "", color='black', zorder=3)
        # axSke.set_alpha(.75)
        axText.set_text(ske.name)
        axText.set_position([ske.centroid[0]-5*len(ske.name), ske.centroid[1]])

        #axslider = plt.axes([0.15, 0.01, 0.7, 0.03])
        #plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
        #slider = Slider(axslider, "Alpha", 0, 1, valinit=1, zorder=4)
        # slider.on_changed(sliderUpdate)

        fig.canvas.draw_idle()

    anext = plt.axes([0.85, 0.01, 0.10, 0.03])
    bnext = Button(anext, 'Sketch')
    bnext.on_clicked(buttonUpdate)
    sliderUpdate(0.5)

    cid = fig.canvas.mpl_connect(
        'button_press_event', lambda event: onclick_classes(event, sketchQueue[-1]))

    ax.set_xlim([0, 700])
    ax.set_ylim([700, 0])
    newAx.set_ylim([700, 0])
    newAx.set_xlim([0, 700])

    plt.show()


def onclick_classes(event, ske):
    # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
    #       ('double' if event.dblclick else 'single', event.button,
    #        event.x, event.y, event.xdata, event.ydata))
    # print("Point Selected: [{:.2f},{:.2f}]".format(
        # event.xdata, event.ydata))

    point = [event.xdata, event.ydata]
    #point[1] = 700-point[1]
    if(event.dblclick):
        print("Double Click Unimplemented")
        pass

        # class_test = np.zeros(shape=(ske.sm.size))
        # for i in range(0, len(class_test)):
        #     class_test[i] = ske.sm.pointEvalND(i, point)

        # # print(class_test)

        # ans = {}
        # for l in ske.labels:
        #     ans[l] = 0
        #     for i in range(0, len(class_test)):
        #         te = ske.con_label[i]
        #         ans[l] += ske.con_label[i][l]*class_test[i]

        # suma = sum(ans.values())
        # for k in ans.keys():
        #     ans[k] /= suma

        # print("Outputing all label probabilities:")
        # for k, v in ans.items():
        #     if(v > 0.009):
        #         print("P: {:0.2f}, L: {}".format(v, k))

    elif(point[0] > 1 and point[1] > 1):
        # Find just most likely class
        # Check all softmax classes

        # Check if it's near
        near = ""
        near_test = np.zeros(shape=(ske.sm_inf.size))
        for i in range(0, len(near_test)):
            near_test[i] = ske.sm_inf.pointEvalND(i, point)
        if(np.argmax(near_test) == 0):
            near = 'Near'

        # Check other classes
        class_test = np.zeros(shape=(ske.sm.size))
        for i in range(0, len(class_test)):
            class_test[i] = ske.sm.pointEvalND(i, point)

        best = np.argmax(class_test)
        if(best == 0):
            near = ""
            best_lab = "Inside"
        else:
            te = ske.con_label[best]
            best_lab = max(te, key=te.get)

        if("North" in best_lab):
            best_lab = best_lab.replace("North", "South")
        elif("South" in best_lab):
            best_lab = best_lab.replace("South", "North")

        print("Most Likely Label: {}".format(near + " " + best_lab))
        print("")


if __name__ == '__main__':

    # overlay()
    # showPoints()
    showSketches()
