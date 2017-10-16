import random
from constants import *
from abstract import ParentSprite
import pygame


class Food(ParentSprite):
    """ 
    Represents a piece of food in our game. Inherits from ParentSprite
    """


    def __init__(self):#, x, y, r, col):
        """ 
        Initializes a food object to a specified center and radius. 
        """
        super(Food, self).__init__()
        #self.center_x, self.center_y = SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2
        self.radius = FOOD_RADIUS
        self.color = FOOD_COLOR
        #self.center_x, self.center_y = x, y
        #self.radius = r
        #self.color = col
        self.eaten = False


