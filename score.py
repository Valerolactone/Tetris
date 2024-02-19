from settings import *
from os.path import join


class Score:
    def __init__(self):
        self.score_surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION - PADDING))
        self.rect = self.score_surface.get_rect(bottomright=(WINDOW_WIDTH - PADDING, WINDOW_HEIGHT - PADDING))
        self.display_surface = pygame.display.get_surface()

        self.font = pygame.font.Font(join('graphics', 'Russo_One.ttf'), 30)

        self.increment_height = self.score_surface.get_height() / 3

        self.score = 0
        self.level = 1
        self.lines = 0

    def display_text(self, position, text):
        text_surface = self.font.render(f'{text[0]}: {text[1]}', True, 'white')
        text_rect = text_surface.get_rect(center=position)
        self.score_surface.blit(text_surface, text_rect)

    def run_score(self):
        self.score_surface.fill(GRAY)
        for index, text in enumerate([('Score', self.score), ('Level', self.level), ('Lines', self.lines)]):
            x = self.score_surface.get_width() / 2
            y = self.increment_height / 2 + index * self.increment_height
            self.display_text((x, y), text)

        self.display_surface.blit(self.score_surface, self.rect)
        pygame.draw.rect(self.display_surface, LINE_COLOR, self.rect, 2, 2)
