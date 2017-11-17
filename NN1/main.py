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

    GOOGLE CHALLENGES:

        google.com/foobar
        forbar.withgoogle.com

    LLE:

        free lancers

            work together to complete coding challenges
            gotta use api of companies they work for
                students:
                    free lancers that are tyring to become employees of companies
            like a multiplayer video-game

                challenges could last 15-minutes, or maybe it's one hour

                give it a crazy cool campapgn


        just i have no idea what your talking about 

        jack of all trades

        employees to train
        connect employees with homeless

    TO DO:

        SHORT TERM (now):

            check out: replika app - AI that talks to you

            gunna have to change up neural network in some way

                i think the reason the neural networks might not be displaying 
                any sort of "intelligent" behavior is because their inputs are
                usually gray

                    also why is there no bias in the equation?

                    also why is a neuron's output literally just the 
                    the squashed sum of its inputs? what about the
                    activation function?

                    might need to find a way to make the inputs more extreme
                        particularly the sight ones
                        but definately test them all

                        once thats done, messing with the MAX_ABS_WEIGHT would
                        be a good idea too

                    maybe print out some sort of average and std dev values over a
                    long span of time (a few seconds) to get an idea of what that 
                    neuron goes through



            gotta figure out how to run simulation:

                is there a way to control the number of blobs currently 
                alive by controlling how they reproduce and how food spawns?

                    do we want to remove the worst blob when one blob
                    eats food?

                    do we want the blobs to reproduce when they eat food?


                go through program and make it so it can draw faster

                    maybe make it so if food array is the same as last time
                    the food is not redrawn

                    or just look for other stuff



            check out (gpu cloud service):

                aws
                google compute
                azure

                check student teirs



            need to make input sensors more sensitive
            the nn isn't going to output much ever
            if its inputs are always close to zero

                consider sqashing the eye rgb inputs

        MEDIUM TERM (later):

            things to plot over time (t = iteration number, not time itself):

                number of blobs
                number of food


            look at the first iteration of source 1:

                how sensitive are the inputs?
                    tbd
                how does he make the neural network?
                    tbd
                how long does it take for effective survival 
                    behavior to become apparent?
                        a long time, but he has a thing that speeds it up
                        so that it takes about 5 minutes
                            how fast is it speed up, idk.
                how laggy is it on my computer
                    compared to his video?
                        Ans. Not laggy at all on my comp.
                how do the neural networks evolve?
                    can the weights be modified within an
                    organisms lifetime?

            look at the next iteration

                same questions ...

            then the next ... until there are no more

            also research how recurrent neural networks work

        LONG TERM (eventually):

    SOURCES:

        gen idea:
        https://www.youtube.com/watch?v=GvEywP8t12I
            https://sites.google.com/site/scriptbotsevo/
        https://www.youtube.com/watch?v=tCPzYM7B338
        https://www.youtube.com/watch?v=aircAruvnKk 3Blue1Brown
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

    def __init__(self, model, size1, size2):
        """ 
        Initialize model
        """
        self.model = model
        self.screen = pygame.display.set_mode((size1[0] + size2[0], size1[1]))
        self.simulation_surface = pygame.Surface((SCREEN_SIZE[0],   SCREEN_SIZE[1]))
        self.info_box_surface   = pygame.Surface((INFO_BOX_SIZE[0], INFO_BOX_SIZE[1]))

        self.mouse_pos = (0,0) # mouse position
        self.mouse_radius = 30 # radius of circle around mouse
        self.first_blob_drawing = True # this is so we draw the input/output keys for the blob nn only once
        self.last_time_steps_selected_circle = model.selected_circle
        self.first_food_drawing = True
        self.first_nothing = True

    def draw_text_in_simulation(self, text, x, y, size, color = (100, 100, 100)):
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
        self.simulation_surface.blit(text_render, (x, y))
    def draw_text_in_info_box(self,   text, x, y, size, color = (100, 100, 100)):
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
        self.info_box_surface.blit(text_render, (x, y))

    def draw_simulation(self):
        """ 
        Draw blobs, food, and text to the pygame window 
        """
        # fill background
        self.simulation_surface.fill(pygame.Color('black'))

        # draw population number
        self.draw_text_in_simulation(str(self.model.population), 1, 1, 48)

        # draw controls helper
        if model.show_controls:
            for n, line in enumerate(CONTROLS):
                self.draw_text_in_simulation(line, 10, 50+14*n, 20)
        #else: self.draw_text_in_simulation("h = toggle help", 30, 1, 20)

        # draw food
        for food in self.model.foods:
            pygame.draw.circle(
                self.simulation_surface,
                food.color,
                (food.center_x, food.center_y),
                food.radius
                )                    

        # draw blobs
        for blob in self.model.blobs:
            if blob.alive:
                pygame.draw.circle(
                    self.simulation_surface, blob.color,
                    blob.int_center, int(blob.radius))
                # pygame.draw.circle(
                #     self.simulation_surface, pygame.Color('green'),
                #     blob.p_left, 2)
                # pygame.draw.circle(
                #     self.simulation_surface, pygame.Color('red'), 
                #     blob.p_right, 2)
                # pygame.draw.circle( # left eye
                #     self.simulation_surface, pygame.Color('white'),
                #     blob.left_eye_pos, 2)


        # draw vision of the selected blob
        blob = self.model.selected_circle
        if blob != None and blob.__class__.__name__ == 'Blob':
            if model.draw_left:
                self.draw_visual_field(blob, 'left_eye')
            if model.draw_right:
                self.draw_visual_field(blob, 'right_eye')

        # draw mouse selector
        self.mouse_pos = pygame.mouse.get_pos()
        if  self.mouse_pos[0] < SCREEN_SIZE[0] and self.mouse_pos[0] > 0 \
        and self.mouse_pos[1] < SCREEN_SIZE[1] and self.mouse_pos[1] > 1:
            pygame.draw.circle(
                self.simulation_surface, pygame.Color('white'), \
                self.mouse_pos, self.mouse_radius, 1)

        pygame.display.update()

    def draw_visual_field(self, blob, eye):
        
        ex, ey = blob.eye_data[eye]['pos'][0], blob.eye_data[eye]['pos'][1]
        if eye == 'left_eye':
            e = -1
            arcs = blob.left_arcs
        else: # right eye
            e = 1
            arcs = blob.right_arcs
        # pygame.gfxdraw.pie(self.simulation_surface, \
        #     int(ex), int(ey), int(blob.max_visable_distance), \
        #     int(180 * (blob.angle + e*blob.eye_separation - blob.eye_peripheral_width) / np.pi), \
        #     int(180 * (blob.angle + e*blob.eye_separation + blob.eye_peripheral_width) / np.pi), \
        #     pygame.Color('white'))
        for a in arcs:
            d = a['d']
            left_angle  = np.arctan2(ey - a['left_side'][1],  ex - a['left_side'][0])
            right_angle = np.arctan2(ey - a['right_side'][1], ex - a['right_side'][0])
            
            #print 'left angle = %f\tright angle = %f' % (left_angle, right_angle)
            if left_angle > 0 and right_angle < 0: right_angle += 2*np.pi
            if a['circle'] == None:
                num_angs = 25 * (abs(right_angle - left_angle)) / (np.pi/2)
                if num_angs < 2.0: num_angs = 2
            else: num_angs = 2
            angles = np.linspace(right_angle, left_angle, num_angs)
            len_ang_list = len(angles)
            points = [0.0] * len_ang_list
            for i in range(len_ang_list):
                points[i] = [ex - d*np.cos(angles[i]), ey - d*np.sin(angles[i])]
                #px, py = int(points[i][0]), int(points[i][1])
                #pygame.draw.circle(self.simulation_surface, pygame.Color('blue'), (px,py), 1)
            points.append([ex,ey])
            pygame.gfxdraw.filled_polygon(self.simulation_surface, points, a['color'])
            
    def draw_info_box(self):

        # draw nn of selected bot
        if self.model.selected_circle != None:

            if model.selected_circle != self.last_time_steps_selected_circle:
                self.first_blob_drawing = True
                self.first_food_drawing = True

            if self.model.selected_circle.__class__.__name__ == 'Blob':
                blob = self.model.selected_circle

                # fill background
                if self.first_blob_drawing:
                    self.info_box_surface.fill(pygame.Color('black'))
                    pygame.draw.rect(self.info_box_surface, pygame.Color('black'), \
                        [0, 0, INFO_BOX_SIZE[0], 190])

                # draw line that separates info box from simulation
                pygame.draw.line( \
                    self.info_box_surface, \
                    pygame.Color('white'), \
                    (0,0), (0,INFO_BOX_SIZE[1]))

                # DRAW INPUT NEURONS OF NEURAL NETWORK
                input_x,  input_y  = 45,  25
                hidden_x, hidden_y = 180, 10
                output_x, output_y = 320, 100

                # DRAW WEIGHTS
                if self.first_blob_drawing:
                    
                    # input to hidden layer
                    for i in range(INPUT_LAYER_SIZE):
                        for h in range(HIDDEN_LAYER_SIZE):
                            self.draw_weight( \
                                input_x,  input_y+i*25, \
                                hidden_x, hidden_y+h*25, \
                                blob.nn.W1[i][h])
                            
                    # hidden to output
                    for h in range(HIDDEN_LAYER_SIZE):
                        for o in range(OUTPUT_LAYER_SIZE):
                            self.draw_weight( \
                                hidden_x, hidden_y+h*25, \
                                output_x, output_y+o*60, \
                                blob.nn.W2[h][o])

                    # DRAW NEURON OUTLINES
                    for i in range(INPUT_LAYER_SIZE):
                        self.draw_neuron_outline(input_x, input_y+i*25)

                    for h in range(HIDDEN_LAYER_SIZE):
                        self.draw_neuron_outline(hidden_x, hidden_y+h*25)

                    for o in range(OUTPUT_LAYER_SIZE):
                        self.draw_neuron_outline(output_x, output_y+o*60)


                # draw labels for everything
                self.draw_labels(input_x, input_y, hidden_x, hidden_y, output_x, output_y)

                selected_neuron = False

                # DRAW INPUT LAYER NEURONS
                for i in blob.input_list:
                    selected_neuron = selected_neuron or \
                    self.draw_neuron(input_x, input_y, i)
                    input_y += 25

                # DRAW HIDDEN LAYER NEURONS
                for h in blob.nn.hiddenLayer:
                    selected_neuron = selected_neuron or \
                    self.draw_neuron(hidden_x, hidden_y, h)
                    hidden_y += 25

                # DRAW OUTPUT LAYER NEURONS
                for o in [blob.left_wheel_rotation, blob.right_wheel_rotation]:
                    selected_neuron = selected_neuron or \
                    self.draw_neuron(output_x, output_y, o)
                    output_y += 60

                if not selected_neuron:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('black'), \
                    [320, 250, 70, 20])

                # reset other options
                self.first_food_drawing = True
                self.first_nothing = True    

            elif self.model.selected_circle.__class__.__name__ == 'Food':
                #print 'foooood'

                # fill background
                #pygame.draw.rect(self.info_box_surface, pygame.Color('black'), \
                #    [0, 0, INFO_BOX_SIZE[0], 190])
                self.info_box_surface.fill(pygame.Color('black'))

                # draw line that separates info box from simulation
                pygame.draw.line( \
                    self.info_box_surface, \
                    pygame.Color('white'), \
                    (0,0), (0,INFO_BOX_SIZE[1]))

                # reset other options
                self.first_blob_drawing = True                
                self.first_nothing = True

        # else nothing is selected
        else:

            # so just clear the whole screen
            # fill entire background
            if self.first_nothing:
                self.first_nothing = False

                self.info_box_surface.fill(pygame.Color('black'))

                # draw line that separates info box from simulation
                pygame.draw.line( \
                    self.info_box_surface, \
                    pygame.Color('white'), \
                    (0,0), (0,INFO_BOX_SIZE[1]))

            # reset other options
            self.first_blob_drawing = True
            self.first_food_drawing = True

        self.last_time_steps_selected_circle = model.selected_circle
    def draw_info_box_old(self):

        # draw nn of selected bot
        if self.model.selected_circle != None:
            if self.model.selected_circle.__class__.__name__ == 'Blob':
                blob = self.model.selected_circle

                # fill background (just the nn diagram part)
                pygame.draw.rect(self.info_box_surface, pygame.Color('black'), \
                    [0, 0, INFO_BOX_SIZE[0], 190])

                # draw line that separates info box from simulation
                pygame.draw.line( \
                    self.info_box_surface, \
                    pygame.Color('white'), \
                    (0,0), (0,INFO_BOX_SIZE[1]))

                # DRAW INPUT NEURONS OF NEURAL NETWORK
                bar = (40, 10)
                bar_input_x = 30

                # energy
                bar_y = 5
                self.draw_text_in_info_box('E', 5, bar_y, 20)
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y, (blob.energy/MAX_ENERGY)*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y, bar[0], bar[1]], 1)
                bar_y += 20

                # left eye
                self.draw_text_in_info_box('LE', 5, bar_y+bar[1], 20)
                lr, lg, lb = blob.visual_input['left_eye']
                if lr > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('red'), \
                        [bar_input_x, bar_y, lr*bar[0], bar[1]])
                if lg > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('green'), \
                        [bar_input_x, bar_y+bar[1], lg*bar[0], bar[1]])
                if lb > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('blue'), \
                        [bar_input_x, bar_y+2*bar[1], lb*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y,        bar[0], 3*bar[1]], 1)
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y+bar[1], bar[0], bar[1]], 1)
                bar_y += 40

                # right eye
                self.draw_text_in_info_box('RE', 5, bar_y+bar[1], 20)
                rr, rg, rb = blob.visual_input['right_eye']
                if rr > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('red'), \
                        [bar_input_x, bar_y, rr*bar[0], bar[1]])
                if rg > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('green'), \
                        [bar_input_x, bar_y+bar[1], rg*bar[0], bar[1]])
                if rb > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('blue'), \
                        [bar_input_x, bar_y+2*bar[1], rb*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y,        bar[0], 3*bar[1]], 1)
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y+bar[1], bar[0], bar[1]], 1)
                bar_y += 40

                # hearing
                self.draw_text_in_info_box('H', 5, bar_y, 20)
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y, blob.noise_heard*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y, bar[0], bar[1]], 1)
                bar_y += 20

                # food smell
                self.draw_text_in_info_box('FS', 5, bar_y, 20)
                pygame.draw.rect(self.info_box_surface, FOOD_COLOR, \
                    [bar_input_x, bar_y, blob.food_smell*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y, bar[0], bar[1]], 1)
                bar_y += 20

                # blob smell
                self.draw_text_in_info_box('BS', 5, bar_y, 20)
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y, blob.blob_smell*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_input_x, bar_y, bar[0], bar[1]], 1)
                bar_y += 20

                # draw input key
                if self.first_blob_drawing:
                    self.draw_text_in_info_box("INPUTS:", 15, 200, 20)
                    for n, line in enumerate(KEY_INPUTS):
                        self.draw_text_in_info_box(line, 15, 205+14*(n+1), 20)                

                # DRAW OUTPUT NEURONS OF NEURAL NETWORK
                output_x = 320

                # left wheel rotation
                output_y = 60
                self.draw_text_in_info_box('LW', output_x+bar[0]+10, bar_y, 20)
                self.draw_neuron(output_x, output_y, blob.left_wheel_rotation)
                output_y += 20

                # right wheel rotation
                self.draw_text_in_info_box('RW', output_x+bar[0]+10, bar_y, 20)
                self.draw_neuron(output_x, output_y, blob.right_wheel_rotation)
                bar_y += 20


                # draw output key
                if self.first_blob_drawing:
                    self.first_blob_drawing = False
                    self.draw_text_in_info_box("OUTPUTS:", 220, 200, 20)
                    for n, line in enumerate(KEY_OUTPUTS):
                        self.draw_text_in_info_box(line, 220, 205+14*(n+1), 20)

                # DRAW HIDDEN LAYER AND WEIGHTS
                hidden_x = 150
                hidden_y = 10

                for node in blob.nn.hiddenLayer:

                    self.draw_neuron(hidden_x, hidden_y, node)
                    hidden_y += 20

                # reset first_food_drawing
                self.first_food_drawing = True
                

            elif self.model.selected_circle.__class__.__name__ == 'Food':
                #print 'foooood'

                # fill background
                #pygame.draw.rect(self.info_box_surface, pygame.Color('black'), \
                #    [0, 0, INFO_BOX_SIZE[0], 190])
                self.info_box_surface.fill(pygame.Color('black'))

                # draw line that separates info box from simulation
                pygame.draw.line( \
                    self.info_box_surface, \
                    pygame.Color('white'), \
                    (0,0), (0,INFO_BOX_SIZE[1]))

            # reset first_blob_drawing
            self.first_blob_drawing = True                

        # else nothing is selected
        else:

            # so just clear the whole screen
            # fill entire background
            self.info_box_surface.fill(pygame.Color('black'))

            # draw line that separates info box from simulation
            pygame.draw.line( \
                self.info_box_surface, \
                pygame.Color('white'), \
                (0,0), (0,INFO_BOX_SIZE[1]))

            # reset first_blob_drawing and first_food_drawing
            # to True for when next circle is selected
            self.first_blob_drawing = True
            self.first_food_drawing = True

    def draw_neuron(self, x, y, value):

        # draw the circle for the neuron
        col = int(255.0 * (value + 1.0) / 2.0)
        if col > 255: col = 255
        if col < 0: col = 0
        radius = 7
        #if value >= 0: col = pygame.Color('green')
        #else: col = pygame.Color('red')
        #min_radius, max_radius = 2.0, 10.0
        #radius = int((max_radius - min_radius) * abs(value) + min_radius)
        #if radius > max_radius: radius = int(max_radius)
        pygame.draw.circle(self.info_box_surface, [col,col,col], (x,y), radius)

        # draw the rectangle with the neurons value in it
        # if the mouse is over the displayed neuron
        if np.sqrt((self.mouse_pos[0] - (x+SCREEN_SIZE[0]))**2 + \
                   (self.mouse_pos[1] - y)**2) <= 7.0:

            pygame.draw.rect(self.info_box_surface, [100,100,100], \
                [320, 250, 70, 20])
            self.draw_text_in_info_box('%.3f' % (value), 320, 250, 34, pygame.Color('black'))
            return True
        return False
    def draw_neuron_outline(self, x, y):
        radius = 8
        pygame.draw.circle(self.info_box_surface, pygame.Color('white'), (x,y), radius)
    def draw_weight(self, start_x, start_y, end_x, end_y, weight):

        min_abs_val = 0.10
        if weight > min_abs_val or weight < -min_abs_val:

            if weight >= 0: col = pygame.Color('green')
            else: col = pygame.Color('red')

            min_width, max_width = 1.0, 4.0
            width = int((max_width - min_width) * abs(weight) + min_width)
            if width > max_width: width = int(max_width)

            pygame.draw.line(self.info_box_surface, col, \
                (start_x, start_y), (end_x, end_y), width)

    def draw_labels(self, input_x, input_y, hidden_x, hidden_y, output_x, output_y):

        # energy
        self.draw_text_in_info_box('E', input_x-40, input_y-7, 20)
        input_y += 50

        # left eye
        self.draw_text_in_info_box('LE', input_x-40, input_y-7,    20)
        self.draw_text_in_info_box('R',  input_x-20,  input_y-25-7, 20, pygame.Color('red'))
        self.draw_text_in_info_box('G',  input_x-20,  input_y-7,    20, pygame.Color('green'))
        self.draw_text_in_info_box('B',  input_x-20,  input_y+25-7, 20, pygame.Color('blue'))
        input_y += 75

        # right eye
        self.draw_text_in_info_box('RE', input_x-40, input_y-7,    20)
        self.draw_text_in_info_box('R',  input_x-20,  input_y-25-7, 20, pygame.Color('red'))
        self.draw_text_in_info_box('G',  input_x-20,  input_y-7,    20, pygame.Color('green'))
        self.draw_text_in_info_box('B',  input_x-20,  input_y+25-7, 20, pygame.Color('blue'))
        input_y += 50

        # # hearing
        self.draw_text_in_info_box('H', input_x-40, input_y-7, 20)
        input_y += 25

        # # food smell
        self.draw_text_in_info_box('FS', input_x-40, input_y-7, 20)
        input_y += 25

        # blob smell
        self.draw_text_in_info_box('BS', input_x-40, input_y-7, 20)
        input_y += 25

        # draw input key
        if self.first_blob_drawing:
            self.draw_text_in_info_box("INPUTS:", 15, 290, 20)
            for n, line in enumerate(KEY_INPUTS):
                self.draw_text_in_info_box(line, 15, 295+14*(n+1), 20)                


        # DRAW OUTPUT

        # left wheel rotation
        self.draw_text_in_info_box('LW', output_x+14, output_y-7, 20)
        output_y += 60

        # right wheel rotation
        self.draw_text_in_info_box('RW', output_x+14, output_y-7, 20)
        
        # draw output key
        if self.first_blob_drawing:
            self.first_blob_drawing = False
            self.draw_text_in_info_box("OUTPUTS:", 220, 290, 20)
            for n, line in enumerate(KEY_OUTPUTS):
                self.draw_text_in_info_box(line, 220, 295+14*(n+1), 20)

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
        self.show_gen = True # show generation number

        self.show_controls = False # controls toggle
        self.draw_left  = False # draw left eye field of view of selected circle
        self.draw_right = False # draw right eye field of view of selected circle
        self.selected_circle = None # blob or food selected for display in the info box
        #self.sleep_time = .005 #seconds between frames

        # create food and blobs
        self.foods, self.blobs = [], []
        for i in range(0, FOOD_NUM):
            self.foods.append(Food(self))
        for i in range(0, BLOB_NUM):
            self.blobs.append(Blob(self, np.random.randint(256, size=3)))

        # population progressions
        self.population = 0
        self.vip_genes = []

    def update(self, controller):
        """ 
        Update the model state. Each time update is called can be though of as
        a frame 
        """

        for blob in self.blobs:
            blob.update_inputs(self, controller)
        for blob in self.blobs:
            blob.update_outputs(self)


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
            self.blobs.append(Blob(self, np.random.randint(256, size=3), new_NN))

class PyGameKeyboardController(object):
    """
    Keyboard controller that responds to keyboard input
    """


    def __init__(self):
        """
        Creates keyboard controller

        Args:
            model (object): contains attributes of the environment
        """
        #self.model = model
        self.paused = False


    def handle_event(self, event):
        """ 
        Look for left and right keypresses to modify the x position of the paddle 

        Args:
            event (pygame class): type of event
        """
        if event.type != KEYDOWN:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    #print 'mouse wheel scroll up'
                    view.mouse_radius += 5
                    if view.mouse_radius >= 100: view.mouse_radius = 100
                elif event.button == 5:
                    #print 'mouse wheel scroll down'
                    view.mouse_radius -= 5
                    if view.mouse_radius <= 5: view.mouse_radius = 5 
                elif event.button == 1:
                    #print 'mouse left click'
                    # select any blob or food in the circle
                    # if multiple circles in mouse circle
                    # select one closest to center
                    mx, my = view.mouse_pos
                    if mx < SCREEN_SIZE[0] and mx > 0 \
                    and my < SCREEN_SIZE[1] and my > 0:
                        model.selected_circle = None
                        closest_distance = view.mouse_radius + 5
                        circles = model.blobs + model.foods
                        for c in circles:
                            distance = np.sqrt((c.center_x - mx)**2 + (c.center_y - my)**2)
                            if distance <= view.mouse_radius and distance < closest_distance:
                                closest_distance = distance
                                model.selected_circle = c
                        print model.selected_circle
                elif event.button == 3:
                    print 'mouse right click'
                else:
                    print 'event.button = %d' % event.button
            return True
        elif event.key == pygame.K_SPACE:
            self.paused = not self.paused
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
            if not model.show_gen:
                model.show_controls   = False
                model.draw_left       = False
                model.draw_right      = False
                model.selected_circle = None

        #elif event.key == pygame.K_PERIOD:
        #    model.sleep_time = max(model.sleep_time-0.005, 0.0)
        #elif event.key == pygame.K_COMMA:
        #    model.sleep_time += 0.005
        elif event.key == pygame.K_h:
            model.show_controls = not model.show_controls
        elif event.key == pygame.K_l:
            model.draw_left = not model.draw_left
        elif event.key == pygame.K_r:
            model.draw_right = not model.draw_right
        return True



if __name__ == '__main__':
    pygame.init()

    model = Model(SCREEN_SIZE[0], SCREEN_SIZE[1])
    view = PyGameView(model, SCREEN_SIZE, INFO_BOX_SIZE)
    controller = PyGameKeyboardController()
    running = True

    start_time = time.time()
    period = 1
    iterations = 0

    while running:

        iterations += 1
        if time.time() - start_time > period:
            start_time += period
            print '%s fps' % iterations
            iterations = 0

        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                # handle event can end pygame loop
                if not controller.handle_event(event):
                    running = False

        if not controller.paused:
            model.update(controller)
        
        if model.show_gen:
            view.draw_simulation()
            view.draw_info_box()
            view.screen.blit(view.simulation_surface, (0,0))
            view.screen.blit(view.info_box_surface,   (SCREEN_SIZE[0],0))
            pygame.display.update()
            #time.sleep(model.sleep_time)


