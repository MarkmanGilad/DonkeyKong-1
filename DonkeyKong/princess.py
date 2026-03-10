# princess.py - Princess character (goal of the game)
import pygame

class Princess(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Princess dimensions
        self.width = 30
        self.height = 50
        
        # Try to load princess image, use default rectangle if not found
        try:
            # Load image if available
            image_path = "D:\\2DonkeyKong\\DonkeyKong\\images\\princess.png"
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except (pygame.error, FileNotFoundError):
            # Create a colored rectangle as fallback
            self.image = pygame.Surface([self.width, self.height])
            self.image.fill((255, 255, 0))  # Yellow color
            
            # Add some details to make it look more like a princess
            pygame.draw.polygon(self.image, (255, 215, 0), 
                               [(15, 5), (5, 15), (25, 15)])  # Simple crown
            pygame.draw.rect(self.image, (255, 182, 193), 
                            (5, 15, 20, 35))  # Dress
        
        # Create rectangle for collision detection
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Animation state
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 30  # Frames between animation updates
    
    def update(self):
        # Simple animation - just wave or something
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
            
            # In a more advanced version, you would switch between animation frames here