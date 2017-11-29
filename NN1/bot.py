from constants import *
from food import *
from abstract import ParentSprite
from nn import NN
import numpy as np
import math
import pygame


class Bot(ParentSprite):
    """ 
    Represents a bot in the natural/articifial evolution simulation
    """


    def __init__(self, model, col, nn=None, parent_x=None, parent_y=None, parent_angle=None):
        """ 
        Initialize bot by inheriting ParentSprite and assigning attributes

        Args:
            nn (class): can pass in the neural net from another bot
        """
        super(Bot, self).__init__() # values are not needed
        self.radius = BOT_BODY_RADIUS

        if parent_angle != None: self.angle = parent_angle
        else: self.angle = random.uniform(0,2*np.pi) # direction the bot is facing

        overlapped = True
        circles = model.bots + model.foods
        angle = self.angle - np.pi # direction its born relative to it parent
        angle2 = 0.0
        d_angle = np.pi / 20
        birth_distance = BOT_BODY_RADIUS * 3 # distance baby is born from parent
        while overlapped:
            if parent_x != None and parent_y != None:
                self.center_x = parent_x + birth_distance * np.cos(angle + angle2)
                self.center_y = parent_y + birth_distance * np.sin(angle + angle2)
                angle2 += d_angle
                if angle2 > 2*np.pi: parent_x = None
            else:
                self.center_x = random.randint(0, SCREEN_SIZE[0])
                self.center_y = random.randint(0, SCREEN_SIZE[1])
            overlapped = False
            for c in circles:
                if self.get_dist(c) < c.radius + self.radius:
                    overlapped = True
                    break
            if self.center_x > SCREEN_SIZE[0] or self.center_x < 0 or \
                self.center_y > SCREEN_SIZE[1] or self.center_y < 0:
                overlapped = True
        self.int_center = int(self.center_x), int(self.center_y)
        
        self.energy = MAX_ENERGY
        self.alive = True
        self.food_eaten = 0
        self.score_int = 0

        ######################

        self.color = col #np.random.randint(256, size=3)

        self.left_wheel_rotation  = 0.0
        self.right_wheel_rotation = 0.0

        # visual input variables
        self.eye_data = {'left_eye':{'pos':[0,0], 'left_peripheral': [0,0], 'right_peripheral': [0,0]}, 
                        'right_eye':{'pos':[0,0], 'left_peripheral': [0,0], 'right_peripheral': [0,0]}}
        self.visual_input = {'left_eye':[0.0, 0.0, 0.0],  # left eye:  red, green, blue
                            'right_eye':[0.0, 0.0, 0.0]}  # right eye: red, green, blue   
        self.left_arcs, self.right_arcs = [], [] # list of arcs of what the bot sees

        # smell input variables
        self.food_smell = 0.0 # the closer a piece of food is the closer food_smell will be to 1
        self.bot_smell = 0.0 # the closer a bot is the closer bot_smell will be to 1

        # sound input variables
        self.noise_made  = 0.0 # represents how much noise this bot is making
        self.noise_heard = 0.0 # represents how much noise the other bots are making

        self.input_list = []

        ######################

        ########## TEST VARIABLES ############

        # self.p_left  = (10,10)
        # self.p_right = (20,20)

        ######################################

        self.last_angle = .01 # IS THIS EVEN USED?

        #scoring related
        self.dist_moved = 0

        # Neural Network stuff here:
        if nn is not None:
            self.nn = NN(parents_NN=nn)
        else:
            self.nn = NN()


    ###################### INPUT ##############################

    # update the inputs of the nn w/ the current data
    def update_inputs(self, model, controller):
        
        self.update_sight(model, controller)
        self.update_hearing(model)
        self.update_smell(model)
        #if self == model.selected_circle: self.print_input()
    def print_input(self):
        self.print_energy()
        self.print_sight()
        self.print_hearing()
        self.print_smell()
        print ''

    # input sight
    def update_sight(self, model, controller):


        # LEFT EYE
        # get left field of vision
        self.update_eye_data('left_eye')

        # get the arcs in the left field of view
        self.left_arcs = self.update_visual_field(model.bots + model.foods, 'left_eye', controller)
        
        # get rgb for left eye
        self.update_eye_rgb(self.left_arcs, 'left_eye')


        # RIGHT EYE
        # get left field of vision
        self.update_eye_data('right_eye')

        # get the arcs in the right field of view
        self.right_arcs = self.update_visual_field(model.bots + model.foods, 'right_eye', controller)
        
        # get rgb for right eye
        self.update_eye_rgb(self.right_arcs, 'right_eye')
    def update_eye_data(self, eye):
        """
        this function finds the x,y position of the 
        eye itself, and the far left and right points
        of its peripheral vision
        """

        # general variable setup
        x, y, r, theta = self.center_x, self.center_y, self.radius, self.angle
        
        # eye variable setup
        eye_sep = EYE_SEPARATION
        vis_dist = MAX_VISABLE_DISTANCE
        periph_angle = EYE_PERIPHERAL_WIDTH
        
        if eye == 'left_eye': e = -1
        else: e = 1 # right eye
        eye_pos = [x + r * np.cos(theta + e*eye_sep), y + r * np.sin(theta +e*eye_sep)]
        self.eye_data[eye]['pos'] = (eye_pos[0], eye_pos[1])
        self.eye_data[eye]['left_peripheral'] = \
            (eye_pos[0] + vis_dist * np.cos(theta + e*eye_sep - periph_angle), \
             eye_pos[1] + vis_dist * np.sin(theta + e*eye_sep - periph_angle))
        self.eye_data[eye]['right_peripheral'] = \
            (eye_pos[0] + vis_dist * np.cos(theta + e*eye_sep + periph_angle), \
             eye_pos[1] + vis_dist * np.sin(theta + e*eye_sep + periph_angle))
    def update_visual_field(self, circles, eye, controller):
        """
        this function finds the objects that are in 
        the bot's field of view and then creates and
        returns a list of the arcs of those objects 
        that the bot sees
        """

        eye_pos = self.eye_data[eye]['pos']
        left_peripheral = self.eye_data[eye]['left_peripheral'] 
        right_peripheral = self.eye_data[eye]['right_peripheral']

        arcs = [{ # start with just 1 empty field of vision
        'left_side':left_peripheral, # left_side = the point on the 
        'right_side':right_peripheral,
        'd':MAX_VISABLE_DISTANCE, # distance from eye to arc
        'color':[255,255,255,VISION_OPAQUENESS], # opaque white
        'circle':None # if the arc represents empty space or a circle
        }]

        # print '\n%s' % self

        for c in circles:

            if c == self: continue

            cx, cy, cr = c.center_x, c.center_y, c.radius
            self.f = (int(cx), int(cy))
            ex, ey = eye_pos[0], eye_pos[1]

            # d = distance from eye_pos to center of c
            dx, dy = cx - ex, cy - ey
            d = np.sqrt(dx**2 + dy**2)

            # if its within the bot's vision
            if d - cr <= MAX_VISABLE_DISTANCE:

                # p_left = the point on the edge of circle c that is
                # forms a line tangent to c when connected to eye_pos.
                # p_left is on the left edge of the circle when viewed from eye_pos
                a = np.arctan2(dy,dx) # a = angle between horizontal line and line from eye_pos to c                    
                a2 = np.arcsin(cr/d) # a2 = angle between line from eye_pos to c and line from eye_pos to p_left
                d2 = np.sqrt(d**2 - cr**2) # d2 = distance from eye_pos to p_left
                # if the circle c is just barely on the outside of the max_visable_distane
                if d2 > MAX_VISABLE_DISTANCE:
                    d2 = MAX_VISABLE_DISTANCE
                    a2 = np.arccos((d2**2 + d**2 - cr**2)/(2*d2*d))
                p_left = (ex + d2*np.cos(a-a2), ey + d2*np.sin(a-a2))
                
                # if p_left is on the left side of right periferal
                if self.left_side(eye_pos, right_peripheral, p_left):

                    #self.p_left  = (int(p_left[0]),  int(p_left[1])) # FOR TESTING PURPOSES 

                    # p_right = the point on the edge of circle c that is
                    # forms a line tangent to c when connected to eye_pos.
                    # p_right is on the right edge of the circle when viewed from eye_pos
                    p_right = (ex + d2*np.cos(a+a2), ey + d2*np.sin(a+a2))

                    # if p_right is on the right side of left periferal
                    if self.right_side(eye_pos, left_peripheral, p_right):

                        # IF WE'VE GOTTEN TO THIS POINT THEN THE CIRCLE c 
                        # IS IN THE VISUAL FIELD OF THE eye
                        #print '%s is in visual field' % c

                        col = [c.color[0], c.color[1], c.color[2], VISION_OPAQUENESS]
                        first_arc, last_arc = True, False # first and last arc in the iteration
                        original_arcs = []
                        for a in arcs: original_arcs.append(a)
                        i = -1
                        for a in original_arcs:

                            i += 1
                            #print 'i=%d, len(arcs)=%d' % (i, len(arcs))
                            #if arcs[i]['color'] == col and arcs[i]['d'] == d2: i += 1
                            try:
                                
                                if arcs[i]['circle'] == c: i += 1
                                
                                if first_arc and i > 0: first_arc = False
                                if i == len(original_arcs)-1: last_arc = True

                                a_left, a_right = a['left_side'], a['right_side']

                                LPLL = self.left_side(eye_pos, a_left, p_left)
                                LPRL = not LPLL
                                LPLR = self.left_side(eye_pos, a_right, p_left)
                                LPRR = not LPLR
                                RPLL = self.left_side(eye_pos, a_left, p_right)
                                RPRL = not RPLL
                                RPLR = self.left_side(eye_pos, a_right, p_right)
                                RPRR = not RPLR

                                a_d = a['d']
                                closer = d - cr < a_d

                                if closer:
                                    #print '%s is closer than arc[%d]:%s' % (col, i, arcs[i]['color'])
                                    #print 'LPLL=%s, LPRL=%s, LPLR=%s, LPRR=%s, RPLL=%s, RPRL=%s, RPLR=%s, RPRR=%s' \
                                    #% (LPLL, LPRL, LPLR, LPRR, RPLL, RPRL, RPLR, RPRR)

                                    if LPLL and RPLL or LPRR and RPRR:
                                        # senario where none of arc a is not overlapped by c
                                        #print '%s none of arc[%d]:%s' % (col, i, arcs[i]['color'])
                                        pass

                                    elif LPRL and LPLR and RPRR:
                                        # senario where the right side of arc a is overlapped by c
                                        #print '%s right of arc[%d]:%s' % (col, i, arcs[i]['color'])

                                        # so move arc a's right side in
                                        arcs[i]['right_side'] = p_left

                                        # and insert it starting at the right side of arc a
                                        arcs.insert(i+1, {
                                            'left_side':p_left,
                                            'right_side':a_right,
                                            'd':d2,
                                            'color':col,
                                            'circle':c
                                        })


                                    elif LPRL and LPLR and RPRL and RPLR:
                                        # senario where the middle of arc a is overlapped by c
                                        #print '%s middle of arc[%d]:%s' % (col, i, arcs[i]['color'])

                                        # so put c in the middle
                                        arcs[i]['right_side'] = p_left
                                        arcs.insert(i+1, {
                                            'left_side':p_left,
                                            'right_side':p_right,
                                            'd':d2,
                                            'color':col,
                                            'circle':c
                                        })
                                        arcs.insert(i+2, {
                                            'left_side':p_right,
                                            'right_side':a_right,
                                            'd':a_d,
                                            'color':arcs[i]['color'],
                                            'circle':arcs[i]['circle']
                                        })

                                    elif LPLL and RPRL and RPLR:
                                        # senario where the left side of arc a is overlapped by c
                                        #print '%s left of arc[%d]:%s' % (col, i, arcs[i]['color'])

                                        # so move arc a's left side in
                                        arcs[i]['left_side'] = p_right

                                        # if arc a is not the first arc and 
                                        # the previous arc is from the same circle
                                        if not first_arc and arcs[i-1]['circle'] == c:

                                            # then this is a continuation of the previous arc
                                            # so just update its right side
                                            arcs[i-1]['right_side'] = p_right

                                        # else, this is a new arc
                                        else:

                                            # so insert it starting at the left side of arc a
                                            arcs.insert(i+1, {
                                                'left_side':a_left,
                                                'right_side':p_right,
                                                'd':d2,
                                                'color':col,
                                                'circle':c
                                            })


                                    elif LPLL and RPRR:
                                        # senario where all of arc a is overlapped by c
                                        #print '%s all of arc[%d]:%s' % (col, i, arcs[i]['color'])

                                        # if arc a is not the first arc and 
                                        # the previous arc is from the same circle
                                        if not first_arc and arcs[i-1]['circle'] == c:

                                            # then this is a continuation of the previous arc
                                            # so just update its right side
                                            arcs[i-1]['right_side'] = a_right
                                            
                                            # and remove this arc
                                            del arcs[i]
                                            i -= 1

                                        # else, this is a new arc
                                        else:
                                            arcs[i]['d'] = d2
                                            arcs[i]['color'] = col
                                            arcs[i]['circle'] = c

                            except Exception:
                                print 'i=%d, len(arcs)=%d\neye = %s, bot = %s\n' % (i, len(arcs), eye, self)
                                controller.paused = True

        #for a in arcs: print a
        #print ''
        return arcs
    def update_eye_rgb(self, arcs_in_view, eye):
        """
        this function uses the list of arcs of what the bot's eye sees
        do determine the percentage of the visual field that each 
        color r,g, and b take up
        """

        x, y, r = self.center_x, self.center_y, self.radius
        theta, eye_sep = self.angle, EYE_SEPARATION
        if eye == 'left_eye':
            ex, ey = x + r * np.cos(theta - eye_sep), y + r * np.sin(theta - eye_sep)
        else:
            ex, ey = x + r * np.cos(theta + eye_sep), y + r * np.sin(theta + eye_sep)

        total_angle = 2 * EYE_PERIPHERAL_WIDTH # all of visual field
                    
        r,g,b = 0.0,0.0,0.0
        for a in arcs_in_view:

            if a['circle'] != None:

                left_angle  = np.arctan2(ey - a['left_side'][1],  ex - a['left_side'][0])
                right_angle = np.arctan2(ey - a['right_side'][1], ex - a['right_side'][0])
                if left_angle > 0 and right_angle < 0: right_angle += 2*np.pi
                arc_angle = abs(left_angle - right_angle)

                r += (a['color'][0] / 255.0) * (arc_angle / total_angle)
                g += (a['color'][1] / 255.0) * (arc_angle / total_angle)
                b += (a['color'][2] / 255.0) * (arc_angle / total_angle)

        self.visual_input[eye] = [self.eye_sigmoid(r), self.eye_sigmoid(g), self.eye_sigmoid(b)]
    def eye_sigmoid(self, x):
        # this is used to increase brain activity when a bot sees something
        A = 7 # this constant controls how much the signal (x, values 0 to 1) is amplified by the sigmoid
        return 2*(1/(1+np.exp(-A*x)))-1.0
    def left_side(self, A, B, C):
    
        # determine if point C is on the left side
        # of line AB from point A's perspective

        # sign((Bx - Ax) * (y - Ay) - (By - Ay) * (x - Ax))
        # + if (x,y) is to the left of line AB, from pt A's perspective,
        # 0 if on the line, and - if to the right

        # its weird, bc when testing it with an arbitrary line and point\
        # + is left, and - is right, but in the simulation it catches it
        # properly when its flipped

        return (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0]) <= 0
    def right_side(self, A, B, C):

        # sign((Bx - Ax) * (y - Ay) - (By - Ay) * (x - Ax))
        # + if (x,y) is to the left of line AB, from pt A's perspective,
        # 0 if on the line, and - if to the right

        return (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0]) >= 0
    def print_sight(self):
        print 'Eyes:\tLeft RGB: [%.3f, %.3f, %.3f] Right RGB: [%.3f, %.3f, %.3f]' \
         % (self.visual_input['left_eye'][0], \
            self.visual_input['left_eye'][1], \
            self.visual_input['left_eye'][2], \
            self.visual_input['right_eye'][0], \
            self.visual_input['right_eye'][1], \
            self.visual_input['right_eye'][2])

    # input hearing
    def update_hearing(self, model):

        noise_heard = 0.0
        for bot in model.bots:
            if self != bot:
                #if self == model.selected_circle:
                #    print 'noise_made = %.3f\tget_dist = %.3f\tnoise_heard = %.3f' \
                #    % (bot.noise_made, self.get_dist(bot), bot.noise_made/self.get_dist(bot))
                noise_heard += (bot.noise_made / self.get_dist(bot))

        # sqash it (think of it as a max volume pervievable)
        self.noise_heard = 2 / (1 + np.exp(-4*noise_heard)) - 1 
    def print_hearing(self):
        
        print 'Ears:\t%.3f' % self.noise_heard
        
    # input smell
    def update_smell(self, model):

        bot_smell = 0.0
        for bot in model.bots:
            if bot != self:
               bot_smell += \
                (-2 / (1 + np.exp(-(2 * self.get_dist(bot)) / (3*BOT_BODY_RADIUS))) + 2)
        self.bot_smell = 2 / (1 + np.exp(-4*bot_smell)) - 1 # sqash it

        food_smell = 0.0
        for food in model.foods:
            food_smell += \
            (-4 / (1 + np.exp(-(2 * self.get_dist(food)) / (3*BOT_BODY_RADIUS))) + 4)
        self.food_smell = 2 / (1 + np.exp(-4*food_smell)) - 1 # sqash it
    def print_smell(self):
        
        print 'Nose:\tbot Smell: %.3f\tFood Smell: %.3f' \
         % (self.bot_smell, self.food_smell)

    # update energy
    def update_energy(self, model, velocity, angular_velocity):
        """ 
        updates self.energy of a bot based on the distance it moves and an 
        energy loss constant

        Args:
            model (object): contains attributes of the environment
            velocity (float): the distance the bot will move
            angular_velocity (float): the angle the bot will change
        """
        #subtract evergy based on distance moved
        self.energy -= (np.abs(velocity) + np.abs(angular_velocity) + ENERGY_LOSS_CONSTANT)
        if self.energy < 0:
            self.alive = False
            #if model.selected_circle == self:
            #    model.selected_circle == None
            self.score_int = self.score()
            model.vip_genes.append((self.score_int, self.nn, self.color))

            model.bots.remove(self)
    def print_energy(self):
        
        print 'Energy:\t%.3f' % self.energy

    ############################################################

    ###################### OUTPUT ##############################

    def update_outputs(self, model):
        """ 
        Update the bot's output, aka nn response to inputs
        """

        # get current wheel rotations based on neural network
        [self.left_wheel_rotation, self.right_wheel_rotation] = self.process_neural_net()
        #if self == model.selected_circle: self.print_output()

        # update position and energy level based on neural network output
        old_pos   = (self.center_x, self.center_y)
        old_angle = self.angle
        self.update_transform(model)
        new_pos   = (self.center_x, self.center_y)
        new_angle = self.angle
        displacement = math.sqrt((new_pos[0] - old_pos[0]) ** 2 + (new_pos[1] - new_pos[1]) ** 2)
        angular_displacement = new_angle - old_angle
        self.update_noise_made(displacement, angular_displacement)
        self.update_energy(model, displacement, angular_displacement)

        # interact with food objects
        self.eat_food(model)

    # update position and orientation
    def update_transform(self, model):

        x, y = self.center_x, self.center_y
        theta = self.angle
        lwr = self.left_wheel_rotation
        rwr = self.right_wheel_rotation
        wr = WHEEL_RADIUS
        al = AXLE_LENGTH

        if lwr == 0 or rwr == 0:

            if lwr == 0 and rwr != 0:
                
                sigma = rwr * wr / al
                new_x = x + (al / 2) * np.sin(sigma) * np.cos(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.sin(theta)
                new_y = y + (al / 2) * np.sin(sigma) * np.sin(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.cos(theta)
                self.center_x, self.center_y = new_x, new_y
                self.int_center = int(self.center_x), int(self.center_y)
                self.angle -= sigma
                self.out_of_bounds()

            elif lwr != 0 and rwr == 0:

                sigma = lwr * wr / al
                new_x = x + (al / 2) * np.sin(sigma) * np.cos(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.sin(theta)
                new_y = y + (al / 2) * np.sin(sigma) * np.sin(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.cos(theta)
                self.center_x, self.center_y = new_x, new_y
                self.int_center = int(self.center_x), int(self.center_y)
                self.angle += sigma
                self.out_of_bounds()
        
        elif lwr == rwr:
            
            # calculate and update new position (no change in rotation)
            distance_traveled = lwr * wr
            self.center_x, self.center_y = \
                x + distance_traveled * np.cos(theta), \
                y + distance_traveled * np.sin(theta)
            self.int_center = int(self.center_x), int(self.center_y)

        else:

            # calculate change in position and rotation
            
            if lwr < rwr:
                radius_of_movement_from_inner_wheel = -al / ((rwr/lwr) - 1)
            else:#if lwr > rwr:
                radius_of_movement_from_inner_wheel = al / ((lwr/rwr) - 1)

            #print "radius_of_movement_from_inner_wheel:%f" % radius_of_movement_from_inner_wheel
            angle_of_movement = lwr * wr / radius_of_movement_from_inner_wheel

            if radius_of_movement_from_inner_wheel > 0:
                radius_of_movement_from_center = radius_of_movement_from_inner_wheel + al / 2
            else:
                radius_of_movement_from_center = radius_of_movement_from_inner_wheel - al / 2

            #print "radius_of_movement_from_center:%f" % radius_of_movement_from_center
            axle_of_movement_rotation_x = x - radius_of_movement_from_center * np.sin(theta)
            axle_of_movement_rotation_y = y + radius_of_movement_from_center * np.cos(theta)

            #print "old(x,y) = (%f,%f)" % (x, y)
            #print "radius_of_movement_from_center * np.sin(theta) = %f" % (radius_of_movement_from_center * np.sin(theta))
            #print "radius_of_movement_from_center * np.cos(theta) = %f" % (radius_of_movement_from_center * np.cos(theta))

            # axle of rotation
            #pygame.draw.line(surface, [255,0,0], \
            #[axle_of_movement_rotation_x, axle_of_movement_rotation_y], [x,y])

            #print "new(x,y) = (%f,%f)" % \
            #   (axle_of_movement_rotation_x + np.cos(-np.pi/2 + theta + angle_of_movement), \
            #   axle_of_movement_rotation_y + np.sin(-np.pi/2 + theta + angle_of_movement))

            R = radius_of_movement_from_center
            sigma = angle_of_movement
            new_x = x + R * np.sin(sigma) * np.cos(theta) + (R * np.cos(sigma) - R) * np.sin(theta)
            new_y = y + R * np.sin(sigma) * np.sin(theta) + (R * np.cos(sigma) - R) * np.cos(theta)
    
            # check if the new position overlaps with any other bots        
            overlaps_with_another_bot = False
            for b in model.bots:
                if b != self:
                    dist = np.sqrt((new_x - b.center_x)**2 + (new_y - b.center_y)**2)
                    if dist <= 2 * BOT_BODY_RADIUS:
                        overlaps_with_another_bot = True
                        break

            # # if there is an overlap
            # if overlaps_with_another_bot:

            #     # reverse its change in position
            #     new_x, new_y = 2*self.center_x - new_x, 2*self.center_y - new_y

            # # don't let bots go out of bounds
            # if new_x > SCREEN_SIZE[0]: new_x = SCREEN_SIZE[0]
            # if new_x < 0: new_x = 0
            # if new_y > SCREEN_SIZE[1]: new_y = SCREEN_SIZE[1]
            # if new_y < 0: new_y = 0

            # infinite environment
            if new_x > SCREEN_SIZE[0]: new_x = 0
            if new_x < 0: new_x = SCREEN_SIZE[0]
            if new_y > SCREEN_SIZE[1]: new_y = 0
            if new_y < 0: new_y = SCREEN_SIZE[1]

            # update new transform
            if not math.isnan(new_x) and not math.isnan(new_y):
                self.center_x, self.center_y = new_x, new_y
                self.int_center = int(self.center_x), int(self.center_y)
            self.angle += angle_of_movement
            self.out_of_bounds()

            # mx, my = pygame.mouse.get_pos()
            # if mx != SCREEN_SIZE[0]/2:
            #     a = np.arctan(float(my - SCREEN_SIZE[1]/2) / (mx - SCREEN_SIZE[0]/2))
            #     if mx > SCREEN_SIZE[0]/2:
            #         a -= np.pi
            # else:
            #     if my > SCREEN_SIZE[1]/2:
            #         a = -np.pi / 2
            #     else: a = np.pi / 2
            # self.center_x, self.center_y = mx, my
            # self.int_center = int(self.center_x), int(self.center_y)
            #self.angle = a
            #self.out_of_bounds()
            

            # draw direction robot is facing
            #pygame.draw.line(surface, [255,0,0], \
            #[x + 200 * np.cos(theta), y + 200 * np.sin(theta)], [x,y])

    # updat ehow much noise this bot is makeing from its
    # translational and angular displacements
    def update_noise_made(self, displacement, angular_displacement):

        self.noise_made = NOISE_AMPLIFIER * \
        np.abs(displacement) + np.abs(angular_displacement)

    def process_neural_net(self):
        """
        use bot's neural network to determine wheel rotation

        Returns:
            list containing distance and angle magnitudes
        """
        #assign binary inputs if the bot can see a food or bot object
        #bot_target_input = 0 if self.target_bot == self else 1 
        #food_target_input = 0 if self.target_food == self else 1

        #create array containing neural net inputs
        self.input_list = np.array( \
            [self.energy / MAX_ENERGY] + \
            self.visual_input['left_eye'] + \
            self.visual_input['right_eye'] + \
            [self.noise_heard, self.food_smell, self.bot_smell])

        return self.nn.process(self.input_list)
    def print_output(self):
        self.print_wheel_rotation()
        print ''

    def print_wheel_rotation(self):
        print 'Wheels:\tL = %.3f rad. = %.3f deg.\tR = %.3f rad. = %.3f deg.' % \
        (self.left_wheel_rotation,  180*self.left_wheel_rotation/np.pi, \
         self.right_wheel_rotation, 180*self.right_wheel_rotation/np.pi)

    def eat_food(self, model):
        """ 
        tests whether or not a bot eats food on a given frame. If a bot 
        eats food, remove the food, increase the bot's energy, asexually 
        reproduce based on its neural net dna, and do some population control.

        Args:
            model (object): contains attributes of the environment

        """
        for i in range(len(model.foods)-1, -1, -1):
            if self.intersect(model.foods[i]):
                self.food_eaten += 1
                self.energy += 500

                if self.energy > MAX_ENERGY:
                    self.energy = MAX_ENERGY

                # delete this food
                del model.foods[i]

                # create another food 
                model.foods.append(Food(model))

                # create another bot with a similar nn
                self.reproduce_asexually(model)

                # kill lowest energy bot if there are more than BOT_NUM bots
                if len(model.bots) > BOT_NUM:
                    energy_list = []
                    for bot in model.bots:
                        energy_list.append(bot.energy)
                    del model.bots[np.argmin(energy_list)]

    ############################################################

    ###################### OTHER ###############################

    def reproduce_asexually(self, model):

        new_col = [0] * 3
        for i in range(1,3):
            change_in_rgb = np.random.normal(0, 10)
            if change_in_rgb > 50:  change_in_rgb = 50
            if change_in_rgb < -50: change_in_rgb = -50
            new_c = self.color[i] + change_in_rgb
            if new_c > 255: new_c = 255
            if new_c < BOT_BRIGHTNESS: new_c = BOT_BRIGHTNESS
            new_col[i] = int(new_c)

        model.bots.append(Bot(model, new_col, (1, self.nn, new_col), self.center_x, self.center_y))

    def score(self):
        """
        gives a bot's score based on: self.food_eaten

        Returns:
            the score of the bot
        """
        return self.food_eaten

    def out_of_bounds(self):
        """ 
        updates self.angle so it is always between -2pi and +2pi
        """

        if self.angle > 2 * np.pi:
            self.angle = self.angle % (2 * np.pi)
        if self.angle < -2 * np.pi:
            self.angle = -self.angle % (2 * np.pi)

    ############################################################

