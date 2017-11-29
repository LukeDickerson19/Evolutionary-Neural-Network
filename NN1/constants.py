import numpy as np
import pygame

SCREEN_SIZE = (600, 400)
INFO_BOX_SIZE = (400, SCREEN_SIZE[1])
FOOD_NUM = 7
BOT_NUM = 6
NUM_PARENTS = 2
MUTATION_RATE = 0.001
MUTATION_AMOUNT = 0.02
MAX_ENERGY = 1000.0
ENERGY_LOSS_CONSTANT = .1

# additional BOT constants
BOT_BODY_RADIUS = 16
WHEEL_RADIUS = 1.50
AXLE_LENGTH = 1.0 * (2 * BOT_BODY_RADIUS)
MAX_WHEEL_ROTATION = np.pi # max rotation a wheel can perform each time step
EYE_SEPARATION = np.pi / 7 # angle from direction they're facing
EYE_PERIPHERAL_WIDTH = np.pi / 3 # angle from center of eye's vision to edge of peripheral
MAX_VISABLE_DISTANCE = 12 * BOT_BODY_RADIUS # how far the eye can see
VISION_OPAQUENESS = 25 # how opaque the view draws the arcs of the vision (0 to 255)
NOISE_AMPLIFIER = 20 # used to amplify how much noise a bot makes from its movement
BOT_BRIGHTNESS = 100 # minimum brightness of an r,g,b value of a bot's color

# additional food constants
FOOD_RADIUS = 8
FOOD_COLOR = pygame.Color('red')

# neural network constants
INPUT_LAYER_SIZE  = 10
HIDDEN_LAYER_SIZE = 88
OUTPUT_LAYER_SIZE = 2
BRAIN_SIZE = INPUT_LAYER_SIZE + HIDDEN_LAYER_SIZE + OUTPUT_LAYER_SIZE
CONNS = 3 # CONNS = the number of input connections for each node in the nn 
MAX_ABS_WEIGHT = 2 # maximum absolute value of the weight of a connection in the neural network


CONTROLS = [
    "Keyboard controls:",
    "    <space> = Pause/Play",
    "    d = Print NN weights to console",
    "    k = Kill all (new generation created)",
    "    s = Toggle simulation drawing",
    "    h = Toggle help",
    "    l = toggle left eye field of view of selected bot",
    "    r = toggle right eye field of view of selected bot"
]

KEY_INPUTS = [
	"E   = Energy",
	"LE = Left Eye",
	"RE = Right Eye",
	"H   = Hearing",
	"FS = Food Smell",
	"BS = BOT Smell"
]

KEY_OUTPUTS = [
	"RW = Right Wheel Rotation",
	"LW = Left Wheel Rotation"
]

