from random import choice
from sys import exit

from settings import *
from timer import Timer


class Game:
    def __init__(self, get_next_shape, update_score):
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.game_surface.get_rect(topleft=(PADDING, PADDING))
        self.sprites = pygame.sprite.Group()

        self.get_next_shape = get_next_shape
        self.update_score = update_score

        self.line_surface = self.game_surface.copy()
        self.line_surface.fill((0, 255, 0))
        self.line_surface.set_colorkey((0, 255, 0))
        self.line_surface.set_alpha(0)

        self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]

        self.tetromino = Tetromino(
            choice(list(TETROMINOS.keys())),
            self.sprites,
            self.create_new_tetromino,
            self.field_data)

        self.down_speed = UPDATE_START_SPEED
        self.down_speed_faster = self.down_speed * 0.25
        self.down_pressed = False
        self.timers = {
            'vertical move': Timer(self.down_speed, True, self.move_down),
            'horizontal move': Timer(MOVE_WAIT_TIME),
            'rotate': Timer(ROTATE_WAIT_TIME)
        }

        self.timers['vertical move'].activate()

        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
            self.down_speed *= 0.75
            self.down_speed_faster = self.down_speed * 0.25
            self.timers['vertical move'].duration = self.down_speed

        self.update_score(self.current_lines, self.current_score, self.current_level)

    def check_game_over(self):
        for block in self.tetromino.blocks:
            if block.position.y < 0:
                exit()

    def create_new_tetromino(self):
        self.check_game_over()
        self.check_finished_rows()
        self.tetromino = Tetromino(
            self.get_next_shape(),
            self.sprites,
            self.create_new_tetromino,
            self.field_data)

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        self.tetromino.move_down()

    def draw_grid(self):
        for column in range(1, COLUMNS):
            x = column * CELL_SIZE
            pygame.draw.line(self.line_surface, GRAY, (x, 0), (x, self.game_surface.get_height()), 1)

        for row in range(1, ROWS):
            y = row * CELL_SIZE
            pygame.draw.line(self.line_surface, GRAY, (0, y), (self.game_surface.get_width(), y), 1)

        self.game_surface.blit(self.line_surface, (0, 0))

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.tetromino.move_horizontal(-1)
                self.timers['horizontal move'].activate()
            if keys[pygame.K_RIGHT]:
                self.tetromino.move_horizontal(1)
                self.timers['horizontal move'].activate()

        if not self.timers['rotate'].active:
            if keys[pygame.K_UP]:
                self.tetromino.rotate()
                self.timers['rotate'].activate()

        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers['vertical move'].duration = self.down_speed_faster

        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers['vertical move'].duration = self.down_speed

    def check_finished_rows(self):
        delete_rows = []
        for index, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(index)

        if delete_rows:
            for delete_row in delete_rows:
                for block in self.field_data[delete_row]:
                    block.kill()

                for row in self.field_data:
                    for block in row:
                        if block and block.position.y < delete_row:
                            block.position.y += 1

            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
            for block in self.sprites:
                self.field_data[int(block.position.y)][int(block.position.x)] = block

            self.calculate_score(len(delete_rows))

    def run_game(self):
        self.input()
        self.timer_update()
        self.sprites.update()

        self.game_surface.fill(GRAY)
        self.sprites.draw(self.game_surface)
        self.draw_grid()
        self.display_surface.blit(self.game_surface, (PADDING, PADDING))
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)


class Tetromino:
    def __init__(self, shape, group, create_new_tetromino, field_data):
        self.shape = shape
        self.block_positions = TETROMINOS[shape]['shape']
        self.block_color = TETROMINOS[shape]['color']
        self.create_new_tetromino = create_new_tetromino
        self.field_data = field_data

        self.blocks = [Block(group, position, self.block_color) for position in self.block_positions]

    def next_horizontal_move_collide(self, blocks, amount):
        collision_list = [block.horizontal_collide(int(block.position.x + amount), self.field_data) for block in
                          self.blocks]
        return True if any(collision_list) else False

    def next_vertical_move_collide(self, blocks, amount):
        collision_list = [block.vertical_collide(int(block.position.y + amount), self.field_data) for block in
                          self.blocks]
        return True if any(collision_list) else False

    def move_down(self):
        if not self.next_vertical_move_collide(self.blocks, 1):
            for block in self.blocks:
                block.position.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.position.y)][int(block.position.x)] = block
            self.create_new_tetromino()

    def move_horizontal(self, amount):
        if not self.next_horizontal_move_collide(self.blocks, amount):
            for block in self.blocks:
                block.position.x += amount

    def rotate(self):
        if self.shape != 'O':
            pivot_position = self.blocks[0].position
            new_block_position = [block.rotate(pivot_position) for block in self.blocks]
            for position in new_block_position:
                if position.x < 0 or position.x >= COLUMNS:
                    return

                if position.y >= ROWS:
                    return

                if self.field_data[int(position.y)][int(position.x)]:
                    return

            for index, block in enumerate(self.blocks):
                block.position = new_block_position[index]


class Block(pygame.sprite.Sprite):
    def __init__(self, group, position, color):
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)

        self.position = pygame.Vector2(position) + BLOCK_OFFSET
        self.rect = self.image.get_rect(topleft=self.position * CELL_SIZE)

    def update(self):
        self.rect.topleft = self.position * CELL_SIZE

    def horizontal_collide(self, x, field_data) -> bool:
        if not 0 <= x < COLUMNS:
            return True

        if field_data[int(self.position.y)][x]:
            return True

    def vertical_collide(self, y, field_data) -> bool:
        if y >= ROWS:
            return True

        if y >= 0 and field_data[y][int(self.position.x)]:
            return True

    def rotate(self, pivot_position):
        return pivot_position + (self.position - pivot_position).rotate(90)
