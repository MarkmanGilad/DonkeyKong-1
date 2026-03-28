import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque
from DQN import DQN
from config import *

class DQN_Agent:
    def __init__(self):
        self.state_dim = STATE_DIM
        self.action_dim = ACTION_DIM
        
        # --- EXPLORATION ---
        self.epsilon = EPSILON_START
        self.epsilon_min = EPSILON_MIN
        
        # --- TRAINING HYPERPARAMETERS ---
        self.learning_rate = LEARNING_RATE
        self.gamma = GAMMA
        self.batch_size = BATCH_SIZE
        self.memory = deque(maxlen=MEMORY_SIZE)
        self.train_step_counter = 0

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # --- THE MAIN BRAIN ---
        self.model = DQN(self.state_dim, self.action_dim).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

        # --- THE TARGET NETWORK (Stability Hack) ---
        # This network doesn't train; it just copies the main network occasionally.
        self.target_model = DQN(self.state_dim, self.action_dim).to(self.device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval() # Set to evaluation mode

    def get_action(self, events, state):
        norm_state = state.clone().detach().float().to(self.device)
        # Normalize
        # for i in [1, 5, 6, 7, 9, 10]:
        #     norm_state[i] /= 1500.0

        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        else:
            with torch.no_grad():
                q_values = self.model(norm_state.unsqueeze(0))
                return torch.argmax(q_values).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def sample(self):
        batch = random.sample(self.memory, self.batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

        state_batch = torch.stack(state_batch).to(self.device)
        action_batch = torch.tensor(action_batch).to(self.device)
        reward_batch = torch.tensor(reward_batch, dtype=torch.float32).to(self.device)
        next_state_batch = torch.stack(next_state_batch).to(self.device)
        done_batch = torch.tensor(done_batch, dtype=torch.float32).to(self.device)

        return state_batch, action_batch, reward_batch, next_state_batch, done_batch

    def train(self):
        if len(self.memory) < self.batch_size:
            return None

        state_batch, action_batch, reward_batch, next_state_batch, done_batch = self.sample()

        # 1. Get current Q values from Main Network
        q_values = self.model(state_batch)
        q_value = q_values.gather(1, action_batch.unsqueeze(1)).squeeze(1)

        # 2. DDQN: Main network selects action, Target network evaluates it
        with torch.no_grad():
            best_actions = self.model(next_state_batch).argmax(1)
            next_q_value = self.target_model(next_state_batch).gather(1, best_actions.unsqueeze(1)).squeeze(1)

        expected_q_value = reward_batch + (self.gamma * next_q_value * (1 - done_batch))

        loss = self.criterion(q_value, expected_q_value)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
              

        # --- UPDATE TARGET NETWORK ---
        self.train_step_counter += 1
        if self.train_step_counter % TARGET_UPDATE_FREQ == 0:
            self.target_model.load_state_dict(self.model.state_dict())

        return loss.item()
