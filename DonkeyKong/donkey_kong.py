# donkey_kong.py - Donkey Kong character that throws barrels
import pygame
import random

class DonkeyKong(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # DK dimensions
        self.width = 60
        self.height = 60
        
        # Try to load DK image, use default rectangle if not found
        try:
            # Load image if available
            image_path = "D:\\2DonkeyKong\\DonkeyKong\\images\\donkey_kong.png"
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Create a colored rectangle as fallback
            self.image = pygame.Surface([self.width, self.height])
            self.image.fill((139, 69, 19))  # Brown color
            
            # Add some facial features to make it look more like DK
            pygame.draw.circle(self.image, (255, 255, 255), (15, 20), 5)  # Left eye
            pygame.draw.circle(self.image, (255, 255, 255), (45, 20), 5)  # Right eye
            pygame.draw.ellipse(self.image, (0, 0, 0), (20, 35, 20, 10))  # Mouth
        
        # Create rectangle for collision detection
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10  # Frames between animation updates
        
        # Barrel throwing
        self.barrel_timer = 0
        self.barrel_interval = random.randint(120, 240)  # Random interval between barrels
    
    def update(self):
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
            
            # In a more advanced version, you would switch between animation frames here
        
        # Update barrel timer
        self.barrel_timer += 1
        
        # Reset barrel timer if it's time to throw
        if self.should_throw_barrel():
            self.barrel_timer = 0
            self.barrel_interval = random.randint(120, 240)  # Set new random interval
    
    def should_throw_barrel(self):
        # Check if it's time to throw a barrel
        return self.barrel_timer >= self.barrel_interval