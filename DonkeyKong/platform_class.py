# platform_class.py - Platform objects for the game
import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y):
        super().__init__()
        
        # Try to load platform image, use default rectangle if not found
        try:
            # Load image if available
            image_path = "D:\\2DonkeyKong\\DonkeyKong\\images\\platform.png"
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        except (pygame.error, FileNotFoundError):
            # Create a colored rectangle as fallback
            self.image = pygame.Surface([width, height])
            self.image.fill((139, 69, 19))  # Brown color
        
        # Create rectangle for collision detection
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self):
        # Platforms are static, so no update logic needed
        pass