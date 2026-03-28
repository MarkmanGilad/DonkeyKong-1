import pygame
import os
import config

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.x = x
        self.y = y
        self.change_x = 0
        self.change_y = 0
        self.speed = config.PLAYER_SPEED
        self.climb_speed = config.PLAYER_CLIMB_SPEED
        self.jump_power = config.PLAYER_JUMP_POWER

        self.facing_right = True
        self.on_ladder = False
        self.is_jumping = False
        self.environment = None
        # Counts consecutive frames the character is holding on a ladder without moving
        self.ladder_hold_counter = 0

        self.load_images()
        self.image = self.images['default']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def load_images(self):
        self.images = {}

        try:
            print("Loading character images...")

            img_dir = os.path.join(os.path.dirname(__file__), "images")
            self.images['default'] = self.load_image(os.path.join(img_dir, "mario_idle.png"))
            self.images['right'] = self.load_image(os.path.join(img_dir, "mario_right.png"))
            self.images['left'] = self.load_image(os.path.join(img_dir, "mario_left.png"))
            self.images['climb'] = self.load_image(os.path.join(img_dir, "mario_back.png"))

        except Exception as e:
            print(f"Error loading character images: {e}")
            fallback = self._create_default_image((0, 0, 255))
            self.images['default'] = fallback
            self.images['right'] = fallback
            self.images['left'] = fallback
            self.images['climb'] = fallback

    def load_image(self, path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (30, 50))

    def _create_default_image(self, color):
        img = pygame.Surface([30, 50])
        img.fill(color)
        return img

    def update_image(self):
        # Show climbing image whenever on a ladder (even if stationary)
        if self.on_ladder:
            self.image = self.images['climb']
            return
        elif self.change_x > 0:
            self.image = self.images['right']
            self.facing_right = True
        elif self.change_x < 0:
            self.image = self.images['left']
            self.facing_right = False
        else:
            self.image = self.images['right'] if self.facing_right else self.images['left']

    def move_right(self):
        if self.on_ladder:
            self.change_x = self.speed * 0.5
        else:
            self.change_x = self.speed

    def move_left(self):
        if self.on_ladder:
            self.change_x = -self.speed * 0.5
        else:
            self.change_x = -self.speed

    def move_up(self):
        if self.on_ladder:
            self.change_y = -self.climb_speed
            self.is_jumping = False

    def move_down(self):
        if self.on_ladder:
            self.change_y = self.climb_speed
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping and not self.on_ladder:
            self.is_jumping = True
            self.change_y = -self.jump_power

    def stop_horizontal(self):
        self.change_x = 0

    def stop_vertical(self):
        if self.on_ladder:
            self.change_y = 0

    def update(self):
        # Update image
        self.update_image()
