import torch
import torch.nn as nn
import config


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, config.HIDDEN_LAYER_1)
        self.fc2 = nn.Linear(config.HIDDEN_LAYER_1, config.HIDDEN_LAYER_2)
        self.fc3 = nn.Linear(config.HIDDEN_LAYER_2, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
