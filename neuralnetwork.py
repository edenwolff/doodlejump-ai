import numpy as np
import random
import copy

class NeuralNet():
    def __init__(self, input, hidden, output):
        self.input = input
        self.hidden = hidden
        self.output = output
        self.weights1 = 2 * np.random.random((self.input, self.hidden)) - 1
        self.weights2 = 2 * np.random.random((self.hidden, self.output)) - 1
        self.bias1 = 2 * np.random.random((self.hidden)) - 1
        self.bias2 = 2 * np.random.random((self.output)) - 1

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def feedForward(self, inputs):
        inputs = np.asarray(inputs)
        hidden = self.sigmoid(np.dot(inputs, self.weights1) + self.bias1)
        output = self.sigmoid(np.dot(hidden, self.weights2) + self.bias2)
        return output

    def mutate(self, rate):   
        def mutation(val):
            if np.random.random() < rate:
                rand = random.gauss(0, 0.1) + val
                return max(min(rand, 1), -1)
            return val
        vmutate = np.vectorize(mutation)
        self.weights1 = vmutate(self.weights1)
        self.weights2 = vmutate(self.weights2)
        self.bias1 = vmutate(self.bias1)
        self.bias2 = vmutate(self.bias2)

    def clone(self):
        cloneBrain = NeuralNet(self.input, self.hidden, self.output)
        cloneBrain.weights1 = copy.deepcopy(self.weights1)
        cloneBrain.weights2 = copy.deepcopy(self.weights2)
        cloneBrain.bias1 = copy.deepcopy(self.bias1)
        cloneBrain.bias2 = copy.deepcopy(self.bias2)
        return cloneBrain
