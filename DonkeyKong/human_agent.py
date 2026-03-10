import pygame

class HumanAgent:
    def __init__(self):
        
        # Track current key states
        self.keys_pressed = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_SPACE: False
        }

    def process_input(self, events):
        # Update key states based on events
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self.keys_pressed:
                    self.keys_pressed[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed[event.key] = False

    def get_action(self, events=None, state=None):
        # Determine action from keys and return it
        # 0: Stop/Idle, 1: Right, 2: Left, 3: Up, 4: Down, 5: Jump, 
        if events:
            self.process_input(events)

        action = 0
        jump = self.keys_pressed[pygame.K_SPACE]
        
        if self.keys_pressed[pygame.K_RIGHT]:
            action = 6 if jump else 1
        elif self.keys_pressed[pygame.K_LEFT]:
            action = 7 if jump else 2
        elif self.keys_pressed[pygame.K_UP]:
            action = 3
        elif self.keys_pressed[pygame.K_DOWN]:
            action = 4
        elif jump:
            action = 5
            
        return action