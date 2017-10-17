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

            mouse wheel controls circle radius

            make it so you can click on a blob and it displays
            data on it in a box on the right 
                make mouse have selection circle around it
                    get mouse circle to select blobs or food
                        what to do if both are in circle?
                    put mouse stuff in controller and/or view, not the model
                        want to be able to pause it and click a blob
                use this to test vision and smell and energy

            figure out that error that occationaly occurs
            in processing the visual field
                take a picture of the error message
                it says something like array index out of bounds
                in the arc array for the visual field in the blob.py file

            currently theres nothing that limits how fast a blob can move
            i made a variable called max_wheel_angular_velocity in the blob init
            but nothing uses it yet

        MEDIUM TERM (later):

            make hearing and smell sensors


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
    def draw_text_in_info_box(self, text, x, y, size, color = (100, 100, 100)):
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
        else: self.draw_text_in_simulation("h = toggle help", 30, 1, 20)

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

                # sight lines are toggleable
                if model.draw_sight and model.selected_circle == None:

                    # draw left and right field of vision
                    self.draw_visual_field(blob, 'left_eye')
                    self.draw_visual_field(blob, 'right_eye')

        # draw vision of the selected blob
        blob = self.model.selected_circle
        if model.draw_sight and blob != None and blob.__class__.__name__ == 'Blob':
                self.draw_visual_field(blob, 'left_eye')
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
                #pygame.draw.circle(self.simulation_surface, pygame.Color('blue'), (px,py), 1)
            points.append([ex,ey])
            pygame.gfxdraw.filled_polygon(self.simulation_surface, points, a['color'])
            
    def draw_info_box(self):

        # fill background
        self.info_box_surface.fill(pygame.Color('black'))

        # draw line that separates info box from simulation
        pygame.draw.line( \
            self.info_box_surface, \
            pygame.Color('white'), \
            (0,0), (0,INFO_BOX_SIZE[1]))


        if self.model.selected_circle != None:
            if self.model.selected_circle.__class__.__name__ == 'Blob':
                blob = self.model.selected_circle
                
                # draw inputs of neural network
                bar = (40, 10)
                bar_start_x = 30

                # energy
                self.draw_text_in_info_box('E', 5, 5, 20, [255, 255, 255])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 5, (blob.energy/MAX_ENERGY)*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 5, bar[0], bar[1]], 1)

                # left eye
                self.draw_text_in_info_box('L', 5, 30+bar[1], 20, [255, 255, 255])
                lr, lg, lb = blob.visual_input['left_eye']
                if lr > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('red'), \
                        [bar_start_x, 30, lr*bar[0], bar[1]])
                if lg > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('green'), \
                        [bar_start_x, 30+bar[1], lg*bar[0], bar[1]])
                if lb > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('blue'), \
                        [bar_start_x, 30+2*bar[1], lb*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 30,        bar[0], 3*bar[1]], 1)
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 30+bar[1], bar[0], bar[1]], 1)

                # right eye
                self.draw_text_in_info_box('R', 5, 70+bar[1], 20, [255, 255, 255])
                rr, rg, rb = blob.visual_input['right_eye']
                if rr > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('red'), \
                        [bar_start_x, 70, rr*bar[0], bar[1]])
                if rg > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('green'), \
                        [bar_start_x, 70+bar[1], rg*bar[0], bar[1]])
                if rb > 0.0:
                    pygame.draw.rect(self.info_box_surface, pygame.Color('blue'), \
                        [bar_start_x, 70+2*bar[1], rb*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 70,        bar[0], 3*bar[1]], 1)
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 70+bar[1], bar[0], bar[1]], 1)

                # food smell
                self.draw_text_in_info_box('FS', 5, 110, 20, [255, 255, 255])
                pygame.draw.rect(self.info_box_surface, pygame.Color('orange'), \
                    [bar_start_x, 110, blob.food_smell*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 110, bar[0], bar[1]], 1)

                # blob smell
                self.draw_text_in_info_box('BS', 5, 130, 20, [255, 255, 255])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 130, blob.blob_smell*bar[0], bar[1]])
                pygame.draw.rect(self.info_box_surface, pygame.Color('white'), \
                    [bar_start_x, 130, bar[0], bar[1]], 1)

                # draw outpus of neural network


            elif self.model.selected_circle.__class__.__name__ == 'Food':
                pass#print 'foooood'
            



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
        self.draw_sight = False # draw sight lines
        self.selected_circle = None # blob or food selected for display in the info box
        #self.sleep_time = .005 #seconds between frames

        # create food and blobs
        self.foods, self.blobs = [], []
        for i in range(0, FOOD_NUM):
            self.foods.append(Food(self))
        for i in range(0, BLOB_NUM):
            self.blobs.append(Blob(self))

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
            self.blobs.append(Blob(self, new_NN))


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

    model = Model(SCREEN_SIZE[0], SCREEN_SIZE[1])
    view = PyGameView(model, SCREEN_SIZE, INFO_BOX_SIZE)
    controller = PyGameKeyboardController()
    running = True

    while running:
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                # handle event can end pygame loop
                if not controller.handle_event(event):
                    running = False

        if not controller.paused:
            model.update()
        
        if model.show_gen:
            view.draw_simulation()
            view.draw_info_box()
            view.screen.blit(view.simulation_surface, (0,0))
            view.screen.blit(view.info_box_surface,   (SCREEN_SIZE[0],0))
            pygame.display.update()
            #time.sleep(model.sleep_time)


