import numpy as np
import pygame 
import sys
import time
from pygame.locals import *


''' NOTES:

	TO DO:

		SHORT TERM (now):



			set up robot class

				set up inputs and outputs of neural network and how to draw them
					inputs:
						some kind of rgb sight
						some kind of hearing
						a health bar
							decreases slowly over time
							the faster a robot moves, the faster their health decreases
							no movement has a base level rate of decrease though
							eating food increases health

					outputs:
						movement (wheeled) causes sound


				maybe make a special coordinate system that wraps around or something
				that will make sensory input calculations easier

					for sensory input, compare which x coordinate is larger:
						the x distance wrapping around or the x distance direct
						aka the up x distance or the down x distance
						(regardless of if up wraps and down is direct or vice versa)
						like wise for y distance
						pythagorean theorem of the shorter 2 will give the shortest 2d distance

			set up food class, node class



		MEDIUM TERM (later):



		LONG TERM (eventually):

			for now lets just make them all herbavors without the ability to harm one another
			
			then lets give them the ability to harm one another but they can't get any health from
			harming/killing one another

			then lets let them get health from killing eachother (aka they can eat eachother)

			then lets make it so the type of food that gave your parents health determines
			the type of food that gives you health to approx. the same degree


			maybe make its so that when you hover the mouse over the 
			screen it draws a circle
			if the user clicks on a robot in the circle, a window is 
			brought up that displays that robot's 
			neural network and the stimulation of each neuron
			maybe have another window too that plots some graphs of stuff
			b/c just seeing the network itself might not be that informative
			maybe make it so that if the mouse is hovered over a connection 
			in the network the weight of that connection is printed somewhere
			also make the NN display have thicker lines for stronger weights


	GEN IDEA:

		make an environment and organisms and food within it
		
		the organisms have sensory input, neural networks, can 
		die, have health, etc.

		see how their neural networks
		evolve to have the best survive


	SOURCES:

		gen idea:
		https://www.youtube.com/watch?v=GvEywP8t12I
		http://duncandhall.github.io/NaturalEvolution/implementation.html

		intro to neural networks:
		http://www.theprojectspot.com/tutorial-post/introduction-to-artificial-neural-networks-part-1/7

		useful for 2d graphics with pygame:
		https://www.pygame.org/docs/ref/draw.html

		most inspirational video if you're ever doubting yourself:
		https://www.youtube.com/watch?v=1lTcgSzf0AQ


	'''

############# GLOBAL VARIABLES ###################

# screen variables and setup
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
pygame.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Evolutionary Neural Networks")
screen.fill(BLACK)
surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
surface_position = (0,0)


##################################################


class Robot:

	def __init__(self, position, rotation):

		self.pos = position
		self.rot = rotation
		self.color = np.random.randint(256, size=3)
		self.body_radius = 8.0

		self.wheel_radius = 1.50
		self.axle_length = 1.0 * (2 * self.body_radius)
		self.left_wheel_rotation  = 0.0
		self.right_wheel_rotation = 0.0

		self.max_wheel_angular_velocity = np.pi / 564 # max pixel displacement per time step
		self.max_rotation = np.pi / 20

		self.eye_position = np.pi / 7 # angle from direction they're facing
		self.eye_peripheral_width = np.pi / 4 # angle from center of eye's vision to edge of peripheral
		self.max_visable_distance = 8 * self.body_radius # how far the eye can see
		self.left_eye_input  = {'r':0.0, 'g':0.0, 'b':0.0, 'p':0.0} # red, green, blue, proximity
		self.right_eye_input = {'r':0.0, 'g':0.0, 'b':0.0, 'p':0.0} # red, green, blue, proximity	

	def input_stimuli(self):
		
		# general variable setup
		x, y, r, theta = self.pos[0], self.pos[1], self.body_radius, self.rot
		

		# EYES

		# eye variable setup
		eye_sep = self.eye_position
		vis_dist = self.max_visable_distance
		periph_angle = self.eye_peripheral_width
		
		# reset input 
		self.left_eye_input['r'],  self.left_eye_input['g'],  self.left_eye_input['b']  = 0.0, 0.0, 0.0
		self.right_eye_input['r'], self.right_eye_input['g'], self.right_eye_input['b'] = 0.0, 0.0, 0.0

		# LEFT EYE
		
		# get left field of vision
		left_eye_pos = [x + r * np.cos(theta - eye_sep), y + r * np.sin(theta - eye_sep)]
		far_outer_left_peripheral = (left_eye_pos[0] + vis_dist * np.cos(theta - eye_sep - periph_angle), \
									 left_eye_pos[1] + vis_dist * np.sin(theta - eye_sep - periph_angle))
		far_inner_left_peripheral = (left_eye_pos[0] + vis_dist * np.cos(theta - eye_sep + periph_angle), \
									 left_eye_pos[1] + vis_dist * np.sin(theta - eye_sep + periph_angle))

		# draw left field of vision
		#pygame.draw.line(surface, WHITE, left_eye_pos, far_outer_left_peripheral)
		#pygame.draw.line(surface, WHITE, left_eye_pos, far_inner_left_peripheral)
		#pygame.draw.arc(surface, WHITE, \
		#	[left_eye_pos[0] - vis_dist, left_eye_pos[1] - vis_dist, 2 * vis_dist, 2 * vis_dist], \
		#	 -(theta - eye_sep + periph_angle), -(theta - eye_sep - periph_angle))
	
		# analysis left field of vision
		num_angles = 2 * r
		num_pts_per_ray = 2 * r
		angles = np.linspace((theta - eye_sep - periph_angle), (theta - eye_sep + periph_angle), num_angles)
		vis_depth = np.linspace(3.5 * r / 8, vis_dist, num_pts_per_ray)
		left_points = []
		for angle in angles:
			for i in vis_depth:
				px, py = left_eye_pos[0] + i * np.cos(angle), left_eye_pos[1] + i * np.sin(angle)
				if px > SCREEN_WIDTH: px -= SCREEN_WIDTH
				if px < 0: px += SCREEN_WIDTH
				if py > SCREEN_HEIGHT: py -= SCREEN_HEIGHT
				if py < 0: py += SCREEN_HEIGHT
				pixel_color = surface.get_at((int(px), int(py)))
				#print 'i = %d, angle = %f, px=%f, py=%f, pixel_color = %s' \
				#% (i, angle, px, py, pixel_color)
				px, py = int(px), int(py)
				left_points.append((px,py))
				if pixel_color != (0,0,0,255):
					self.left_eye_input['r'] += pixel_color[0]
					self.left_eye_input['g'] += pixel_color[1]
					self.left_eye_input['b'] += pixel_color[2]
					break

		self.left_eye_input['r'] /= (num_angles * 255)
		self.left_eye_input['g'] /= (num_angles * 255)
		self.left_eye_input['b'] /= (num_angles * 255)

		
		# RIGHT EYE
		right_eye_pos = (x + r * np.cos(theta + eye_sep), y + r * np.sin(theta + eye_sep))
		far_outer_right_peripheral = (right_eye_pos[0] + vis_dist * np.cos(theta + eye_sep - periph_angle), \
									  right_eye_pos[1] + vis_dist * np.sin(theta + eye_sep - periph_angle))
		far_inner_right_peripheral = (right_eye_pos[0] + vis_dist * np.cos(theta + eye_sep + periph_angle), \
									  right_eye_pos[1] + vis_dist * np.sin(theta + eye_sep + periph_angle))

		# draw field of vision
		#pygame.draw.line(surface, WHITE, right_eye_pos, far_outer_right_peripheral)
		#pygame.draw.line(surface, WHITE, right_eye_pos, far_inner_right_peripheral)
		#pygame.draw.arc(surface, WHITE, \
		#	[right_eye_pos[0] - vis_dist, right_eye_pos[1] - vis_dist, 2 * vis_dist, 2 * vis_dist], \
		#	 -(theta + eye_sep + periph_angle), -(theta + eye_sep - periph_angle))

		# analysis right field of vision
		angles = np.linspace((theta + eye_sep - periph_angle), (theta + eye_sep + periph_angle), num_angles)
		vis_depth = np.linspace(1.75 * r / 8, vis_dist, num_pts_per_ray)
		right_points = []
		for angle in angles:
			for i in vis_depth:
				px, py = right_eye_pos[0] + i * np.cos(angle), right_eye_pos[1] + i * np.sin(angle)
				if px > SCREEN_WIDTH: px -= SCREEN_WIDTH
				if px < 0: px += SCREEN_WIDTH
				if py > SCREEN_HEIGHT: py -= SCREEN_HEIGHT
				if py < 0: py += SCREEN_HEIGHT
				pixel_color = surface.get_at((int(px), int(py)))
				#print 'i = %d, angle = %f, px=%f, py=%f, pixel_color = %s' \
				#% (i, angle, px, py, pixel_color)
				px, py = int(px), int(py)
				right_points.append((px,py))
				if pixel_color != (0,0,0,255):
					self.right_eye_input['r'] += pixel_color[0]
					self.right_eye_input['g'] += pixel_color[1]
					self.right_eye_input['b'] += pixel_color[2]
					break

		self.right_eye_input['r'] /= (num_angles * 255)
		self.right_eye_input['g'] /= (num_angles * 255)
		self.right_eye_input['b'] /= (num_angles * 255)
		

		# draw points that were analyzed
		for pt in left_points:
			pygame.draw.circle(surface, [255,0,0], pt, 1)

		# draw points that were analyzed
		for pt in right_points:
			pygame.draw.circle(surface, [0,255,0], pt, 1)

	def print_input(self):
	
		print 'Eyes: L(r,g,b): (%.3f,%.3f,%.3f)\tR(r,g,b): (%.3f,%.3f,%.3f)' % ( \
		self.left_eye_input['r'],  self.left_eye_input['g'],  self.left_eye_input['b'], \
		self.right_eye_input['r'], self.right_eye_input['g'], self.right_eye_input['b'])


	def output_response(self):

		# randomly change wheel rotation
		self.left_wheel_rotation  += self.max_wheel_angular_velocity * (2 * np.random.rand() - 1)
		self.right_wheel_rotation += self.max_wheel_angular_velocity * (2 * np.random.rand() - 1)

		self.move_robot()

	def move_robot(self):

		x, y = self.pos
		theta = self.rot
		lwr = self.left_wheel_rotation
		rwr = self.right_wheel_rotation
		wr = self.wheel_radius
		al = self.axle_length

		if lwr == 0 or rwr == 0:

			if lwr == 0 and rwr != 0:
				
				sigma = rwr * wr / al
				new_x = x + (al / 2) * np.sin(sigma) * np.cos(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.sin(theta)
				new_y = y + (al / 2) * np.sin(sigma) * np.sin(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.cos(theta)
				if new_x > SCREEN_WIDTH: new_x -= SCREEN_WIDTH
				if new_x < 0: new_x += SCREEN_WIDTH
				if new_y > SCREEN_HEIGHT: new_y -= SCREEN_HEIGHT
				if new_y < 0: new_y += SCREEN_HEIGHT
				self.pos = (new_x, new_y)
				self.rot -= sigma

			elif lwr != 0 and rwr == 0:

				sigma = lwr * wr / al
				new_x = x + (al / 2) * np.sin(sigma) * np.cos(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.sin(theta)
				new_y = y + (al / 2) * np.sin(sigma) * np.sin(theta) + ((al / 2) * np.cos(sigma) - (al / 2)) * np.cos(theta)
				if new_x > SCREEN_WIDTH: new_x -= SCREEN_WIDTH
				if new_x < 0: new_x += SCREEN_WIDTH
				if new_y > SCREEN_HEIGHT: new_y -= SCREEN_HEIGHT
				if new_y < 0: new_y += SCREEN_HEIGHT
				self.pos = (new_x, new_y)
				self.rot += sigma
		
		elif lwr == rwr:
			
			# calculate and update new position (no change in rotation)
			distance_traveled = lwr * wr
			self.pos = (x + distance_traveled * np.cos(theta), \
						y + distance_traveled * np.sin(theta))

		else:

			# calculate change in position and rotation
			
			if lwr < rwr:
				radius_of_movement_from_inner_wheel = -al / ((rwr/lwr) - 1)
			elif lwr > rwr:
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
			#	(axle_of_movement_rotation_x + np.cos(-np.pi/2 + theta + angle_of_movement), \
			#	axle_of_movement_rotation_y + np.sin(-np.pi/2 + theta + angle_of_movement))
			
			# update new transform
			R = radius_of_movement_from_center
			sigma = angle_of_movement
			new_x = x + R * np.sin(sigma) * np.cos(theta) + (R * np.cos(sigma) - R) * np.sin(theta)
			new_y = y + R * np.sin(sigma) * np.sin(theta) + (R * np.cos(sigma) - R) * np.cos(theta)
			if new_x > SCREEN_WIDTH: new_x -= SCREEN_WIDTH
			if new_x < 0: new_x += SCREEN_WIDTH
			if new_y > SCREEN_HEIGHT: new_y -= SCREEN_HEIGHT
			if new_y < 0: new_y += SCREEN_HEIGHT
			self.pos = (new_x, new_y)
			self.rot += angle_of_movement

			# direction robot is facing
			#pygame.draw.line(surface, [255,0,0], \
			#[x + 200 * np.cos(theta), y + 200 * np.sin(theta)], [x,y])

	def draw_robot(self):
		
		self.draw_body()
		#self.draw_eyes()
		self.draw_tail()
	def draw_body(self):
		
		draw_circle(self.pos[0], self.pos[1], self.body_radius, self.color)
	def draw_tail(self):
		x, y, r, theta = self.pos[0], self.pos[1], self.body_radius, self.rot
		
		tail_width = np.pi / 3
		tail_tip = [x - 1.750 * r * np.cos(theta), y - 1.40 * r * np.sin(theta)]
		left_cheek = [ \
			x - 0.90 * r * np.cos(theta + tail_width), \
			y - 0.90 * r * np.sin(theta + tail_width)]
		right_cheek = [ \
			x - 0.90 * r * np.cos(theta - tail_width), \
			y - 0.90 * r * np.sin(theta - tail_width)]

		points = [left_cheek, tail_tip, right_cheek]

		draw_polygon(points, self.color)
	def draw_eyes(self):

		x, y, r, theta = self.pos[0], self.pos[1], self.body_radius, self.rot
		
		left_eye_pos  = (x + 0.70 * r * np.cos(theta - self.eye_position), \
						 y + 0.70 * r * np.sin(theta - self.eye_position))
		draw_circle(left_eye_pos[0], left_eye_pos[1], r / 8, WHITE)

		right_eye_pos = (x + 0.70 * r * np.cos(theta + self.eye_position), \
						 y + 0.70 * r * np.sin(theta + self.eye_position))
		draw_circle(right_eye_pos[0], right_eye_pos[1], r / 8, WHITE)

class Rock:

	pass

class Food:

	def __init__(self, position):

		self.pos = position
		self.radius = 5
		self.color = [0,200,0]

	def draw_food(self):

		draw_circle(self.pos[0], self.pos[1], self.radius, self.color)

class Node:

	pass


def draw_circle(x, y, r, color):

	x, y, r = int(x), int(y), int(r)

	# the circle is in left half
	if x < SCREEN_WIDTH / 2:

		# the circle is in top left
		if y < SCREEN_HEIGHT / 2:

			top_right_point    = (x + SCREEN_WIDTH, y                )
			bottom_right_point = (x + SCREEN_WIDTH, y + SCREEN_HEIGHT)
			bottom_left_point  = (x,                y + SCREEN_HEIGHT)
			pygame.draw.circle(surface, color, top_right_point,    r)
			pygame.draw.circle(surface, color, bottom_right_point, r)
			pygame.draw.circle(surface, color, bottom_left_point,  r)

		# else the circle is in the bottom left
		else:

			top_right_point    = (x + SCREEN_WIDTH, y - SCREEN_HEIGHT)
			top_left_point     = (x,                y - SCREEN_HEIGHT)
			bottom_right_point = (x + SCREEN_WIDTH, y                )
			pygame.draw.circle(surface, color, top_right_point,    r)
			pygame.draw.circle(surface, color, top_left_point,     r)
			pygame.draw.circle(surface, color, bottom_right_point, r)

	# else the circle is in the right half
	else:

		# the circle is in top right
		if y < SCREEN_HEIGHT / 2:

			top_left_point     = (x - SCREEN_WIDTH, y                )
			bottom_right_point = (x,                y + SCREEN_HEIGHT)
			bottom_left_point  = (x - SCREEN_WIDTH, y + SCREEN_HEIGHT)
			pygame.draw.circle(surface, color, top_left_point,     r)
			pygame.draw.circle(surface, color, bottom_right_point, r)
			pygame.draw.circle(surface, color, bottom_left_point,  r)

			
		# else the circle is in the bottom right
		else:

			top_right_point   = (x,                y - SCREEN_HEIGHT)
			top_left_point    = (x - SCREEN_WIDTH, y - SCREEN_HEIGHT)
			bottom_left_point = (x - SCREEN_WIDTH, y                )
			pygame.draw.circle(surface, color, top_right_point,   r)
			pygame.draw.circle(surface, color, top_left_point,    r)
			pygame.draw.circle(surface, color, bottom_left_point, r)


	# regardless of whether is crosses any borders or not were going to
	# draw it where it actually is at least once
	pygame.draw.circle(surface, color, (x, y), r)
def draw_polygon(points, color):

	x, y = points[0][0], points[0][1]

	# the polygon is in left half
	if x < SCREEN_WIDTH / 2:

		# the polygon is in top left
		if y < SCREEN_HEIGHT / 2:

			top_right_points, bottom_right_points, bottom_left_points = [], [], []
			for pt in points:
				top_right_points.append(    [pt[0] + SCREEN_WIDTH, pt[1]                ]  )
				bottom_right_points.append( [pt[0] + SCREEN_WIDTH, pt[1] + SCREEN_HEIGHT]  )
				bottom_left_points.append(  [pt[0],                pt[1] + SCREEN_HEIGHT]  )
			pygame.draw.polygon(surface, color, top_right_points     )
			pygame.draw.polygon(surface, color, bottom_right_points  )
			pygame.draw.polygon(surface, color, bottom_left_points   )

		# else the polygon is in the bottom left
		else:

			top_right_points, top_left_points, bottom_right_points = [], [], []
			for pt in points:
				top_right_points.append(    [pt[0] + SCREEN_WIDTH, pt[1] - SCREEN_HEIGHT]  )
				top_left_points.append(     [pt[0],                pt[1] - SCREEN_HEIGHT]  )
				bottom_right_points.append( [pt[0] + SCREEN_WIDTH, pt[1]                ]  )
			pygame.draw.polygon(surface, color, top_right_points)
			pygame.draw.polygon(surface, color, top_left_points)
			pygame.draw.polygon(surface, color, bottom_right_points)

	# else the polygon is in the right half
	else:

		# the polygon is in top right
		if y < SCREEN_HEIGHT / 2:

			top_left_points, bottom_right_points, bottom_left_points = [], [], []
			for pt in points:
				top_left_points.append(     [pt[0] - SCREEN_WIDTH, pt[1]                ]  )
				bottom_right_points.append( [pt[0],                pt[1] + SCREEN_HEIGHT]  )
				bottom_left_points.append(  [pt[0] - SCREEN_WIDTH, pt[1] + SCREEN_HEIGHT]  )
			pygame.draw.polygon(surface, color, top_left_points)
			pygame.draw.polygon(surface, color, bottom_right_points)
			pygame.draw.polygon(surface, color, bottom_left_points)

			

		# else the polygon is in the bottom right
		else:


			top_right_points, top_left_points, bottom_left_points = [], [], []
			for pt in points:
				top_right_points.append(    [pt[0],                pt[1] - SCREEN_HEIGHT]  )
				top_left_points.append(     [pt[0] - SCREEN_WIDTH, pt[1] - SCREEN_HEIGHT]  )
				bottom_left_points.append(  [pt[0] - SCREEN_WIDTH, pt[1]                ]  )
			pygame.draw.polygon(surface, color, top_right_points)
			pygame.draw.polygon(surface, color, top_left_points)
			pygame.draw.polygon(surface, color, bottom_left_points)


	# regardless of whether is crosses any borders or not were going to
	# draw it where it actually is at least once
	pygame.draw.polygon(surface, color, points)



def main(argv):

	

	# create a robot for testing
	r0 = Robot( \
		(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), np.pi / 1)
		#(SCREEN_WIDTH * np.random.rand(), \
		#SCREEN_HEIGHT * np.random.rand()), \
		#2 * np.pi * np.random.rand())

	# create a food for testing
	f0 = Food((SCREEN_WIDTH / 2 - 40, SCREEN_HEIGHT / 2))

	while True:

		# clear surface
		surface.fill(BLACK)
		
		# draw r0 on surface
		r0.draw_robot()

		# draw food on surface
		f0.draw_food()

		# update the sensory input of r0
		r0.input_stimuli()

		# do the response output of r0 to its input
		r0.output_response()

		# put surface on the screen and update the screen
		screen.blit(surface, surface_position)
		pygame.display.update()

if __name__ == "__main__":
	main(sys.argv[1:])

