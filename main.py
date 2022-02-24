import pygame
from sys import exit
from random import choice, randint
from math import cos, sin, radians
import settings


class SpaceHero:
    def __init__(self):
        pygame.init()
        self.settings = settings.Settings()
        pygame.display.set_caption('Космический герой')
        pygame.display.set_icon(pygame.image.load('ico.png'))
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.settings.screen_wight, self.settings.screen_height))
        self.background = Background()
        self.station = Station()
        self.player = Ship()
        self.all_sprites = pygame.sprite.Group()
        self.group_bullets = pygame.sprite.Group()
        self.group_energy = pygame.sprite.Group()
        self.group_dark_holes = pygame.sprite.Group()
        self.speed_moveobject = 1
        self.level = 1
        self.point = 0

    def run_game(self):
        while True:
            self._check_event()
            self._update_()
            self._update_screen()
            self.station.generation()
            self.clock.tick(self.settings.FPS)

    def _check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = True
                elif event.key == pygame.K_LEFT:
                    self.player.moving_left = True
                elif event.key == pygame.K_SPACE:
                    Bullet(1, self.player, game.group_bullets, 2)  # времено
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.player.moving_right = False
                elif event.key == pygame.K_LEFT:
                    self.player.moving_left = False

    def _update_(self):
        self.background.update()
        self.all_sprites.update()
        self.station.update()
        self.player.update()

    def _update_screen(self):
        self.window.fill(self.settings.bg_color)
        self.background.draw_background(self.window)
        self.all_sprites.draw(self.window)
        self.station.draw_station(self.window)
        self.player.draw_ship(self.window)
        pygame.display.update()


class Background:
    def __init__(self):
        background_space = ['space1.jpg', 'space2.jpg', 'space3.jpg']
        self.image = pygame.image.load('images/' + choice(background_space))
        self.imagedraw = self.image
        self.background_position_angle = 0
        self.background_speed = 0.1
        self.rect = self.imagedraw.get_rect(center=(400, 400))

    def update(self):
        self.background_position_angle += self.background_speed
        if self.background_position_angle > 360:
            self.background_position_angle = 0
        self.imagedraw = pygame.transform.rotate(self.image, self.background_position_angle)
        self.rect = self.imagedraw.get_rect(center=(400, 400))

    def draw_background(self, surface):
        surface.blit(self.imagedraw, self.rect)


class Ship:
    def __init__(self):
        model_ship = ['ship1.png', 'ship2.png', 'ship3.png']
        self.image = pygame.image.load('images/' + choice(model_ship))
        self.imagedraw = self.image
        self.mask = pygame.mask.from_surface(self.imagedraw)
        self.position_angle = 0
        self.position_x = 400
        self.position_y = 750
        self.speed = 1
        self.rect = self.image.get_rect(center=(self.position_x, self.position_y))
        self.moving_right = False
        self.moving_left = False

    def update(self):
        # обновление позиции и положения
        if self.moving_left:
            self.position_angle -= self.speed
            if self.position_angle < 0:
                self.position_angle = 360
        if self.moving_right:
            self.position_angle += self.speed
            if self.position_angle > 360:
                self.position_angle = 0
        self.position_x = int(400 + 350 * sin(radians(self.position_angle)))
        self.position_y = int(400 + 350 * cos(radians(self.position_angle)))
        self.rect = self.image.get_rect(center=(self.position_x, self.position_y))
        self.imagedraw = pygame.transform.rotate(self.image, self.position_angle)
        self.mask = pygame.mask.from_surface(self.imagedraw)

    def draw_ship(self, surface):
        surface.blit(self.imagedraw, self.rect)


class Station:
    def __init__(self):
        self.images_station = [pygame.image.load(f"images/station{i}.png") for i in range(1, 4)]
        self.image = self.images_station[0]
        self.imagedraw = self.image
        self.station_position_angle = 360
        self.station_speed = 0.1
        self.station_health = 800
        self.rect = self.imagedraw.get_rect(center=(400, 400))
        self.mask = pygame.mask.from_surface(self.imagedraw)
        self.generation_dark_hole = 0
        self.generation_energy = 0
        self.hit = 0

    def update(self):
        if self.hit > 0:
            self.generation_energy = self.hit
            self.station_health -= self.hit
        if not self.hit:
            self.station_position_angle -= self.station_speed
        if self.station_position_angle < 0:
            self.station_position_angle = 360
        if self.generation_dark_hole < 100:
            self.image = self.images_station[0]
        elif 100 <= self.generation_dark_hole < 150 or 180 <= self.generation_dark_hole < 200:
            self.image = self.images_station[1]
        elif 150 <= self.generation_dark_hole < 180:
            self.image = self.images_station[2]
        self.imagedraw = pygame.transform.rotate(self.image, self.station_position_angle)
        self.rect = self.imagedraw.get_rect(center=(400, 400))
        self.mask = pygame.mask.from_surface(self.imagedraw)
        self.hit = 0

    def draw_station(self, surface):
        surface.blit(self.imagedraw, self.rect)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (self.station_health, 0), 3)

    def generation(self):
        if self.generation_energy > 0:
            self.generation_dark_hole = 0
            for _ in range(self.generation_energy * 3):
                MoveObject('energy', game.group_energy, game.speed_moveobject)
            self.generation_energy = 0
        self.generation_dark_hole += 1
        if self.generation_dark_hole == 180:
            for _ in range(game.level * 10):
                MoveObject('dark_hole', game.group_dark_holes, game.speed_moveobject)
        if self.generation_dark_hole > 200:
            self.generation_dark_hole = 0


class MoveObject(pygame.sprite.Sprite):
    def __init__(self, object_type, group, speed=1):
        super().__init__(game.all_sprites)
        self.cost = 0
        self.position_angle_move = randint(0, 360)
        self.x = 400.0
        self.y = 400.0
        self.vx = round(sin(radians(self.position_angle_move)) * speed, 2)
        self.vy = round(cos(radians(self.position_angle_move)) * speed, 2)
        self.object_type = object_type
        if self.object_type == 'energy':
            self.cost = choice([1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3])
            self.image = pygame.image.load('images/energy' + str(self.cost) + '.png')
        elif self.object_type == 'dark_hole':
            self.image = pygame.image.load('images/dark_hole1.png')
        self.image = pygame.transform.rotate(self.image, self.position_angle_move)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(400, 400))
        self.add(group)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        if self.object_type == 'energy':
            for bullet in game.group_bullets:
                if pygame.sprite.collide_mask(self, bullet):
                    self.kill()
        if 800 >= self.x >= 0 and 800 >= self.y >= 0:
            return
        self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_type, player, group, speed=1):
        super().__init__(game.all_sprites)
        self.bullet_type = bullet_type
        self.bullet_kill = 0
        if self.bullet_type == 1:
            self.image = pygame.image.load('images/bullet1.png')
        self.x = player.position_x
        self.y = player.position_y
        self.vx = -round(sin(radians(player.position_angle)) * speed, 2)
        self.vy = -round(cos(radians(player.position_angle)) * speed, 2)
        self.image = pygame.transform.rotate(self.image, player.position_angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.add(group)

    def update(self):
        if self.bullet_kill > 0:
            self.kill()
            return
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        if self.bullet_type == 1:  # если снаряд 1-го типа сталкивается с черной дырой он пропадает
            for dark_hole in game.group_dark_holes:
                if pygame.sprite.collide_mask(self, dark_hole):
                    self.bullet_kill = 1
                    return
        if pygame.sprite.collide_mask(self, game.station):  # если снаряд сталкивается со станцией
            game.station.hit = self.bullet_type
            self.bullet_kill = 1
            return
        if 390 <= self.x <= 410 and 390 <= self.y <= 410:
            self.kill()


if __name__ == '__main__':
    game = SpaceHero()
    game.run_game()
