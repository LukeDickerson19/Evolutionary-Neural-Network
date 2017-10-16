import numpy as np
import pygame

SCREEN_SIZE = (800, 500)
FOOD_NUM = 7
BLOB_NUM = 10
NUM_PARENTS = 2
MUTATION_RATE = 0.2
MUTATION_AMOUNT = 0.05
MAX_ENERGY = 1000
ENERGY_LOSS_CONSTANT = .1

# additional blob constants
BLOB_BODY_RADIUS = 15
WHEEL_RADIUS = 1.50
AXLE_LENGTH = 1.0 * (2 * BLOB_BODY_RADIUS)
MAX_WHEEL_ANGULAR_VELOCITY = np.pi / 564 # max
EYE_SEPARATION = np.pi / 7 # angle from direction they're facing
EYE_PERIPHERAL_WIDTH = np.pi / 4 # angle from center of eye's vision to edge of peripheral
MAX_VISABLE_DISTANCE = 8 * BLOB_BODY_RADIUS # how far the eye can see
VISION_OPAQUENESS = 25 # how opaque the view draws the arcs of the vision (0 to 255)

# additional food constants
FOOD_RADIUS = 5
FOOD_COLOR = pygame.Color('orange')


CONTROLS = [
    "Keyboard controls:",
    "    <space> = Pause/Play",
    "    d = Print NN weights to console",
    "    k = Kill all (new generation created)",
    "    s = Toggle simulation drawing",
    "    . = Speed up simulation",
    "    , = Slow down simulation",
    "    h = Toggle help",
    "    a = Toggle sight"
]
