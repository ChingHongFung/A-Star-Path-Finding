"""
Created on Thu Oct 14 18:15:08 2021

@author: ChingHongFung 
Final Iteration: Added two separate portal connections; refined heuristic algorithm so at any iteration, it seeks for the lowest h score between current neighbor and the
closest portal before looking for the h score to the end point. This maximises the chance of uncovering a shorter path with fewer iterations.
"""

import pygame
import math
from queue import PriorityQueue

from pygame.constants import MOUSEBUTTONDOWN

# Initialising RGB values for colours used in the visualisaiton
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
PINK = (255, 0, 190)

# Create a class called spot that holds attributes such as x,y coordinate location, color, surrounding neighbors, cost of each square, portal status, etc.
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

    def get_neighbors(self):
        return self.neighbors
    
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

    def is_portal_pink(self):
        return self.color == PINK

    def is_portal_purple(self):
        return self.color == PURPLE
    
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
    
    def make_portal_pink(self):
        self.color = PINK

    def make_portal_purple(self):
        self.color = PURPLE

    # Add cost to a block; path could still traverse through but with a higher cost (i.e. takes additional 'steps' to walk through)
    def add_cost(self): 
        if self.color == BLACK:
            pass
        else:
            self.cost += 1
            r = self.color[0]
            g = self.color[1] - 20
            b = self.color[2] - 20
            # Once cost reaches over 13 (20*13=260 over the colour range for visualisation), set block as BLACK i.e. make_barrier()
            if g < 0:
                r = g = b = 0
            self.color = (r, g, b)
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    # Look at each spot and evaluate its neighbors; if a neighbor is a barrier or it falls out of the grid space, then it is not added to the neighbors list
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

# Use Manhattan distance as a heuristic funciton to estimate the shortest distance between two points; Do not use Euclidean distance becase path cannnot be diagonal
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)

# Redraw path from end to start once a solution is found
def reconstruct_path(came_from, current, draw):
    # Count the number of steps needed to reconstruct path (i.e. the lowest number of steps to get from start to end)
    steps = 0
    while current in came_from:
        steps += 1 * current.cost
        current = came_from[current]
        current.make_path()
        draw()
    return steps

# Create two lists for the two sets of portals to be used in add_portal_neighbors()
def check_portal(grid):
    portals_pink=[]
    portals_purple=[]
    for row in grid:
        for spot in row: 
            if spot.color == PINK:
                portals_pink.append(spot)
            elif spot.color == PURPLE:
                portals_purple.append(spot)
    return portals_pink, portals_purple

# Essentially add additional neighbors to those adjacent to portals
def add_portal_neighbors(portals):
    for i in portals:
        for j in portals:
            for currentNeighbor in i.neighbors:
                # Do not add additional neighbors if i==j (already a neighbor!)
                if i != j:
                    for extraNeighbor in j.neighbors:
                        # Add the additional neighbors from other portals
                        currentNeighbor.neighbors.append(extraNeighbor)

# Main Astar algorithm here             
def algorithm(draw, grid, start, end, portals_pink, portals_purple):
    count = 0
    # Use a priority queue data structure to store f score, count (when a point is added), and node; queue will give lowest f score node when prompted
    open_set = PriorityQueue() 
    open_set.put((0, count, start)) # Set the start point with f score of 0
    came_from = {} # A dictionary to store key value pairs linking how each node is reached from previous nodes so path drawing could be carried out in the end
    # Set g score and f score to infinity to initialise
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start} # A dictionary to keep track of which nodes that have not been considered

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Allow pygame interface to be terminated
                pygame.quit()

        current = open_set.get()[2] # Get current node that is to be considered
        open_set_hash.remove(current)  # Remove is from open_set_hash as it will no longer be considered again

        # Solution is found if current == end
        if current == end:
            steps = reconstruct_path(came_from, end, draw)
            print("Total number of steps needed = ", steps)
            # Repaint the colours of start, end and portals for better visualisation
            end.make_end()
            start.make_start()
            for portal in portals_pink:
                portal.make_portal_pink()
            for portal in portals_purple:
                portal.make_portal_purple()
            return True

        for neighbor in current.neighbors:
            # temp_g_score is added with the cost of each neighbor block in mind
            temp_g_score = g_score[current] + 1 * neighbor.cost

            # If temp_g_score is lower than previously recorded, meaning we found a path with lower cost to get to this neighbour, update its score
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current # Track where the lower-cost path came from
                g_score[neighbor] = temp_g_score # Update score

                # Use min_portal_h to store the lowest heuristic function between current and closest portal
                min_portal_h = float("inf")
                for portal in portals_pink:
                    # Do not optimise by attempting to reach closed portals
                    if portal.is_closed():
                        pass
                    else: 
                        temp_h = h(neighbor.get_pos(), portal.get_pos())
                        if temp_h < min_portal_h:
                            min_portal_h = temp_h
                for portal in portals_purple:
                    if portal.is_closed():
                        pass
                    else:
                        temp_h = h(neighbor.get_pos(), portal.get_pos())
                        if temp_h < min_portal_h:
                            min_portal_h = temp_h

                # Take f_score to be the smaller of f score between current and end or f score between current and a close portal
                f_score[neighbor] = min(temp_g_score + h(neighbor.get_pos(), end.get_pos()), temp_g_score + min_portal_h)

                if neighbor not in open_set_hash:
                    count += 1 # Increment the count for next node to be stored
                    open_set.put((f_score[neighbor], count, neighbor)) 
                    open_set_hash.add(neighbor) # Add new neighbors to the open_set_hash dictionary
                    neighbor.make_open() # Open neighbors to be considered next

        draw()

        if current != start:
            current.make_closed() # Close off already-considered nodes

    #return False
    print("------------------------")
    print("There is no solution!!!!")
    pygame.quit()

# Calculate the grid spacing and add spot instances to each grid point
def make_grid(rows, width):
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid

# Draw grid lines with gray lines
def draw_grid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

# Paint the grid white
def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

# Get the position of where the mouse click is
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

# Main function to run all the functions
def main():
    print("What do you want the grid spacing to be (Please pick a number below 50)?")
    rows = input()
    if rows == "":
        rows = 50
    else: 
        rows = int(rows)
    width = rows*15
    print("-----------------------------------------------")
    print("Instructions:")
    print("   1st left click selects the start point")
    print("   2nd left click selects the end point")
    print("   Left clicks after the first two select barriers")
    print("   Scroll click to add cost to a block (up to 13 times)")
    print("   Key 'p' to add portal to a block")
    print("   Key 'p' on existing portal to switch it to the other type of portal")
    print("   Right click to reselect blocks")
    print("   Press space bar to start game")
    print("   Press c to clear board")
    print("-----------------------------------------------")

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

            # Left clicks to select start, end and barriers
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

            # Use mid scroll key to add cost to blocks
            elif pygame.mouse.get_pressed()[1]: # MID
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                spot.add_cost()

            # Right click to reinitialise a block
            elif pygame.mouse.get_pressed()[2]: # RIGHT
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            # Use key 'p' to add portals to grid; click on an existing portal turns it to the other type
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, rows, width)
                    spot = grid[row][col]
                    if spot.is_portal_purple() or spot.color == WHITE:
                        spot.make_portal_pink()
                    elif spot.is_portal_pink() or spot.color == WHITE:
                        spot.make_portal_purple()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    portals_pink, portals_purple = check_portal(grid)
                    for row in grid:
                        for spot in row:
                            # Calculate all the neighbors of each spot in the grid
                            spot.update_neighbors(grid) 
                    # Add additional neighbors to those adjacent to portals
                    add_portal_neighbors(portals_pink) 
                    add_portal_neighbors(portals_purple)       

                    algorithm(lambda: draw(win, grid, rows, width), grid, start, end, portals_pink, portals_purple)
                
                # Key c to restart board
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(rows, width)

    #return False
    pygame.quit()

# main(WIN, WIDTH)
main()