# ladder.py - Ladder objects for climbing between platforms
import pygame
import os

class Ladder(pygame.sprite.Sprite):
    def __init__(self, x, bottom_y, height):
        super().__init__()
        
        # Ladder dimensions
        self.width = 30
        self.height = height
        
        # Try to load ladder image, use default rectangle if not found
        try:
            # Load image if available
            image_path = os.path.join(os.path.dirname(__file__), "images", "ladder.png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Create a colored rectangle as fallback
            self.image = pygame.Surface([self.width, self.height])
            self.image.fill((200, 200, 0))  # Yellow-ish color
            
            # Add some detail to make it look like a ladder
            for y in range(0, self.height, 10):
                pygame.draw.line(self.image, (150, 150, 0), (0, y), (self.width, y), 2)
        
        # Create rectangle for collision detection
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = bottom_y  # Bottom of ladder connects to platform
    
    def update(self):
        # Ladders are static, so no update logic needed
        pass