import numpy as np

from neural_network.activation_functions.SoftmaxActivationFunction import Softmax
from neural_network.loss_functions.LossCategoricalCrossEntropy import LossCategoricalCrossEntropy


class SoftmaxCrossEntropy:
    def __init__(self):
        self.dinputs = None

    def backward(self, dvalues, target_classes):
        samples = len(dvalues)

        if len(target_classes.shape) == 2:
            target_classes = np.argmax(target_classes, axis=1)

        self.dinputs = dvalues.copy()
        self.dinputs[range(samples), target_classes] -= 1
        self.dinputs = self.dinputs / samples
