import random
from constants import *
from abstract import ParentSprite



class Food(ParentSprite):
    """ 
    Represents a piece of food in our game. Inherits from ParentSprite
    """


    def __init__(self):
        """ 
        Initializes a food object to a specified center and radius. 
        """
        super(Food, self).__init__()
        #self.center_x, self.center_y = SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] / 2
        self.radius = random.randint(5, 10)
        self.color = [155, 55, 0]
        self.eaten = False


