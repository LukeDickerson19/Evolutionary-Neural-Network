import pygame
import random
import time
from pygame.locals import QUIT, KEYDOWN
from pygame import gfxdraw
from constants import *
from food import *
from blob import *
import os


''' NOTES:

    TO DO:

        SHORT TERM (now):

            fix right eye
                display just right eye

            figure out that error that occationaly occurs
            in processing the visual field

            find places in vision where redundent calculations and code exist

            make it so blobs cannot overlap with eachother
                currently the program crashes when this happens b/c vision
                equations divide by 0 or something

            make it so health/energy bar is visable when you hover mouse over blob
            also have circle around mouse

            make it so you can pause the game w/ spacebar

            put all the blob and food variables that are constant in the constants.py file
                delete all the places they're initialized in the init of the blob's and food
                change all the names in the rest of the files

        MEDIUM TERM (later):

            get it to the point where there are bots moving around
            they have sight
            and food appears randomly around the screen

                take it step by step
                comment out everything in the loop
                print out stuff to console


        LONG TERM (eventually):

    SOURCES:

        gen idea:
        https://www.youtube.com/watch?v=GvEywP8t12I
        http://duncandhall.github.io/NaturalEvolution/index.html

        intro to neural networks:
        http://www.theprojectspot.com/tutorial-post/introduction-to-artificial-neural-networks-part-1/7

        useful for 2d graphics with pygame:
        https://www.pygame.org/docs/ref/draw.html

    OTHER:

        how to properly push to github:

            git add .
            git commit -m "asdf"
            git push -u origin master

            if fails: "Upload Files" on website



        '''


class PyGameView(object):
    """ 
    Provides a view of the environment in a pygame window 
    """


    def __init__(self, model, size):
        """ 
        Initialize model
        """
        self.model = model
        self.screen = pygame.display.set_mode(size)


    def draw_text(self, text, x, y, size, color=(100, 100, 100)):
        """ 
        Helper to draw text onto screen.

        Args:
            text (string): text to display
            x (int): horizontal position
            y (int): vertical position
            size (int): font size
            color (3-tuple int): color of text.  Can use pygame colors.
            defualt = (100, 100, 100)
        """
        basicfont = pygame.font.SysFont(None, size)
        text_render = basicfont.render(
            text, True, color)
        self.screen.blit(text_render, (x, y))


    def draw(self):
        """ 
        Draw blobs, food, and text to the pygame window 
        """
        # fill background
        self.screen.fill(pygame.Color('black'))

        # draw population number
        self.draw_text(str(self.model.population), 1, 1, 48)

        # draw controls helper
        if model.show_controls:
            for n, line in enumerate(CONTROLS):
                self.draw_text(line, 10, 50+14*n, 20)
        else:
            self.draw_text(
                "h = toggle help", 30, 1, 20)

        # draw food
        for food in self.model.foods:
            pygame.draw.circle(
                self.screen,
                food.color,
                (food.center_x, food.center_y),
                food.radius
                )                    

        # draw blobs
        for blob in self.model.blobs:
            if blob.alive:
                pygame.draw.circle(
                    self.screen, blob.color,
                    blob.int_center, int(blob.radius))
                # pygame.draw.circle(
                #     self.screen, pygame.Color('green'),
                #     blob.p_left, 2)
                # pygame.draw.circle(
                #     self.screen, pygame.Color('red'), 
                #     blob.p_right, 2)
                # pygame.draw.circle( # left eye
                #     self.screen, pygame.Color('white'),
                #     blob.left_eye_pos, 2)
                if model.draw_sight: # sight lines are toggleable

                    # draw left field of vision
                    self.draw_visual_field(blob, 'left_eye')

                    # draw right field of vision
                    self.draw_visual_field(blob, 'right_eye')

        pygame.display.update()

    def draw_visual_field(self, blob, eye):
        
        ex, ey = blob.eye_data[eye]['pos'][0], blob.eye_data[eye]['pos'][1]
        if eye == 'left_eye': e = -1
        else: e = 1 # right eye
        # pygame.gfxdraw.pie(self.screen, \
        #     int(ex), int(ey), int(blob.max_visable_distance), \
        #     int(180 * (theta + e*eye_sep - periph_angle) / np.pi), \
        #     int(180 * (theta + e*eye_sep + periph_angle) / np.pi), \
        #     pygame.Color('white'))
        for a in blob.left_arcs:
            d = a['d']
            left_angle  = np.arctan2(ey - a['left_side'][1],  ex - a['left_side'][0])
            right_angle = np.arctan2(ey - a['right_side'][1], ex - a['right_side'][0])
            
            #print 'left angle = %f\tright angle = %f' % (left_angle, right_angle)
            if left_angle > 0 and right_angle < 0: right_angle += 2*np.pi
            if a['empty']:
                num_angs = 25 * (abs(right_angle - left_angle)) / (np.pi/2)
                if num_angs < 2.0: num_angs = 2
            else: num_angs = 2
            angles = np.linspace(right_angle, left_angle, num_angs)
            len_ang_list = len(angles)
            points = [0.0] * len_ang_list
            for i in range(len_ang_list):
                points[i] = [ex - d*np.cos(angles[i]), ey - d*np.sin(angles[i])]
                #px, py = int(points[i][0]), int(points[i][1])
                #pygame.draw.circle(self.screen, pygame.Color('blue'), (px,py), 1)
            points.append([ex,ey])
            pygame.gfxdraw.filled_polygon(self.screen, points, a['color'])
            


class Model(object):
    """
    Represents the state of all entities in the environment and drawing
    parameters
    """


    def __init__(self, width, height):
        """
        initialize model, environment, and default keyboard controller states

        Args:
            width (int): width of window in pixels
            height (int): height of window in pixels
        """
        #window parameters / drawing
        self.height = height
        self.width = width
        self.show_gen = True #show generation number
        self.show_controls = False #controls toggle
        self.draw_sight = False #draw sight lines
        self.sleep_time = .005 #seconds between frames

        # create foods
        self.foods = []
        for i in range(0, FOOD_NUM):
            self.foods.append(Food())
        #self.foods.append(Food(330, 300, 10, pygame.Color('green')))
        #self.foods.append(Food(300, 300, 10,  pygame.Color('red')))
        #self.foods.append(Food(270, 300, 10,  pygame.Color('blue')))

        # create blobs
        self.blobs = []
        for i in range(0, BLOB_NUM):
            self.blobs.append(Blob())

        # population progressions
        self.population = 0
        self.vip_genes = []


    def update(self):
        """ 
        Update the model state. Each time update is called can be though of as
        a frame 
        """
        for blob in self.blobs:
            blob.update(self)

        # If all blobs are dead, start new cycle
        if self.blobs == []:
            self.create_population(NUM_PARENTS)
            self.vip_genes = []


    def create_population(self, num_winners=2):
        """ 
        create new population of blobs based on the top scoring blobs

        Args:
            num_winners (int): number of vip blobs to use
        """
        top_scoring = sorted(self.vip_genes, reverse=True)[:num_winners]

        for i in range(0, BLOB_NUM):
            new_NN = NN(parents_NN=top_scoring)
            self.blobs.append(Blob(new_NN))



class PyGameKeyboardController(object):
    """
    Keyboard controller that responds to keyboard input
    """


    def __init__(self, model):
        """
        Creates keyboard controller

        Args:
            model (object): contains attributes of the environment
        """
        self.model = model


    def handle_event(self, event):
        """ 
        Look for left and right keypresses to modify the x position of the paddle 

        Args:
            event (pygame class): type of event
        """
        if event.type != KEYDOWN:
            return True
        elif event.key == pygame.K_SPACE:
            return False
        elif event.key == pygame.K_d:
            for blob in model.blobs:
                print 'W1 is'
                print blob.nn.W1
                print ""
                print "W2 is"
                print ""
                print blob.nn.W2
                # break #iterate through first thing in a list
        elif event.key == pygame.K_k:
            for blob in model.blobs:
                blob.energy = 0
        elif event.key == pygame.K_s:
            model.show_gen = not model.show_gen
        elif event.key == pygame.K_PERIOD:
            model.sleep_time = max(model.sleep_time-0.005, 0.0)
        elif event.key == pygame.K_COMMA:
            model.sleep_time += 0.005
        elif event.key == pygame.K_h:
            model.show_controls = not model.show_controls
        elif event.key == pygame.K_a:
            model.draw_sight = not model.draw_sight
        return True



if __name__ == '__main__':
    pygame.init()
    size = SCREEN_SIZE

    model = Model(size[0], size[1])
    view = PyGameView(model, size)
    controller = PyGameKeyboardController(model)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                # handle event can end pygame loop
                if not controller.handle_event(event):
                    running = False
        model.update()
        if model.show_gen:
            view.draw()
            #time.sleep(model.sleep_time)


