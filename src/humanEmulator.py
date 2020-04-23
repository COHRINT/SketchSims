import time
import threading

'''
***********************************************************
File: humanEmulator.py
Classes: Human
Allows for the creation and use of parameterized human
response engines which can interact in a separated fashion
with simulations
Mostly just a bag of timers

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


class Human:

    def __init__(self, params):
        # minimum seconds between skeches
        self.sketchBlock = params['sketchBlock']

        # Exponential Distribution Rate
        self.sketchRate = params['sketchRate']

        # minimum seconds between answers
        self.answerBlock = params['answerBlock']

        # Exponential Distribution Rate
        self.answerRate = params['answerRate']


if __name__ == '__main__':
    params = {'sketchBlock': 10, 'sketchRate': .2,
              'answerBlock': 5, 'answerRate': .2}

    h = Human()
