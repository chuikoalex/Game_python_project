import pygame
import pickle
from sys import exit
from random import choice, randint
from math import cos, sin, radians
from settings import Settings


class SpaceHero:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        pygame.display.set_caption(self.settings.title_game)
        pygame.display.set_icon(pygame.image.load('ico.png'))
        self.images_move_object = [pygame.image.load(f"images/move_object{i}.png") for i in range(0, 6)]
        self.images_bullet = [pygame.image.load(f"images/bullet{i}.png") for i in range(0, 4)]
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((self.settings.screen_wight, self.settings.screen_height))
        self.interface = UI()
        self.background = Background()
        self.station = Station()
        self.player = Ship()
        self.panel = Panel(self.player)
        self.all_sprites = pygame.sprite.Group()
        self.group_bullets = pygame.sprite.Group()
        self.group_energy = pygame.sprite.Group()
        self.group_dark_holes = pygame.sprite.Group()
        self.group_plus_minus = pygame.sprite.Group()
        self.level = 1
        self.start_game = True  # True - игра запущена, нужно буде вывести стартовое меню
        self.number_save = 0  # Номер сохранения которое запустил игрок

    def run_game(self):
        while True:
            self._check_event()
            self._update_()
            self._update_screen()
            if self.start_game:
                self.interface.ui_start_game()
            self.station.generation()
            self.clock.tick(self.settings.FPS)

    def save_game(self, data_save):
        """Сохранение игры"""
        if data_save['save_name'] != 'пусто':
            data_save['level'] = self.level  # уровень игры
            data_save['ship_number_ship'] = game.player.number_ship  # тип (цвет) корабля
            data_save['ship_position_angle'] = game.player.position_angle  # позиция корабля
            data_save['ship_speed'] = game.player.speed  # скорость корабля
            data_save['panel_player_health'] = game.panel.player_health  # жизни корабля
            data_save['panel_energy_point'] = game.panel.energy_point  # количество энергии
            data_save['energy_point_in_bank'] = game.panel.energy_point_in_bank  # количество энергии в банке
            data_save['panel_bullets_type'] = game.panel.bullets_type  # тип ракет
            data_save['panel_bullets_speed'] = game.panel.bullets_speed  # скорость ракет
            data_save['panel_bullets_start_speed'] = game.panel.bullets_start_speed  # время ожидания запуска
            data_save['panel_magnetic_field'] = game.panel.magnetic_field  # тип магнитного поля
            data_save['station_speed'] = game.station.station_speed  # скорость вращения станции (зачем сохранять?)
            data_save['station_health'] = game.station.station_health  # количество жизни у станции
        try:
            with open(f'save/data{game.number_save}.save', 'wb') as f:
                pickle.dump(data_save, f)
        except EOFError:
            return False
        return True

    def load_game(self, data_save):
        """Загрузка игры"""
        game.number_save = data_save['number_file']
        self.level = data_save['level']
        game.player.number_ship = data_save['ship_number_ship']
        game.player.position_angle = data_save['ship_position_angle']
        game.player.speed = data_save['ship_speed']
        game.panel.player_health = data_save['panel_player_health']
        game.panel.energy_point = data_save['panel_energy_point']
        game.panel.energy_point_in_bank = data_save['energy_point_in_bank']
        game.panel.bullets_type = data_save['panel_bullets_type']
        game.panel.bullets_speed = data_save['panel_bullets_speed']
        game.panel.bullets_start_speed = data_save['panel_bullets_start_speed']
        game.panel.magnetic_field = data_save['panel_magnetic_field']
        game.station.station_speed = data_save['station_speed']
        game.station.station_health = data_save['station_health']
        game.player.num_ship(game.player.number_ship)
        return True

    def _check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.moving_right = True
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.moving_left = True
                elif event.key == pygame.K_SPACE:
                    game.interface.ui_pause_game()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.moving_right = False
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.moving_left = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                self.panel.pressed_panel(x, y)

    def _update_(self):
        """Обновление состояния объектов"""
        self.background.update()
        self.all_sprites.update()
        self.station.update()
        self.player.update()
        self.panel.update(self.player)

    def _update_screen(self):
        """Отрисовка объектов в окне"""
        self.window.fill(self.settings.bg_color)
        self.background.draw_background(self.window)
        self.all_sprites.draw(self.window)
        self.station.draw_station(self.window)
        self.player.draw_ship(self.window)
        self.panel.draw_panel(self.window)
        pygame.display.update()


class UI:
    class Button:
        def __init__(self, x, y, text, wight, surface_ui):
            self.surface_button = pygame.Surface((wight, 45))
            self.rect = pygame.Rect(x + 25, y + 25, x + 25 + wight, y + 70)
            self.surface_button.fill((36, 159, 222))
            pygame.draw.rect(self.surface_button, (18, 79, 111), (0, 0, wight, 45), 3)
            self.button_font = pygame.font.Font('font/Pixel_Times.ttf', 24)
            text = self.button_font.render(text, True, (5, 5, 5))
            self.surface_button.blit(text, (10, 9))
            surface_ui.blit(self.surface_button, (x, y))

        def click(self):
            x, y = pygame.mouse.get_pos()
            if self.rect[0] < x < self.rect[2] and self.rect[1] < y < self.rect[3]:
                return True
            return False

    def __init__(self):
        self.surface_ui = pygame.Surface((750, 870))
        self.title_font = pygame.font.Font('font/Space_age.ttf', 42)
        self.text_font = pygame.font.Font('font/Pixel_Times.ttf', 24)

    def draw_window_ui(self):
        """Отрисовка основного окна интерфейса"""
        self.surface_ui.fill((75, 91, 127))
        pygame.draw.rect(self.surface_ui, (38, 50, 56), (0, 0, 750, 870), 5)
        pygame.draw.rect(self.surface_ui, (96, 125, 139), (0, 0, 760, 880), 5)
        title = self.title_font.render(game.settings.title_game, True, (255, 111, 0))
        self.surface_ui.blit(title, (self.surface_ui.get_rect().centerx - title.get_rect().centerx, 30))

    def ui_start_game(self):
        """Интерфейс запуска игры, выбор слота сохранения"""
        self.draw_window_ui()
        text = self.text_font.render(game.settings.title_rule_ui1, True, (255, 255, 255))
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 150))
        file1 = f"{game.settings.title_save} {game.settings.data1_save['number_file']}:" \
                f"  {game.settings.data1_save['save_name']}"
        file2 = f"{game.settings.title_save} {game.settings.data2_save['number_file']}:" \
                f"  {game.settings.data2_save['save_name']}"
        file3 = f"{game.settings.title_save} {game.settings.data3_save['number_file']}:" \
                f"  {game.settings.data3_save['save_name']}"
        save1 = self.Button(50, 200, file1, 650, self.surface_ui)
        save2 = self.Button(50, 270, file2, 650, self.surface_ui)
        save3 = self.Button(50, 340, file3, 650, self.surface_ui)
        exit1 = self.Button(240, 500, game.settings.title_exit, 280, self.surface_ui)
        self.ui_draw(game.window)
        start = True
        while start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if save1.click():
                        if game.settings.data1_save['save_name'] in {'пусто', 'ошибка чтения файла'}:
                            save_name = self.ui_input(290, 228)
                            if len(save_name) > 0:
                                game.settings.data1_save['save_name'] = save_name
                                game.number_save = 1
                                game.save_game(game.settings.data1_save)
                                start = False
                            else:
                                self.ui_draw(game.window)
                        else:
                            game.load_game(game.settings.data1_save)
                            start = False
                    elif save2.click():
                        if game.settings.data2_save['save_name'] in {'пусто', 'ошибка чтения файла'}:
                            save_name = self.ui_input(300, 298)
                            if len(save_name) > 0:
                                game.settings.data2_save['save_name'] = save_name
                                game.number_save = 2
                                game.save_game(game.settings.data2_save)
                                start = False
                            else:
                                self.ui_draw(game.window)
                        else:
                            game.load_game(game.settings.data2_save)
                            start = False
                    elif save3.click():
                        if game.settings.data3_save['save_name'] in {'пусто', 'ошибка чтения файла'}:
                            save_name = self.ui_input(300, 368)
                            if len(save_name) > 0:
                                game.settings.data3_save['save_name'] = save_name
                                game.number_save = 3
                                game.save_game(game.settings.data3_save)
                                start = False
                            else:
                                self.ui_draw(game.window)
                        else:
                            game.load_game(game.settings.data3_save)
                            start = False
                    if exit1.click():
                        pygame.quit()
                        exit()
        game.start_game = False

    def ui_end_game(self, result):
        """Интерфейс окончания игры (result = 0 - проигрыш, 1 - победа)"""
        self.draw_window_ui()
        text = self.text_font.render(game.settings.title_end_game[result], True, (255, 255, 255))
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 150))
        restart = self.Button(250, 430, game.settings.title_end_game[2], 280, self.surface_ui)
        exit1 = self.Button(250, 500, game.settings.title_end_game[3], 280, self.surface_ui)
        self.ui_draw(game.window)
        end = True
        while end:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart.click():
                        if game.number_save == 1:
                            game.settings.data1_save = {'number_file': 1, 'save_name': 'пусто'}
                            game.save_game(game.settings.data1_save)
                        elif game.number_save == 2:
                            game.settings.data2_save = {'number_file': 2, 'save_name': 'пусто'}
                            game.save_game(game.settings.data2_save)
                        elif game.number_save == 3:
                            game.settings.data3_save = {'number_file': 3, 'save_name': 'пусто'}
                            game.save_game(game.settings.data3_save)
                        game.__init__()
                        game.run_game()
                    elif exit1.click():
                        pygame.quit()
                        exit()

    def ui_pause_game(self):
        """Интерфейс постановки игры на паузу (видна информация)"""
        self.draw_window_ui()
        col = (255, 255, 255)
        text = self.text_font.render(game.settings.title_pause_ui, True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 150))
        text = self.text_font.render(game.settings.title_pause_ui0[0] + str(game.level), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 200))
        text = self.text_font.render(game.settings.title_pause_ui0[1] + str(game.panel.energy_point), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 250))
        text = self.text_font.render(game.settings.title_pause_ui0[2] + str(game.panel.energy_point_in_bank), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 300))
        text = self.text_font.render(game.settings.title_pause_ui0[3] + str(game.panel.player_health), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 350))
        text = self.text_font.render(game.settings.title_pause_ui0[4] + str(game.panel.bullets_type), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 400))
        text = self.text_font.render(game.settings.title_pause_ui0[5] + str(game.panel.magnetic_field), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 450))
        text = self.text_font.render(game.settings.title_pause_ui0[6] + str(game.station.station_health), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 500))
        text = self.text_font.render(game.settings.title_pause_ui0[7] + str(game.number_save), True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 600))
        text = self.text_font.render(game.settings.title_pause_ui0[8], True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 700))
        self.ui_draw(game.window)
        pause = True
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause = False
                    elif event.key == pygame.K_SPACE:
                        pause = False

    def ui_level_up_game(self):
        """Интерфейс перехода на новый уровень (набрано 1000 Е), доступ к магазину"""

        def available_energy(energy):
            """Проверка хватает ли энергии для покупки"""
            if energy <= game.panel.energy_point:
                return True
            return False

        self.draw_window_ui()
        game.panel.energy_point += game.panel.energy_point_in_bank  # достаем энергию из банка
        game.panel.energy_point_in_bank = 0  # обнуляем энергию в банке
        col = (255, 255, 255)
        text = self.text_font.render(game.settings.title_shop_game[0], True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 100))
        text = self.text_font.render(game.settings.title_shop_game[1], True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 150))
        text = self.text_font.render(game.settings.title_shop_game[2], True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 180))
        # магазин
        up_speed_ship = self.Button(50, 230, game.settings.shop_game[0], 650, self.surface_ui)
        down_speed_ship = self.Button(50, 280, game.settings.shop_game[1], 650, self.surface_ui)
        type_bullet = self.Button(50, 330, game.settings.shop_game[2], 650, self.surface_ui)
        up_speed_bullet = self.Button(50, 380, game.settings.shop_game[3], 650, self.surface_ui)
        time_out_bullet = self.Button(50, 430, game.settings.shop_game[4], 650, self.surface_ui)
        type_magnetic_field = self.Button(50, 480, game.settings.shop_game[5], 650, self.surface_ui)
        ship_up_10_health = self.Button(50, 530, game.settings.shop_game[6], 650, self.surface_ui)
        ship_up_20_health = self.Button(50, 580, game.settings.shop_game[7], 650, self.surface_ui)
        hit_station_100 = self.Button(50, 630, game.settings.shop_game[8], 650, self.surface_ui)
        self.ui_sell()
        go = self.Button(200, 780, game.settings.title_shop_game[3], 330, self.surface_ui)
        text = self.text_font.render(game.settings.title_shop_game[4], True, col)
        self.surface_ui.blit(text, (self.surface_ui.get_rect().centerx - text.get_rect().centerx, 830))

        self.ui_draw(game.window)
        shop = True
        while shop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if up_speed_ship.click():
                        if game.player.speed < 3:
                            if available_energy(200):
                                game.player.speed += 1
                                game.panel.energy_point -= 200
                                self.ui_sell(game.settings.shop_game_res[0])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif down_speed_ship.click():
                        if game.player.speed > 1:
                            if available_energy(100):
                                game.player.speed -= 1
                                game.panel.energy_point -= 100
                                self.ui_sell(game.settings.shop_game_res[1])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif type_bullet.click():
                        if game.panel.bullets_type < 3:
                            if available_energy(500):
                                game.panel.bullets_type += 1
                                game.panel.energy_point -= 500
                                self.ui_sell(game.settings.shop_game_res[2])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif up_speed_bullet.click():
                        if game.panel.bullets_speed < 3:
                            if available_energy(800):
                                game.panel.bullets_speed += 1
                                game.panel.energy_point -= 800
                                self.ui_sell(game.settings.shop_game_res[3])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif time_out_bullet.click():
                        if game.panel.bullets_start_speed > 70:
                            if available_energy(400):
                                game.panel.bullets_start_speed -= 20
                                game.panel.energy_point -= 400
                                self.ui_sell(game.settings.shop_game_res[4])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif type_magnetic_field.click():
                        if game.panel.magnetic_field < 3:
                            if available_energy(500):
                                game.panel.magnetic_field += 1
                                game.panel.energy_point -= 500
                                self.ui_sell(game.settings.shop_game_res[5])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif ship_up_10_health.click():
                        if game.panel.player_health + 10 <= 80:
                            if available_energy(200):
                                game.panel.player_health += 10
                                game.panel.energy_point -= 200
                                self.ui_sell(game.settings.shop_game_res[6])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif ship_up_20_health.click():
                        if game.panel.player_health + 20 <= 80:
                            if available_energy(300):
                                game.panel.player_health += 20
                                game.panel.energy_point -= 300
                                self.ui_sell(game.settings.shop_game_res[7])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[10], False)
                    elif hit_station_100.click():
                        if game.station.station_health > 100:
                            if available_energy(1200):
                                game.station.station_health -= 100
                                game.panel.energy_point -= 1200
                                self.ui_sell(game.settings.shop_game_res[8])
                            else:
                                self.ui_sell(game.settings.shop_game_res[9], False)
                        else:
                            self.ui_sell(game.settings.shop_game_res[11], False)
                    elif go.click():
                        game.panel.energy_point_in_bank = game.panel.energy_point  # кладем остатки энергии в банк
                        game.panel.energy_point = 0  # обнуляем энергию у игрока
                        if game.number_save == 1:
                            game.save_game(game.settings.data1_save)
                        elif game.number_save == 2:
                            game.save_game(game.settings.data2_save)
                        elif game.number_save == 3:
                            game.save_game(game.settings.data3_save)
                        game.level += 1
                        shop = False

    def ui_draw(self, surface):
        surface.blit(self.surface_ui, (25, 25))
        pygame.display.update()

    def ui_sell(self, message=' ', yes_no=True):
        """Поле вывода количества энергии и результата покупки"""
        energy = game.panel.energy_point + game.panel.energy_point_in_bank
        surface_sell = pygame.Surface((650, 95))
        surface_sell.fill((75, 91, 127))
        text = self.text_font.render(game.settings.title_shop_game[5] + str(energy), True, (255, 255, 255))
        surface_sell.blit(text, (surface_sell.get_rect().centerx - text.get_rect().centerx, 9))

        pygame.draw.rect(surface_sell, (255, 255, 255), (25, 40, 600, 50), 3)
        if yes_no:
            color = (0, 200, 0)
        else:
            color = (100, 10, 0)
        text = self.text_font.render(message, True, color)
        surface_sell.blit(text, (surface_sell.get_rect().centerx - text.get_rect().centerx, 50))
        self.surface_ui.blit(surface_sell, (50, 680))
        self.ui_draw(game.window)
        pass

    def ui_input(self, x, y):
        """Поле ввода имени для интерфейса начало игры, когда выбран слот сохранения"""
        surface_input = pygame.Surface((400, 38))
        surface_input_text = pygame.Surface((600, 45))
        image = pygame.image.load(f'images/cursor.png')
        name = ''
        input_litter = True
        while input_litter:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_litter = False
                    elif event.key == pygame.K_ESCAPE:
                        name = ''
                        input_litter = False
                    elif event.key == pygame.K_SPACE:
                        name += ' '
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 12:
                            name += event.unicode
            # заменяем сообщение о начале игры на "Введите имя:"
            text_rule = self.text_font.render(game.settings.title_rule_ui2, True, (255, 255, 255))
            surface_input_text.fill((75, 91, 127))
            surface_input_text.blit(text_rule, (0, 0))
            game.window.blit(surface_input_text, (110, 175))
            # прорисовываем вводимое имя
            text_name = self.text_font.render(name, True, (255, 255, 255))
            surface_input.fill((36, 159, 222))
            surface_input.blit(image, (0, 0))
            surface_input.blit(text_name, (15, 8))
            game.window.blit(surface_input, (x, y))

            pygame.display.update()
        name = name.strip()
        if len(name) < 1:
            return ''
        return name


class Background:
    def __init__(self):
        background_space = ['space1.jpg', 'space2.jpg', 'space3.jpg']
        self.image = pygame.image.load('images/' + choice(background_space))  # случайный фон
        self.image_draw = self.image
        self.background_position_angle = 0  # угол вращения
        self.background_speed = 0.1  # скорость вращения
        self.rect = None
        self.update()

    def update(self):
        self.background_position_angle += self.background_speed
        if self.background_position_angle > 360:
            self.background_position_angle = 0
        self.image_draw = pygame.transform.rotate(self.image, self.background_position_angle)
        self.rect = self.image_draw.get_rect(center=(400, 400))

    def draw_background(self, surface):
        surface.blit(self.image_draw, self.rect)


class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.number_ship = None
        self.num_ship(choice([1, 2, 3]))  # выбирается случайный номер корабля
        self.position_angle = 0  # начальный угол положения (внизу 0)
        self.position_x = 400  # начальная координата х
        self.position_y = 750  # начальная координата у
        self.speed = 1  # скорость движения корабля
        self.moving_right = False  # движение по часовой
        self.moving_left = False  # движение против часовой
        self.magnetic_field = False  # ВКЛ. Магнитного поля - синий круг
        self.protective_field = False  # ВКЛ. Защитного поля - красный круг
        self.image_draw, self.mask = None, None
        self.update()

    def num_ship(self, number):
        """Рисунок корабля (случайный если не было загрузки)"""
        self.number_ship = number
        self.image = pygame.image.load(f'images/ship{self.number_ship}.png')

    def update(self):
        if self.moving_left:  # движение против часовой
            self.position_angle -= self.speed
            if self.position_angle < 0:
                self.position_angle = 360
        if self.moving_right:  # движение по часовой
            self.position_angle += self.speed
            if self.position_angle > 360:
                self.position_angle = 0
        self.position_x = int(400 + 350 * sin(radians(self.position_angle)))  # расчет новых координат х у
        self.position_y = int(400 + 350 * cos(radians(self.position_angle)))  # в зависимости от угла положения
        self.image_draw = pygame.transform.rotate(self.image, self.position_angle)
        self.rect = self.image_draw.get_rect(center=(self.position_x, self.position_y))
        self.mask = pygame.mask.from_surface(self.image_draw)

    def draw_ship(self, surface):
        surface.blit(self.image_draw, self.rect)
        if self.magnetic_field:  # Если ВКЛ. Магнитное поле рисуем синий круг
            pygame.draw.circle(surface, (0, 0, 255), (self.rect.centerx, self.rect.centery), 35, 2)
        if self.protective_field:  # Если ВКЛ. Защитное поле рисуем красный круг
            pygame.draw.circle(surface, (255, 0, 0), (self.position_x, self.position_y), 35, 2)


class Panel:
    def __init__(self, player):
        self.player = player
        self.images_panel = [pygame.image.load(f"images/panel{i}.png") for i in range(18)]
        self.surface_panel = pygame.Surface((730, 97))
        self.player_health = 50  # здоровье игрока
        self.energy_point = 0  # очки энергии (деньги)
        self.energy_point_in_bank = 0  # очки энергии в банке (остаются если не потратить в магазине)
        self.bullets_type = 1  # тип ракет (1..3)
        self.bullets_speed = 2  # скорость ракет
        self.bullets_start = 0  # к запуску ракет готов, должно быть 0
        self.bullets_start_speed = 100  # время ожидания (охлаждение) после запуска (кратно 4)
        self.magnetic_field = 1  # тип магнитного поля (1..3) - дольше работа
        self.magnetic_field_power = 0  # время работы магнитного поля (40...0)
        self.protective_field = 0  # защитное поле отключается при 0
        self.energy_font = pygame.font.Font('font/Space_age.ttf', 22)
        self.update(self.player)

    def update(self, player):
        self.player = player
        if self.player_health < 0:
            game.interface.ui_end_game(0)
        if self.energy_point >= 1000:
            game.player.magnetic_field = False
            game.player.protective_field = False
            game.player.moving_right = False
            game.player.moving_left = False
            game.interface.ui_level_up_game()
            return
        # панель жизни и очков
        self.surface_panel.blit(self.images_panel[0], (0, 0))
        text = self.energy_font.render(str(self.energy_point), True, (36, 159, 222))
        self.surface_panel.blit(text, (25, 11))
        pygame.draw.line(self.surface_panel, (255, 0, 0), (27, 57), (27 + self.player_health, 57), 7)
        # панель управления полетом
        if self.player.moving_left:
            self.surface_panel.blit(self.images_panel[2], (150, 0))
        else:
            self.surface_panel.blit(self.images_panel[1], (150, 0))
        if self.player.moving_right:
            self.surface_panel.blit(self.images_panel[4], (215, 0))
        else:
            self.surface_panel.blit(self.images_panel[3], (215, 0))
        # панель запуска ракет
        self.surface_panel.blit(self.images_panel[self.bullets_type + 4], (300, 0))
        if self.bullets_start > 0:  # значит еще не готов (охлаждается)
            self.bullets_start -= 1
            speed = self.bullets_start / self.bullets_start_speed * 100
            if 75 < speed <= 100:
                self.surface_panel.blit(self.images_panel[8], (300, 70))
            elif 50 < speed <= 75:
                self.surface_panel.blit(self.images_panel[9], (300, 70))
            elif 25 < speed <= 50:
                self.surface_panel.blit(self.images_panel[10], (300, 70))
            elif 0 < speed <= 25:
                self.surface_panel.blit(self.images_panel[11], (300, 70))
        else:
            self.surface_panel.blit(self.images_panel[12], (300, 70))
        # панель включения магнитного поля
        self.surface_panel.blit(self.images_panel[self.magnetic_field + 12], (450, 0))
        if self.magnetic_field_power > 0:  # если магнитное поле ВКЛ.
            self.magnetic_field_power -= 0.6 / self.magnetic_field  # то постоянно уменьшаем его заряд
            player.magnetic_field = True  # Передаем кораблю ВКЛ. Магнитное поле
        else:
            player.magnetic_field = False  # Передаем кораблю ОТКЛ. Магнитное поле
        pygame.draw.line(self.surface_panel, (2, 136, 255), (545, 56), (545, 56 - int(self.magnetic_field_power)), 4)
        # панель включения защитного поля
        if self.protective_field > 0:  # если защитное поле ВКЛ.
            self.protective_field -= 1  # то постоянно уменьшаем его время его работы
            self.surface_panel.blit(self.images_panel[17], (600, 0))
            player.protective_field = True  # Передаем кораблю ВКЛ. Защитное поле
        else:
            player.protective_field = False  # Передаем кораблю ОТКЛ. Защитное поле
            self.surface_panel.blit(self.images_panel[16], (600, 0))

    def pressed_panel(self, x, y):
        """События при клике на панели управления"""
        if 350 <= x < 780 and 800 <= y < 897:  # если клик на панели вообще
            if 350 <= x < 480 and self.bullets_start < 1:  # если клик на панели запуска ракет и запуск готов
                self.protective_field = 0  # отключаем защитное поле
                self.magnetic_field_power = 0  # отключаем магнитное поле
                Bullet(self.bullets_type, self.player, game.group_bullets, self.bullets_speed)  # запускаем ракету
                self.bullets_start = self.bullets_start_speed  # устанавливаем ожидание (типа охлаждение) после запуска
            elif 500 <= x < 630 and self.magnetic_field_power < 1:  # если клик на панели магнитного поля и оно не вкл.
                self.magnetic_field_power = 40  # включаем магнитное поле
                self.protective_field = 0  # и отключаем защитное
            elif 650 <= x < 780 and self.protective_field < 1:  # если клик на панели защитного поля и оно не вкл.
                self.protective_field = 100  # включаем защитное поле
                self.magnetic_field_power = 0  # и отключаем магнитное
        else:
            return

    def draw_panel(self, surface):
        surface.blit(self.surface_panel, (50, 800))


class Station(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images_station = [pygame.image.load(f"images/station{i}.png") for i in range(1, 4)]
        self.image = self.images_station[0]
        self.image_draw = self.image
        self.station_position_angle = 0  # угол вращения станции
        self.station_speed = 0.1  # скорость вращения
        self.station_health = 800  # кол-во жизней станции
        self.rect = self.image_draw.get_rect(center=(400, 400))
        self.mask = pygame.mask.from_surface(self.image_draw)
        self.generation_dark_hole = 0  # генерирует черные дыры если > 0
        self.generation_energy = 0  # # генерирует куски энергии если > 0
        self.hit = 0  # нанесенный урон по станции
        self.update()

    def update(self):
        if self.hit > 0:  # если получен урон по станции
            self.generation_energy = self.hit  # генерирует количество кусков энергии
            self.station_health -= self.hit * 5  # отнимает количество жизни
            if self.station_health < 0:
                game.interface.ui_end_game(1)
            self.hit = 0  # обнуление урона
        if not self.hit:  # если урона нет:
            self.station_position_angle = (self.station_position_angle - self.station_speed) % 360  # вращается
        if self.generation_dark_hole < 100:  # анимация подготовки к генерации черных дыр
            self.image = self.images_station[0]  # обычный вид
        elif 100 <= self.generation_dark_hole < 150 or 180 <= self.generation_dark_hole < 200:
            self.image = self.images_station[1]  # подсветка
        elif 150 <= self.generation_dark_hole < 180:
            self.image = self.images_station[2]  # раскрывается
        self.image_draw = pygame.transform.rotate(self.image, self.station_position_angle)
        self.rect = self.image_draw.get_rect(center=(400, 400))
        self.mask = pygame.mask.from_surface(self.image_draw)

    def draw_station(self, surface):
        surface.blit(self.image_draw, self.rect)
        pygame.draw.line(surface, (255, 0, 0), (0, 0), (self.station_health, 0), 5)  # линия жизни

    def generation(self):
        """Функция генерации объектов станцией"""
        if self.generation_energy > 0:  # если генерируется энергия
            if self.generation_dark_hole > 150:
                number_dark_hole = 6  # количество энергии выбивается больше, если попасть во время раскрытия станции
            else:
                number_dark_hole = 3
            self.generation_dark_hole = 0  # сбрасывается подготовка генерации черных дыр
            for _ in range(self.generation_energy * number_dark_hole):  # генерация энергии
                MoveObject('energy', game.group_energy, game.level)  # game.level это скорость объектов - ну вот так :)
            self.generation_energy = 0  # сброс генерации энергии
        self.generation_dark_hole += 1  # подготовка к генерации черных дыр
        if self.generation_dark_hole == 180:  # если время настало:
            for _ in range(game.level * 10):  # генерируем черные дыры
                MoveObject('dark_hole', game.group_dark_holes, game.level)  # game.level это скорость объектов
        if self.generation_dark_hole > 200:  # тайм-аут для анимации, иначе станция сразу гаснет
            self.generation_dark_hole = 0  # сбрасывается подготовка генерации черных дыр


class MoveObject(pygame.sprite.Sprite):
    def __init__(self, object_type, group, speed=1):
        super().__init__(game.all_sprites)
        self.cost = 0  # цена объекта, нужна если объект энергия
        self.position_angle_move = randint(0, 360)
        self.x = 400.0
        self.y = 400.0
        self.vx = round(sin(radians(self.position_angle_move)) * speed, 2)
        self.vy = round(cos(radians(self.position_angle_move)) * speed, 2)
        self.object_type = object_type
        if self.object_type == 'energy':
            self.cost = choice([1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3])  # случайная цена энергии
            self.image = game.images_move_object[self.cost]
        elif self.object_type == 'dark_hole':
            self.image = game.images_move_object[0]
        self.image = pygame.transform.rotate(self.image, self.position_angle_move)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(400, 400))
        self.move_object_kill = 0
        self.add(group)

    def update(self):
        if self.move_object_kill > 0:
            self.kill()
        else:
            self.x += self.vx
            self.y += self.vy
            self.rect.center = (self.x, self.y)
            if self.object_type == 'energy':  # если объект энергия
                for bullet in game.group_bullets:
                    if pygame.sprite.collide_mask(self, bullet):
                        if bullet.bullet_type == 1:  # сталкивается с ракетой тип 1
                            self.move_object_kill = 1  # то уничтожается
                            return
                if pygame.sprite.collide_mask(self, game.player):  # сталкивается с кораблем
                    if game.player.magnetic_field:  # и при этом включено магнитное поле
                        game.panel.energy_point += self.cost * 10  # добавляются очки в зависимости от цены энергии
                        Icons('plus', self.x, self.y)
                        self.kill()
            if self.object_type == 'dark_hole':  # если объект черная дыра
                for bullet in game.group_bullets:
                    if pygame.sprite.collide_mask(self, bullet):
                        if bullet.bullet_type == 3:  # сталкивается с ракетой тип 3
                            self.move_object_kill = 1  # то уничтожается
                            return
                if pygame.sprite.collide_mask(self, game.player):  # сталкивается с кораблем
                    if game.panel.protective_field:  # если включено защитное поле
                        self.vx, self.vy = -self.vx, -self.vy  # черная дыра отскакивает
                        return
                    else:
                        game.panel.magnetic_field_power = 0  # иначе отключается магнитное поле
                        game.panel.player_health -= game.level * 6  # И наносит урон кораблю равный уровню игры умн. 3
                        Icons('minus', self.x, self.y)
                        self.kill()
            if (800 < self.x or self.x < 0) or (1200 < self.y or self.y < 0):
                self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_type, player, group, speed=1):
        super().__init__(game.all_sprites)
        self.bullet_type = bullet_type
        self.x = player.position_x
        self.y = player.position_y
        self.bullet_position_angle = player.position_angle
        self.vx = -round(sin(radians(self.bullet_position_angle)) * speed, 2)
        self.vy = -round(cos(radians(self.bullet_position_angle)) * speed, 2)
        self.image = pygame.transform.rotate(game.images_bullet[self.bullet_type], self.bullet_position_angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.bullet_kill = 0
        self.add(group)

    def update(self):
        if self.bullet_kill == 2:
            self.kill()
            return
        elif self.bullet_kill == 1:  # анимация взрыва
            self.image = game.images_bullet[0]
            self.bullet_kill = 2
            return
        else:
            self.x += self.vx
            self.y += self.vy
            self.rect.center = (self.x, self.y)
            if self.bullet_type == 1:  # если снаряд 1 типа сталкивается с черной дырой он просто пропадает
                for dark_hole in game.group_dark_holes:
                    if pygame.sprite.collide_mask(self, dark_hole):
                        self.bullet_kill = 2
                        return
            if self.bullet_type == 1:  # если снаряд 1 типа сталкивается с энергией он взрывается
                for energy in game.group_energy:
                    if pygame.sprite.collide_mask(self, energy):
                        self.bullet_kill = 1
                        return
            if pygame.sprite.collide_mask(self, game.station):  # если снаряд сталкивается со станцией, то наносит урон
                game.station.hit = self.bullet_type  # количество урона передается станции
                self.bullet_kill = 1
                return
            if 390 <= self.x <= 410 and 390 <= self.y <= 410:
                self.kill()


class Icons(pygame.sprite.Sprite):
    def __init__(self, object_type, x, y):
        super().__init__(game.all_sprites)
        self.time_live = 27  # время жизни
        self.object_type = object_type
        self.x = x
        self.y = y
        if self.object_type == 'plus':
            self.image = game.images_move_object[4]
        elif self.object_type == 'minus':
            self.image = game.images_move_object[5]
        self.rect = self.image.get_rect(center=(self.x, self.y - 5))

    def update(self):
        if self.time_live < 1:
            self.kill()
        self.y -= 1
        self.time_live -= 1
        self.rect = self.image.get_rect(center=(self.x, self.y))


if __name__ == '__main__':
    game = SpaceHero()
    game.run_game()
