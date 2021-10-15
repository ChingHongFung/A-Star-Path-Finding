"""
Created on Thu Oct 14 18:15:08 2021

@author: ChingHongFung 
Iteration 2: Added in cost property - using the scroll button to add cost to a block
"""

import pygame
import math
from queue import PriorityQueue

from pygame.constants import MOUSEBUTTONDOWN

#WIDTH = 800
#WIN = pygame.display.set_mode((WIDTH, WIDTH))
#pygame.display.set_caption("A* Path Finding Algorithm")

RED = (230, 15, 15)
GREEN = (80, 190, 80)
BLUE = (15, 200, 220)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (195, 115, 50)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.cost = 1
        
    def get_pos(self):
        return self.row, self.col

    def get_cost(self):
        return self.cost
    
    def is_closed(self):
        return self.color == ORANGE
    
    def is_open(self):
        return self.color == BROWN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == YELLOW
    
    def is_end(self):
        return self.color == GREEN
    
    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = YELLOW
        
    def make_closed(self):
        self.color = ORANGE
        
    def make_open(self):
        self.color = BROWN
    
    def make_barrier(self):
        self.color = BLACK
        
    def make_end(self):
        self.color = GREEN
        
    def make_path(self):
        self.color = BLUE
    
    def add_cost(self):
        if self.color == BLACK:
            pass
        else:
            self.cost += 1
            r = self.color[0]
            g = self.color[1] - 20
            b = self.color[2] - 20
            if g < 0:
                r = g = b = 0
            self.color = (r, g, b)
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        
    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1 * neighbor.cost

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    #return False
    print("------------------------")
    print("There is no solution!!!!")
    pygame.quit()

def make_grid(rows, width):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid

def draw_grid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main():
    print("What do you want the grid spacing to be (Please pick a number below 50)?")
    rows = input()
    if rows == "":
        rows = 50
    else: 
        rows = int(rows)
    width = rows*15
    print("Instructions:")
    print("   1st left click selects the start point")
    print("   2nd left click selects the end point")
    print("   Left clicks after the first two select barriers")
    print("   Scroll click to add cost to a block (up to 13 times)")
    print("   Right click to reselect blocks")
    print("   Press space bar to start game")
    print("   Press c to clear board")
    win = pygame.display.set_mode((width, width))
    pygame.display.set_caption("A* Path Finding Algorithm")
    grid = make_grid(rows, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # LEFT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[1]: # MID
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                spot.add_cost()

            elif pygame.mouse.get_pressed()[2]: # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, rows, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, width)

    #return False
    pygame.quit()

# main(WIN, WIDTH)
main()