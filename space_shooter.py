import pygame
import os, random, math, sys

pygame.init()
pygame.mixer.init()
pygame.font.init()

cwd = os.getcwd()

WIDTH, HEIGHT = 1920, 1080
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Shooter')

class Player(pygame.sprite.Sprite):

    def __init__(self, top_left_coord):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill('white')
        self.rect = self.image.get_rect()
        self.rect.topleft = top_left_coord
        self.velocity = 5

    def move(self, dx = 0, dy = 0):
        self.rect.move_ip(dx * self.velocity, dy * self.velocity)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Projectile(pygame.sprite.Sprite):

    def __init__(self, top_left_coord, dx = float(0), dy = float(0)):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        self.dx = dx
        self.dy = dy
        self.image = pygame.Surface((10, 10))
        self.image.fill('white')
        self.rect = self.image.get_rect()
        self.rect.topleft = top_left_coord
        self.velocity = 15

    def update(self):
        self.rect.move_ip(self.dx * self.velocity, self.dy * self.velocity)
        if self.rect.top < 0 or self.rect.top > HEIGHT:
            self.kill()
        if self.rect.left < 0 or self.rect.left > WIDTH:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def check_collision(self, group, enemy_group, kill_self=False):
        for self in group:
            pygame.sprite.spritecollide(self, enemy_group, kill_self)

class Enemy(pygame.sprite.Sprite):

    def __init__(self, top_left_coord, dx = 0, dy = 0):
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill('red')
        self.rect = self.image.get_rect()
        self.rect.topleft = top_left_coord
        self.dx, self.dy = dx, dy
        self.velocity = 7

    def update(self):
        self.rect.move_ip(self.dx * self.velocity, self.dy * self.velocity)
        if self.rect.top < 0 or self.rect.top > HEIGHT:
            self.kill()
        if self.rect.left < 0 or self.rect.left > WIDTH:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def check_collision(self, group, enemy_group, kill_self=False):
        for self in group:
            pygame.sprite.spritecollide(self, enemy_group, kill_self)

# function to define enemy spawns from all screen sides and assign movement
def spawn():
    sides = ['left', 'right', 'top', 'bottom']
    side = random.choice(sides)
    if side == 'left':
        x = 0
        y = random.randint(0, HEIGHT)
        dx = 1
        dy = 0
    if side == 'right':
        x = WIDTH
        y = random.randint(0, HEIGHT)
        dx = -1
        dy = 0
    if side == 'top':
        x = random.randint(0, WIDTH)
        y = 0
        dx = 0
        dy = 1
    if side == 'bottom':
        x = random.randint(0, WIDTH)
        y = HEIGHT
        dx = 0
        dy = -1
    return x, y, dx, dy


def draw_text(text = str, location = (0, 0), color = 'white', size = int):
    font = pygame.font.SysFont('Agency FB', size)
    blit_text = font.render(f'{text}', 1, color)
    WIN.blit(blit_text, location)
    

# add sprites to groups    
projectiles = pygame.sprite.Group()
player = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# spawn player
player = Player((WIDTH / 2, HEIGHT / 2))

# load cursor image, hide cursor
new_cursor_path = os.path.join(cwd, 'images', 'crosshair2.png')
new_cursor = pygame.image.load(new_cursor_path).convert_alpha()
pygame.mouse.set_visible(False)

# load and assign audio files
shoot_sound_path = os.path.join(cwd, 'audio', 'shoot.wav')
SHOOT_SOUND = pygame.mixer.Sound(shoot_sound_path)
SHOOT_SOUND.set_volume(0.7)
enemy_death_sound_path = os.path.join(cwd, 'audio', 'success.wav')
ENEMY_DEATH_SOUND = pygame.mixer.Sound(enemy_death_sound_path)
ENEMY_DEATH_SOUND.set_volume(0.25)
get_hit_sound_path = os.path.join(cwd, 'audio', 'roblox-death-sound_1.mp3')
GET_HIT_SOUND = pygame.mixer.Sound(get_hit_sound_path)
lose_sound_path = os.path.join(cwd, 'audio', 'sfx_lose.wav')
LOSE_SOUND = pygame.mixer.Sound(lose_sound_path)

def main():
    run = True
    clock = pygame.time.Clock()

    # scorekeeping
    lives = 3
    score = 0

    # enemy parameters
    enemy_spawn = 0
    enemy_timer = 300
        
    while run:
        # fill screen with background, display scoreline
        WIN.fill('black')
        draw_text(f'Score: {score}', (10, 10), 'green', 30)
        draw_text(f'Lives: {lives}', (10, 45), 'green', 30)

        # set FPS and spawn enemies
        enemy_spawn +=clock.tick(120)
        if enemy_spawn > enemy_timer:
            x, y, dx, dy = spawn()
            enemy = Enemy((x, y), dx, dy)
            enemies.add(enemy)
            enemy_spawn = 0
            enemy_timer -= .2
            print(enemy_timer)

        # event manager
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

            # generate projectile aimed at mouse when clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = (mouse_x - player.rect.right) / math.sqrt((mouse_x - player.rect.right)**2 + (mouse_y - player.rect.top)**2)
                dy = (mouse_y - player.rect.top) / math.sqrt((mouse_x - player.rect.right)**2 + (mouse_y - player.rect.top)**2)
                projectile = Projectile(player.rect.topright, dx, dy)
                projectiles.add(projectile)
                SHOOT_SOUND.play()

        # player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.rect.x > 0:
            player.move(dx = -1)
        if keys[pygame.K_d] and player.rect.x + player.image.get_width() < WIDTH:
            player.move(dx = 1)
        if keys[pygame.K_w] and player.rect.y > 0:
            player.move(dy = -1)
        if keys[pygame.K_s] and player.rect.y + player.image.get_height() < HEIGHT:
            player.move(dy = 1)

        # check for collision
        for projectile in projectiles:
            if pygame.sprite.spritecollide(projectile, enemies, True):
                projectile.kill()
                score += 1
                ENEMY_DEATH_SOUND.play()
        if pygame.sprite.spritecollide(player, enemies, True):
            lives -= 1
            GET_HIT_SOUND.play()
            
        # update sprite positions and draw onto screen
        player.update()
        player.draw(WIN)
        projectiles.update()
        projectiles.draw(WIN)
        enemies.update()
        enemies.draw(WIN)

        # redraw cursor, appears on top of player/proj/enemy sprites
        mouse_pos = pygame.mouse.get_pos()
        WIN.blit(new_cursor, mouse_pos)

        # end game if 3 lives are lost
        if lives == 0:
            draw_text(f'Lives: 0', (10, 45), 'green', 30)           
            draw_text('YOU DIED', (230, 200), 'red', 500)
            LOSE_SOUND.play()
            pygame.display.flip()
            pygame.time.delay(5000)
            break
        
        # update display each frame
        pygame.display.flip()
        

    pygame.quit()


if __name__ == '__main__':
    main()


