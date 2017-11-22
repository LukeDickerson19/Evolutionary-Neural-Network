import random
from constants import *
from abstract import ParentSprite
import pygame


class Food(ParentSprite):
    """ 
    Represents a piece of food in our game. Inherits from ParentSprite
    """


    def __init__(self, model, dna=None):
        """ 
        Initializes a food object to a specified center and radius. 
        """
        self.radius = FOOD_MAX_RADIUS
        super(Food, self).__init__(model, dna)
        self.radius = FOOD_START_RADIUS

        self.color = FOOD_COLOR
        self.eaten = False


    def update(self, model):

    	if self.radius < FOOD_MAX_RADIUS:
			self.radius += FOOD_GROWTH_RATE

    	else:
    		self.radius = FOOD_START_RADIUS
    		self.reproduce_asexually(model)


    def reproduce_asexually(self, model):

    	children = self.reproduce(model)
    	for child in children:
    		model.foods.append(Food(model, child))



