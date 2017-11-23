# Evolutionary Neural Networks

## Synopsis

This program runs a simulation of a robots that use MLP neural networks (NN)
to survive and reproduce in the simulation.

## Motivation

The goal of this project was to try to train NNs to correctly
control robots to move around in their simulated environment to
eat food and reproduce, through the random mutations in
reproduction, instead of with supervized learning or another
form of NN training.

![results](https://github.com/PopeyedLocket/Evolutionary-Neural-Network/blob/master/videos_and_images/simulation_display.png?raw=true "Simulation"){:height="36px" width="36px"}
<img src="https://github.com/PopeyedLocket/Evolutionary-Neural-Network/blob/master/videos_and_images/simulation_display.png" width="100" height="100">

Each robot has its own Multi-Layer Perceptron NN:

![results](https://github.com/PopeyedLocket/Evolutionary-Neural-Network/blob/master/videos_and_images/nn_display.png?raw=true "MLP Neural Network")

The inputs of their NNs are: <br />
    Energy: how much energy this bot has <br />
    Left Eye RGB: how much red, green and blue the bot's left eye sees <br />
    Right Eye RGB: how much red, green and blue the bot's right eye sees <br />
    Sound: how much noise this bot hears, <br />
           the faster a bot move the more noise it makes, <br />
           the closer a bot is to other moving bots the louder <br />
           it hears that noise <br />
    Food Smell: how much food this bot smells, <br />
                the closer it is to food the greater this input is <br />
    Bot Smell: how much other bots this bot smells, <br />
                the closer it is to other bots the greater this input is <br />

The outputs of the NNs are:
    Left and right wheel rotation. 

This gives their NNs 10 input neurons and 2 output neurons.
Their NNs have one hidden layer of 88 neurons

![results](https://github.com/PopeyedLocket/Evolutionary-Neural-Network/blob/master/videos_and_images/vision_display.png?raw=true "Visual Input")

When a robot eats food, it creates another child robot
next to it. Its child will inherate its parent's color and
neural network weights with slight mutations. At the time of birth of
the child robot, whichever robot has currently eaten 
the least amount of food will be killed to maintain a constant
number of robots at a time. So the race is on to get food
as quickly as possible!

Each time a food is eaten, another food is created at a random
location, in order to maintain a constant number of food

Initially the weights of their brain are set to random 

## Installation

You will need pygame downloaded to run this program:
https://www.pygame.org/news

Once pygame is downloaded and this repository is cloned,
run the main.py file in the NN1 directory.

