import pygame
import json

pygame.init()

width = 800
height = 800
game_over = 0
tile_size = 40
clock = pygame.time.Clock()
fps = 60
lives = 5
score = 0

display = pygame.display.set_mode((width, height))
pygame.display.set_caption("Platformer")

bg_image = pygame.image.load("img/bg9.png")
bg_rect = bg_image.get_rect()

sound_jump = pygame.mixer.Sound("img/music/jump.wav")
sound_game_over = pygame.mixer.Sound("img/music/game_over.wav")

class Hero:
    def __init__(self):
        self.image = pygame.image.load("img/player1.png")
        self.rect = self.image.get_rect()
        self.direction = 1

    def update(self):
        self.rect.x += self.direction
        if self.rect.right > width or self.rect.left < 0:
            self.direction *= -1
        display.blit(self.image, self.rect)

def draw_text(text, color, size, x, y):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    display.blit(img, (x, y))
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        self.direction = 0
        self.gravity = 0
        self.jumped = False
        for num in range(1, 5):
            img_right = pygame.image.load("img/player1.png")
            img_right = pygame.transform.scale(img_right, (35, 70))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.image = self.images_right[self.index]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = height - 130
        self.dead_image = pygame.image.load("img/ghost.png")

    def update(self):
        global game_over
        x = 0
        y = 0
        walk_speed = 10
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped:
                self.gravity = -15
                self.jumped = True
                sound_jump.play()
            if key[pygame.K_LEFT]:
                x -= 5
                self.direction = -1
                self.counter += 1
            if key[pygame.K_RIGHT]:
                x += 5
                self.direction = 1
                self.counter += 1
            if self.counter > walk_speed:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]
        self.gravity += 1
        if self.gravity > 10:
            self.gravity = 10
        y += self.gravity
        for tile in world.tile_list:
            if tile[1].colliderect(self.rect.x + x, self.rect.y, self.width, self.height):
                x = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + y, self.width, self.height):
                if self.gravity < 0:
                    y = tile[1].bottom - self.rect.top
                    self.gravity = 0
                elif self.gravity >= 0:
                    y = tile[1].top - self.rect.bottom
                    self.gravity = 0
                    self.jumped = False
        self.rect.x += x
        self.rect.y += y
        if self.rect.bottom > height:
            self.rect.bottom = height
        if pygame.sprite.spritecollide(self, lava_group, False):
            game_over = -1
        if pygame.sprite.spritecollide(self, exit_group, False):
            game_over = 1
        if game_over == -1:
            sound_game_over.play()
            self.jumped = False
            self.image = self.dead_image
            if self.rect.y > 0:
                self.rect.y -= 5
        display.blit(self.image, self.rect)


class World:
    def __init__(self, data):
        dirt_img = pygame.image.load("img/dirt.png")
        grass_img = pygame.image.load("img/tile1.png")
        self.tile_list = []
        for row_count, row in enumerate(data):
            for col_count, tile in enumerate(row):
                if tile in {1, 2}:
                    images = {1: dirt_img, 2: grass_img}
                    img = pygame.transform.scale(images[tile], (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    self.tile_list.append((img, img_rect))
                elif tile == 3:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)

                elif tile == 5:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)

                elif tile == 6:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)

    def draw(self):
        for tile in self.tile_list:
            display.blit(tile[0], tile[1])


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        img = pygame.image.load("img/tile6.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

lava_group = pygame.sprite.Group()

class Button:
    def __init__(self, x, y, image):
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self):
        action = False
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        display.blit(self.image, self.rect)
        return action

restart_button = Button(width // 2, height // 2, "img/restart_btn 2.png")
start_button = Button(width // 2, height // 2, "img/start_btn 2.png")
exit_button = Button(width // 2, height // 2, "img/exit_btn 2.png")

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/exit.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

exit_group = pygame.sprite.Group()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

coin_group = pygame.sprite.Group()

with open("levels/level1.json", "r") as file:
    world_data = json.load(file)

level = 1
max_level = 3

def reset_level():
    player.rect.x = 100
    player.rect.y = height - 130
    lava_group.empty()
    exit_group.empty()
    with open(f"levels/level{level}.json", "r") as file:
        world_data = json.load(file)
    world = World(world_data)
    return world

world = World(world_data)
player = Player()

run = True
main_menu = True
while run:
    clock.tick(fps)
    display.blit(bg_image, bg_rect)
    if main_menu:
        start_button.draw()
        if start_button.draw():
            main_menu = False
            level = 1
            lives = 5
            world = reset_level()
    else:
        world.draw()
        lava_group.draw(display)
        exit_group.draw(display)
        coin_group.draw(display)
        draw_text((str(score)), (255, 255, 255), 30, 10, 10)
        player.update()

        if pygame.sprite.spritecollide(player, coin_group, True):
            score += 1
            print(score)

        if game_over == -1:
            if lives > 0:
                if restart_button.draw():
                    lives -= 1
                    if lives > 0:
                        player = Player()
                        world = reset_level()
                        game_over = 0
                    else:
                        main_menu = True
            else:
                main_menu = True
                lives = 5

        if game_over == 1:
            game_over = 0
            if level < max_level:
                level += 1
                world = reset_level()
            else:
                print("win")
                main_menu = True

        lava_group.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()

pygame.quit()