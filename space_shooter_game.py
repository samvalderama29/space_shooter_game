import pygame
from os.path import join

from random import randint, uniform

# Function to display the start screen
def show_start_screen():
    start_sound = pygame.mixer.Sound(join('audio', 'start_sound.wav')) # Load start sound
    font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 100) # Load main font
    sub_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 50) # Load sub font

    title_surf = font.render("SPACE SHOOTER", True, (255, 215, 0)) # Render title text
    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)) # Center title

    sub_surf = sub_font.render("Press any key to start", True, (255, 165, 0))  # Render instruction text
    sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 1.65)) # Position instruction

    display_surface.fill('#3a2e3f') # Set background color
    display_surface.blit(title_surf, title_rect) # Draw title text
    display_surface.blit(sub_surf, sub_rect) # Draw instruction text
    pygame.display.update() # Update display

    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                start_sound.play()
                pygame.time.delay(500)
                waiting = False # Exit loop on key press

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha() # Load player image
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)) # Set position
        self.direction = pygame.Vector2() # Movement direction
        self.speed = 300 # Speed of player

        # Laser cooldown setup
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400 # # 400ms cooldown

        # Collision mask
        self.mask = pygame.mask.from_surface(self.image)

    # Laser cooldown timer
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    # Update player movement and shooting
    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt # Move player

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites)) # Shoot laser
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(250, 400)
        self.rotation_speed = randint(40, 80)
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        explosion_sound.play()

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

# Function to detect collisions
def collisions():
    global running

    # Check if player collides with meteors
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        display_game_over()
        pygame.time.delay(2000)
        running = False

    # Check if lasers hit meteors
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)

# Display score
def display_score():
    current_time = pygame.time.get_ticks() // 100 # Calculate score based on time
    text_surf = font.render(str(current_time), True, (240, 240, 240)) # Render score text
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50)) # Position text
    display_surface.blit(text_surf, text_rect) # Draw score
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10) # Draw border

# Display game over screen
def display_game_over():
    game_music.stop()
    game_over_sound.play()
    game_over_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 100)
    text_surf = game_over_font.render("GAME OVER", True, (255, 0, 0)) # Render game over text
    text_rect = text_surf.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)) # Center text
    display_surface.blit(text_surf, text_rect)
    pygame.display.update()

# General game setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter 👾')
show_start_screen()
running = True
clock = pygame.time.Clock()

# Load and import images and sound
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.2)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.2)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.2)
game_music.play(loops = -1)
game_over_sound = pygame.mixer.Sound(join('audio', 'game_over.wav'))
game_over_sound.set_volume(200)


# Initialize sprite groups
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

# Set custom events for meteors
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 200)

# Game loop
while running:
    dt = clock.tick() / 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
    # update
    all_sprites.update(dt)
    collisions()

    # draw the game
    display_surface.fill('#3a2e3f')
    display_score()
    all_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()

# source code: Clear Code youtube
