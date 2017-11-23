import math
import numpy as np
import random
from constants import *


class ParentSprite(object):
    """
    Parent class for sprites that defines standard methods and attributes for
    all sprites
    """


    def __init__(self, model, dna=None):

        # position
        try: self.x, self.y = dna['x'], dna['y']
        except:

            overlapped = True
            circles = model.bots + model.foods
            while overlapped:
                self.x = np.random.uniform(0, SCREEN_SIZE[0])
                self.y = np.random.uniform(0, SCREEN_SIZE[1])
                overlapped = False
                for c in circles:
                    if self.get_dist(c) < c.radius + self.radius:
                        overlapped = True
                        break
        self.int_center = int(self.x), int(self.y)

        # angle
        try: self.angle = dna['angle']
        except: self.angle = np.random.uniform(0, 2*np.pi)

    def reproduce(self, model):

        # get data on child
        circles = model.bots + model.foods
        birth_distance = self.radius * np.random.uniform(2,15)
        d_ang = np.pi/15

        child = {}

        # position
        overlapped = True
        angle = np.random.uniform(0,2*np.pi)
        angle2 = 0
        while overlapped:
            x = self.x + birth_distance*np.cos(angle+angle2)
            y = self.y + birth_distance*np.sin(angle+angle2)
            angle2 += d_ang
            if angle2 > 2*np.pi: break
            if x > SCREEN_SIZE[0] or x < 0 or y > SCREEN_SIZE[1] or y < 0: continue
            overlapped = False
            for c in circles:
                if np.sqrt((c.x-x)**2 + (c.y-y)**2) < \
                    c.radius + self.radius:
                    overlapped = True
                    break
        child['x'], child['y'] = x, y
        child['found_spot'] = not overlapped

        # angle
        child['angle'] = angle

        return child

    def get_dist(self, other):
        """ 
        The distance between two abstract sprites

        Args:
            other (object) - the other sprite
        """
        dist = np.hypot(
            other.x-self.x, other.y-self.y)
        return dist

    def intersect(self, other):
        """
        Tells whether or not two AbstractSprites are intersecting
            
        Args: 
            other (object) - the other sprite
        """
        dist = self.get_dist(other)
        return dist < self.radius + other.radius

    def angle_between(self, other):
        """ 
        Gets the angle between this sprite and another Abstract Sprite
            
        Args:
            other (object): other the other sprite
        """
        deltaX = other.x - self.x
        deltaY = other.y - self.y
        return math.atan2(deltaY, deltaX)