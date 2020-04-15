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


def showSketches():
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
              'angle_noise': .3, 'pois_mean': 2, 'area_multiplier': 3, 'name': "Test"}
    allSketches = []
    for k, v in fi['Landmarks'].items():
        params['name'] = k
        params['dist_nom'] = v['radius']
        params['centroid'] = v['loc']
        allSketches.append(Sketch(params))
    sketchQueue = deque(allSketches)
    currentSketch = 0

    axSke = ax.scatter(0, 0, alpha=1, zorder=2, color='red')
    axText = ax.text(0, 0, "", color='black', zorder=3)

    # print(fi['Landmarks'])
    # for k, v in fi['Landmarks'].items():
    #     #ax.scatter(v['loc'][0], v['loc'][1], color='red', zorder=2)
    #     ax.text(v['loc'][0] - 5*len(k), v['loc'][1], k, color='red', zorder=2)

    def buttonUpdate(event):
        print("Next Sketch")
        ske = sketchQueue[0]
        sketchQueue.rotate(-1)
        axSke.set_offsets(ske.points)
        axText.set_text(ske.name)
        axText.set_position([ske.centroid[0]-5*len(ske.name), ske.centroid[1]])
        fig.canvas.draw_idle()

    anext = plt.axes([0.85, 0.01, 0.10, 0.03])
    bnext = Button(anext, 'Sketch')
    bnext.on_clicked(buttonUpdate)

    plt.xlim([0, 700])
    plt.ylim([0, 700])

    plt.show()


if __name__ == '__main__':

    # overlay()
    showSketches()
