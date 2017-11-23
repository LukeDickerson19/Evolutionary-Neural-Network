import numpy as np
import pygame

SCREEN_SIZE = (600, 400)
INFO_BOX_SIZE = (400, SCREEN_SIZE[1])
FOOD_NUM = 6
BOT_NUM = 6
NUM_PARENTS = 2
MUTATION_RATE = 0.001
MUTATION_AMOUNT = 0.02
MAX_ENERGY = 1000.0
ENERGY_LOSS_CONSTANT = .1

# bot constants
BOT_START_RADIUS = 5.0
BOT_MAX_RADIUS = 15.0
MAX_WHEEL_ROTATION = np.pi # max rotation a wheel can perform each time step
EYE_SEPARATION = np.pi / 7 # angle from direction they're facing
EYE_PERIPHERAL_WIDTH = np.pi / 3 # angle from center of eye's vision to edge of peripheral
VISION_OPAQUENESS = 25 # how opaque the view draws the arcs of the vision (0 to 255)
NOISE_AMPLIFIER = 20 # used to amplify how much noise a bot makes from its movement

# food constants
FOOD_START_RADIUS = 3.0
FOOD_GROWTH_RATE = 0.01 # change in radius per time step
FOOD_MAX_RADIUS = 12.0
FOOD_COLOR = pygame.Color('green')

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

