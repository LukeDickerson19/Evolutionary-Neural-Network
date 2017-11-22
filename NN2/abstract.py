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

        # determine number of children
        if isinstance(self, Bot):
            number_of_children = 1
        else: number_of_children = \
        np.random.uniform(1,4)

        # get data on children
        children = []
        circles = model.bots + model.foods
        birth_distance = self.radius * np.random.uniform(2,5)
        d_ang = np.pi/15
        for i in range(number_of_children):

            child = {}

            # position
            overlapped = True
            angle2 = 0
            while overlapped:
                x = self.x + birth_distance*np.cos(-self.angle+angle2)
                y = self.y + birth_distance*np.sin(-self.angle+angle2)
                angle2 += d_ang
                if x > SCREEN_SIZE[0] or x < 0 or y > SCREEN_SIZE[1] or y < 0: continue
                overlapped = False
                for c in circles:
                    if self.get_dist(c) < c.radius + self.radius:
                        overlapped = True
                        break

            # angle
            child['angle'] = self.angle

            # create this child if we found a place for them
            if not overlapped: children.append(child)

        return children

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