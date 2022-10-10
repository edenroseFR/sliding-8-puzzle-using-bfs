import pygame
from .sprite import *
from .settings import *
from time import sleep
from solver.main import randomize_puzzle, solve_puzzle


class Game:
    def __init__(self, actions=[], initial=[], solution=[]):
        """
        :param actions: actions taken to shuffle the puzzle
        :param initial: the shuffled state
        :param solution: action to take in order to solve the puzzle
        """
        pygame.init()
        self.initial = initial or [1,2,3,4,5,6,7,8,0]
        self.solution = solution
        self.key_moves = ''
        self.show_clicked = False
        self.solve_clicked = False

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

    def create_game(self):
        """
        This function will create a 2D list that will hold all the grids
        """
        if self.initial:
            return [
                self.initial[:3],
                self.initial[3:6],
                self.initial[6:9]
            ]

        # Create a 2D grid
        grid = []
        tiles = [x+1 for x in range(GAME_SIZE**2)]
        for x in range(GAME_SIZE):
            row = tiles[(x)*GAME_SIZE:GAME_SIZE*(x+1)]
            grid.append(row)

        # Set the bottom right grid to zero
        grid[-1][-1] = 0

        return grid

    def draw_tiles(self):
        self.tiles = []
        self.initial = []
        for row, x in enumerate(self.tiles_grid):
            self.tiles.append([])
            for col, tile in enumerate(x):
                if tile != 0:
                    self.tiles[row].append(Tile(self, col, row, str(tile)))
                else:
                    self.tiles[row].append(Tile(self, col, row, 'empty'))

                try:
                    self.initial.append(int(tile))
                except ValueError:
                    self.initial.append(0)

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_grid = self.create_game()
        self.grid_completed = [1,2,3,4,5,6,7,8,0]
        self.puzzle_solved = True
        self.start_shuffle = False
        self.shuffle_times = 0
        self.solving = False
        self.draw_tiles()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.draw()
            self.update()
            self.events()

    def update(self):
        self.all_sprites.update()

        if self.start_shuffle:
            prev_move = self.solution[0] if len(self.solution) == 1 else ''
            self.solution = [randomize_puzzle(self.initial, prev_move)]
            self.execute_solution()
            self.shuffle_times += 1
            if self.shuffle_times > 10:
                self.start_shuffle = False
                self.shuffle_times = 0

        if self.initial == self.grid_completed:
            self.puzzle_solved = True
            self.show_clicked  = False
            self.solution = []

        if len(self.key_moves) > 0 and self.solving:
            self.solution = [self.key_moves[0]]
            self.execute_solution()

        if len(self.key_moves) == 0:
            self.solving = False


    def draw(self):
        """
        This is where all the graphics are drawn
        """
        # Set window background
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.draw_UI()
        pygame.display.flip()

    def draw_UI(self):
        # Navbar
        self.nav_rect = UIElement(0, 0)
        self.nav_rect.draw_nav(self.screen, BGCOLOR, WIDTH, NAV_HEIGHT+30)
        self.nav_rect.draw_nav(self.screen, TILE_COLOR, WIDTH, NAV_HEIGHT)

        # Buttons
        img, rect = Game.get_img_info(LOGO)
        w,h = rect.width, rect.height
        rect.x = 10
        rect.y = (NAV_HEIGHT - h) / 2
        self.logo = Button()
        self.logo.draw_img(self.screen, img, rect)

        img, rect = Game.get_img_info(SHUFFLE_BTN)
        w,h = rect.width, rect.height
        rect.x = WIDTH - w - 10
        rect.y = (NAV_HEIGHT - h) / 2
        self.shuffle = Button()
        self.shuffle.draw_img(self.screen, img, rect)
        if self.shuffle.hover():
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        self.solve = Button()
        if self.show_clicked:
            img, rect = Game.get_img_info(SOLVE_BTN)
        elif self.puzzle_solved:
            img, rect = Game.get_img_info(SOLVED_BTN)
        else:
            img, rect = Game.get_img_info(SHOW_BTN)
        w,h = rect.width, rect.height
        rect.x = ((WIDTH - w) / 2) + 10
        rect.y = HEIGHT - NAV_HEIGHT - (TILESIZE*GAME_SIZE) - (TOP_MARGIN * 100 - 80)
        self.solve.draw_img(self.screen, img, rect)
        if self.solve.hover() and not self.puzzle_solved:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        img, rect = Game.get_img_info(HELP_BTN)
        w,h = rect.width, rect.height
        rect.x = WIDTH - w - 20
        rect.y = HEIGHT - h - 20
        self.help = Button()
        self.help.draw_img(self.screen, img, rect)

        self.key = UIElement(self.solve.x, self.solve.y, ' '.join(self.key_moves))
        self.key.write_text(self.screen)

        if self.help.hover():
            img, rect = Game.get_img_info(HELP_TEXT)
            w,h = rect.width, rect.height
            rect.x = int((WIDTH - w) / 2)
            rect.y = int(HEIGHT - (NAV_HEIGHT*2))
            self.help_text = Button()
            self.help_text.draw_img(self.screen, img, rect)

    @staticmethod
    def get_img_info(img):
        btn = pygame.image.load(img)
        rect = btn.get_rect()
        return btn, rect

    def move_tile(self, clicked_tile, row, col, s=False):
        """
        :param clicked_tile:
        :param row:
        :param col:
        :param s: the passed solution (computer-generated)
        :param k: the key pressed
        """
        if s == 'R'\
            or (clicked_tile.right() and col-1 >= 0 and self.tiles_grid[row][col-1] == 0):

            self.tiles_grid[row][col-1] = int(clicked_tile.text)
            self.tiles_grid[row][col] = 0
            self.update_key_moves('R')

        elif s == 'L'\
            or (clicked_tile.left() and col+1 < GAME_SIZE and self.tiles_grid[row][col+1] == 0):

            self.tiles_grid[row][col+1] = int(clicked_tile.text)
            self.tiles_grid[row][col] = 0
            self.update_key_moves('L')

        elif s == 'U'\
            or (clicked_tile.up() and row+1 < GAME_SIZE and self.tiles_grid[row+1][col] == 0):

            self.tiles_grid[row+1][col] = int(clicked_tile.text)
            self.tiles_grid[row][col] = 0
            self.update_key_moves('U')

        elif s == 'D'\
            or (clicked_tile.down() and row-1 >= 0 and self.tiles_grid[row-1][col] == 0):

            self.tiles_grid[row-1][col] = int(clicked_tile.text)
            self.tiles_grid[row][col] = 0
            self.update_key_moves('D')

        else:
            print('Invalid move')


    def update_key_moves(self, action):
        if len(self.key_moves) > 0 and self.key_moves[0] == action:
            self.key_moves = self.key_moves[2:]


    def events(self):
        """
        This function is responsible for detecting events in the game.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for row, tiles in enumerate(self.tiles):
                    for col, tile in enumerate(tiles):
                        if tile.click(mouse_x, mouse_y) and \
                            tile.text != 'empty':
                            self.move_tile(tile, row, col)
                            self.draw_tiles()

                if self.shuffle.click(mouse_x, mouse_y):
                    self.key_moves = ''
                    self.show_clicked = False
                    self.start_shuffle = True
                    self.puzzle_solved = False

                if self.solve.click(mouse_x, mouse_y):
                    if not self.puzzle_solved:
                        if self.show_clicked:
                            self.show_clicked = False
                            self.solve_clicked = True
                        else:
                            self.show_clicked = True
                            self.solve_clicked = False
                        self.solution = solve_puzzle(self.initial)
                        print('Solution found!')
                        self.key_moves = ' '.join(self.solution)

                if self.solve_clicked:
                    self.solving = True

            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.execute_solution()

    def execute_solution(self):
        """
        This function will execute the list of
        actions in the self.solution array.
        """
        if self.solution:
            # search_solution(self.initial)
            for action in self.solution:
                x = self.initial.index(0)
                if action == 'U':
                    row = int(x / 3) - 1
                elif action == 'D':
                    row = int(x / 3) + 1
                else:
                    row = int(x / 3)
                if action == 'R':
                    col = int(x % 3) + 1
                elif action == 'L':
                    col = int(x % 3) - 1
                else:
                    col = int(x % 3)
                tile = self.tiles[row][col]
                self.move_tile(tile, row, col, action)
                sleep(100/1000)
                self.draw_tiles()

def start_game(actions=[], initial_state=[], solution=[]):
    game = Game(actions, initial_state, solution)

    while True:
        pygame.time.delay(1500)
        game.new()
        game.run()