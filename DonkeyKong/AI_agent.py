import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQN_Agent:
    def __init__(self):
        self.state_dim = 11
        self.action_dim = 8
        
        # --- EXPLORATION ---
        self.epsilon = 1.0
        self.epsilon_min = 0.05
        #decay for quick test:
        #self.epsilon_decay = 0.985 # Decay slower (let it explore more)
        #dcay for actual training:
        self.epsilon_decay = 0.9995
        
        # --- TRAINING HYPERPARAMETERS ---
        self.learning_rate = 0.001  # Increased (safe because of Target Network)
        self.gamma = 0.99
        self.batch_size = 64
        self.memory = deque(maxlen=50000)
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

    def train(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

        state_batch = torch.stack(state_batch).to(self.device)
        action_batch = torch.tensor(action_batch).to(self.device)
        reward_batch = torch.tensor(reward_batch, dtype=torch.float32).to(self.device)
        next_state_batch = torch.stack(next_state_batch).to(self.device)
        done_batch = torch.tensor(done_batch, dtype=torch.float32).to(self.device)

        # Normalize batches
        for i in [1, 5, 6, 7, 9, 10]:
            state_batch[:, i] /= 1500.0
            next_state_batch[:, i] /= 1500.0

        # 1. Get current Q values from Main Network
        q_values = self.model(state_batch)
        q_value = q_values.gather(1, action_batch.unsqueeze(1)).squeeze(1)

        # 2. Get next Q values from TARGET Network (More stable!)
        with torch.no_grad():
            next_q_values = self.target_model(next_state_batch)
            next_q_value = next_q_values.max(1)[0]

        expected_q_value = reward_batch + (self.gamma * next_q_value * (1 - done_batch))

        loss = self.criterion(q_value, expected_q_value)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update epsilon
        # if self.epsilon > self.epsilon_min:
        #     self.epsilon *= self.epsilon_decay
            
        if self.train_step_counter % 100 == 0:
            print(f"TRAINING... Epsilon: {self.epsilon:.4f} | Loss: {loss.item():.5f}")    

        # --- UPDATE TARGET NETWORK ---
        # Every 1000 steps, update the target network to match the main network
        self.train_step_counter += 1
        if self.train_step_counter % 1000 == 0:
            self.target_model.load_state_dict(self.model.state_dict())