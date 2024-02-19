from settings import *
from pygame.image import load
from os import path


class Preview:
    def __init__(self):
        self.preview_surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION))
        self.rect = self.preview_surface.get_rect(topright=(WINDOW_WIDTH - PADDING, PADDING))
        self.display_surface = pygame.display.get_surface()

        self.shape_surfaces = {shape: load(path.join('graphics', f'{shape}.png')).convert_alpha()
                               for shape in TETROMINOS.keys()}

        self.increment_height = self.preview_surface.get_height() / 2

    def display_pieces(self, shapes):
        for index, shape in enumerate(shapes):
            shape_surface = self.shape_surfaces[shape]
            x = self.preview_surface.get_width() / 2
            y = self.increment_height / 2 + index * self.increment_height
            rect = shape_surface.get_rect(center=(x, y))
            self.preview_surface.blit(shape_surface, rect)

    def run_preview(self, next_shapes):
        self.preview_surface.fill(GRAY)
        self.display_pieces(next_shapes)
        self.display_surface.blit(self.preview_surface, self.rect)
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)
