import torch
import torch.nn as nn
import numpy as np

class DQN(nn.Module):
    def __init__(self, n_feat, n_hidden, n_actions, n_layers):
        """
        Args:
            n_feat (int): Number of input features.
            n_hidden (int): Number of nodes at each hidden layer.
            n_actions (int): Number of actions, i.e. output features.
            n_layers (int): Number of layers for our NN.
        """
        super(DQN, self).__init__()

        self.n_layers = n_layers

        self.input = nn.Sequential(
            nn.Linear(n_feat, n_hidden),
            nn.ReLU(),
        )
        self.hidden = nn.Sequential(
            nn.Linear(n_hidden, n_hidden),
            nn.ReLU()
        )
        self.output = nn.Linear(n_hidden, n_actions)



    def forward(self, x):
        """
        Args:
            x: Tensor of shape (batch_size, n_feat)

        Returns:
            Tensor of shape (batch_size, n_actions)
        """
        out = self.input(x)

        # Run through the hidden layers
        for i in range(self.n_layers):
            out = self.hidden(out)

        return self.output(out)
