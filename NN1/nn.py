import numpy as np
from constants import *
import random

# old NN - multi layer perceptron
class NN(object):
    """ 
    Represents the Neural Network of a bot 
    """

    def __init__(self, parents_NN=None):
        """ 
        intializes the neural network of a bot

        Args:
            parents_NN (list): list of neural networks (classes)
        """

        self.inputLayerSize  = INPUT_LAYER_SIZE
        self.hiddenLayerSize = HIDDEN_LAYER_SIZE
        self.outputLayerSize = OUTPUT_LAYER_SIZE

        self.hiddenLayer = [0] * self.hiddenLayerSize

        if parents_NN is not None:
            self.W1, self.W2 = self.get_recombine(parents_NN)

        else:

            self.W1 = np.random.uniform(-MAX_ABS_WEIGHT, MAX_ABS_WEIGHT, \
                (self.inputLayerSize, self.hiddenLayerSize))

            self.W2 = np.random.uniform(-MAX_ABS_WEIGHT, MAX_ABS_WEIGHT, \
                (self.hiddenLayerSize, self.outputLayerSize))

    def get_recombine(self, parents_NN):
        pw1, pw2 = parents_NN[1].W1, parents_NN[1].W2
        W1 = []
        for i in range(len(pw1)):
            W1.append([])
            for j in range(len(pw1[0])):
                W1[i].append(pw1[i][j] + np.random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT))
        W2 = []
        for i in range(len(pw2)):
            W2.append([])
            for j in range(len(pw2[0])):
                W2[i].append(pw2[i][j] + np.random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT))
        return W1, W2
    def get_recombine2(self, parents_NN):
        """ 
        Natural evolution isn't working.  When nn is passed in from bot.eat_food, it experiences no mutation.

        Args:
            parents_NN (list): list of neural networks (classes)
        """
        new_W_list = []

        list_ws = [(n[1].W1, n[1].W2) for n in parents_NN]

        for W_parents in zip(*list_ws):
            dim = W_parents[0].shape
 
            for w_par in W_parents:
                if w_par.shape != dim:
                    raise ValueError
            new_W = np.zeros(dim)
            for r in range(dim[0]):
                for c in range(dim[1]):
                    new_W[r][c] = random.choice(
                        [n[r][c] for n in W_parents]) + \
                        self.get_mutation()
            new_W_list.append(new_W)
        return tuple(new_W_list)

    def get_mutation(self):
        """
        decides whether or not mutation occurs using using values from
        constants

        Returns:
            the mutation amount to be added or no mutation
        """
        if np.random.rand() < MUTATION_RATE:
            return np.random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT)
        return 0

    def process(self, z1):
        """ 
        propigates the signal through the neural network.

        Args:
            z1 (array): array of neural network inputs

        Returns:
            list of outputs with post-processing. a3[0] refers to distance,
            a3[1] refers to angle
        """
        # input and output to level 2 (nodes)
        z2 = z1.dot(self.W1)
        a2 = self.sigmoid(z2)
        self.hiddenLayer = a2
        # input and output to level 3 (results)
        z3 = a2.dot(self.W2)
        a3 = self.sigmoid(z3)

        return [a3[0] * MAX_WHEEL_ROTATION, \
        a3[1] * MAX_WHEEL_ROTATION]

    def sigmoid(self, z):
        """ 
        applies sigmoid to matrix elementwise
        """
        # -.5 allows negative values for proper angle rotations
        return ((1/(1+np.exp(-z))) - .5)



# new NN - Damped Weighted Recurrent AND/OR Network
class NN2(object):

    def __init__(self, parents_NN=None):

        """ 
        intializes the neural network of a bot

        Args:
            parents_NN (list): list of neural networks (classes)
        """

        self.inputLayerSize  = INPUT_LAYER_SIZE
        self.hiddenLayerSize = HIDDEN_LAYER_SIZE
        self.outputLayerSize = OUTPUT_LAYER_SIZE
        self.hiddenLayer = [0] * self.hiddenLayerSize
        self.nodes = []


        if parents_NN is not None:
            parents_nn = parents_NN[1]
            for i in range(BRAIN_SIZE):
                self.nodes.append(Node(parents_nn.nodes[i]))
        
        else:
            for i in range(BRAIN_SIZE):
                n = Node()
                for j in range(CONNS):
                    if(np.random.uniform(0,1)<0.05): n.id[j]=0;
                    if(np.random.uniform(0,1)<0.05): n.id[j]=5;
                    if(np.random.uniform(0,1)<0.05): n.id[j]=12;
                    if(np.random.uniform(0,1)<0.05): n.id[j]=4;
                self.nodes.append(n)

    def process(self, z1):

        for i in range(INPUT_LAYER_SIZE):
            self.nodes[i].out = z1[i]

        for i in range(INPUT_LAYER_SIZE, BRAIN_SIZE):
            n = self.nodes[i]

            if n.type == 0: # AND node
                res = 1
                for j in range(CONNS):
                    idx = n.id[j]
                    val = self.nodes[idx].out
                    if n.notted[j]: val = 1 - val
                    res *= val
                res *= n.bias
                n.target = res

            else: # OR node
                res = 0
                for j in range(CONNS):
                    idx = n.id[j]
                    val = self.nodes[idx].out
                    if n.notted[j]: val = 1 - val
                    res += val*n.w[j]
                res += n.bias
                n.target = res

            if n.target < 0: n.target = 0
            if n.target > 1: n.target = 1
        
        # make all boxes go a bit toward target
        for i in range(INPUT_LAYER_SIZE, BRAIN_SIZE):
            n = self.nodes[i]
            n.out += (n.target - n.out)*n.kp

        # finally set the output to the last few nodes output
        out = []
        for i in range(OUTPUT_LAYER_SIZE):
            out.append(self.nodes[BRAIN_SIZE-1 - i].out)

        return out

# nodes of new NN
class Node(object):

    def __init__(self, parents_node=None):

        if parents_node == None:
            self.type = np.random.randint(0,2) # 0:AND, 1:OR
            self.kp = np.random.uniform(0.8,1.0)   # kp: damping strength
            self.w = np.random.uniform(0.1, 2, CONNS) # weight of each connecting box
            self.id = np.random.randint(0, BRAIN_SIZE, CONNS)  # id in boxes[] of the connecting box
            for i in range(CONNS):
                if np.random.uniform(0,1)<0.20: self.id[i] = np.random.uniform(0, INPUT_LAYER_SIZE) # 20% of the brain AT LEAST should connect to input
            self.notted = np.random.choice(a=[False, True], size=CONNS, p=[0.50, 1.00-0.50]) # is this input notted before coming in?
            self.bias = np.random.uniform(-1,1)
            self.out = 0
            self.target = 0

        else:

            # kp giggled
            self.kp = parents_node.kp
            if np.random.uniform(0,1) < 3*MUTATION_RATE:
               self.kp += np.random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT)
               if self.kp < 0.01: self.kp = 0.01
               if self.kp > 1.00: self.kp = 1.00

            self.w = []
            self.id = []
            self.notted = []
            for i in range(CONNS): # deep copy
                self.w.append(parents_node.w[i])
                self.id.append(parents_node.id[i])
                self.notted.append(parents_node.notted[i])

            # weight giggled
            if np.random.uniform(0,1) < 3*MUTATION_RATE:
                rc = np.random.randint(0, CONNS)
                self.w[rc] += np.random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT)
                if self.w[rc] < 0.01: self.w[rc] = 0.01
            
            # biased giggled
            self.bias = parents_node.bias
            if np.random.uniform(0,1) < 3*MUTATION_RATE:
                self.bias += np.random.uniform(-MUTATION_AMOUNT, MUTATION_AMOUNT)

            # connectivity changed
            if np.random.uniform(0,1) < MUTATION_RATE:
                rc = np.random.randint(0, CONNS)
                self.id[rc] = np.random.randint(0, BRAIN_SIZE)

            # notted flipped
            if np.random.uniform(0,1) < MUTATION_RATE:
                rc = np.random.randint(0, CONNS)
                self.notted[rc] = not self.notted[rc]

            # type flipped
            self.type = parents_node.type
            if np.random.uniform(0,1) < MUTATION_RATE:
                self.type = 1 - self.type


            self.bias = parents_node.bias
            self.out = 0
            self.target = 0
