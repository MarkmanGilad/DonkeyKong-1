# barrel.py - Barrels thrown by Donkey Kong
import pygame
import random
import os

class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Barrel dimensions
        self.width = 20
        self.height = 20
        
        # Movement variables - start moving left
        self.change_x = -2
        self.change_y = 0
        
        # Try to load barrel image, use default rectangle if not found
        try:
            # Load image if available
            image_path = os.path.join(os.path.dirname(__file__), "images", "barrel.png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Create a colored circle as fallback
            self.image = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
            pygame.draw.circle(self.image, (139, 69, 19), (self.width // 2, self.height // 2), 
                              self.width // 2)  # Brown circle
        
        # Create rectangle for collision detection
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation variables
        self.animation_ticks = 0
        self.rotation_angle = 0
        
        # Store original image for rotation
        self.original_image = self.image.copy()
        # Platform state
        self.on_platform = False
        self.current_platform = None
    
    def update(self):
        # Animate rolling based on direction
        self.animation_ticks += 1
        if self.animation_ticks >= 3:  # Control rotation speed
            self.animation_ticks = 0
            
            # Rotate based on movement direction
            if self.change_x < 0:  # Moving left
                self.rotation_angle = (self.rotation_angle + 15) % 360
            elif self.change_x > 0:  # Moving right
                self.rotation_angle = (self.rotation_angle - 15) % 360
            
            # Create rotated image (using original to prevent quality loss)
            self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
            
            # Keep the rect centered at the same position
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center