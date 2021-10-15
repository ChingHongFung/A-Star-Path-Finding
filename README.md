# A-Star-Path-Finding

This project is inspired by a youtuber "Tech with Tim" who implements the A-star-path-finding algorithm using Python. Visualisation is done using the Pygame package to show how the algorithm considers each negihboring nodes in each iteration. More information about the algorithm could be found on https://en.wikipedia.org/wiki/A*_search_algorithm.

#### Basic overview
![equation](https://user-images.githubusercontent.com/91271318/137495297-7b3dde30-8212-4182-bf15-2be5a79811eb.png)
Essentially, the algorithm seeks for the shortest path by considering a value f_score of all available neighbors next to a current node. For each neighbor, f_score is composed of the g_score and h_score. g_score measures the cost of the path (the number of steps needed) to travel from the start to this neighbor; h_score is a heuristic function that estimates the cheapest cost to reach the end point from this neighbor. By sequentially, considering the f_score of each node, we could insert these values into a priority queue which allows the next iteration to priotise searching at the node with lowest f_score. Each iteration updates the corresponding scores while removing the already-considered nodes from the queue until a solution is found. 

#### Heuristic function
![Manhattan_distance](https://user-images.githubusercontent.com/91271318/137496871-1b7b3446-afb1-465c-9230-c9e8fd46c85c.png)

(https://en.wikipedia.org/wiki/Taxicab_geometry)
For my implementation, I used the Manhattan distance as a lowerbound heuristic funciton instead of other measures such as Euclidean. This is because the path could not traverse diagonally so the Manhattan distance is a more conservative estimation for paths along the x,y directions. This heuristic is very simple to implement as we only need to find the absolute difference in Cartesian coordinates of the two points. 

#### Improvement to progamme by "Tech with Tim"
source.py is the original implementation of the algorithm. I added a few extra features and refined certain aspects of the programme including custom grid sizing, additional costs to certain nodes, portals between nodes and refined optimisaion heuristic function.

#### Grid spacing
![grid_spcaing](https://user-images.githubusercontent.com/91271318/137500839-105d0726-c39f-469f-9606-ba1df9ae3758.png)
Running main() allows you to pick a grid size of your own choice. Instructions are printed to show how the pathfinding game works.

#### Basic visualisation with no obstacless
##### update_neighbors()
![update_neighbors](https://user-images.githubusercontent.com/91271318/137501410-33db8d7c-12c9-40c0-a28d-9c65e1112ae9.png)

update_neighbors is called to go through each spot instance of the grid to assign neighbors to each node. Barriers and nodes outside the grid are disregarded. Neighbors are stored as an attribute of each spot instance making it easy to retrieve.

Light brown colours show nodes that have been considered and thrown out of the queue; dark brown shows nodes that are open and on the queue waiting to be considered. Queuing system depends on the f_score of each node which is stored in the priority queue structure. 

Video: Basic run with no additonal elements

https://user-images.githubusercontent.com/91271318/137501043-ec380f5f-9ea7-4967-907f-d7ad6b7e376e.mp4

#### Additional costs
#### add_cost()
![add_cost](https://user-images.githubusercontent.com/91271318/137504502-2a0061b9-400e-4092-854e-70896bcc8bca.png)

Additional costs are added to nodes upon mid scroll click. Values are again stored as an attribute within the nodes. The more red a block is, the higher the cost. In the first video, notice when the open nodes reach the red nodes at the bottom left, the algorithm first looks away at other nodes with cost of 1 (white nodes) on the right hand side. This is because, additional costs increased the g_score of the red nodes making their overall f_scores higher so they fall into lower posiitons in the queue. After some iterations, as the open nodes spread to futher nodes on the right, the algorithm jumps back to the bottom left as they have lower f_scores. Finally, a path is found that traverses through the bottom left.

Video: Costly nodes 1

https://user-images.githubusercontent.com/91271318/137501820-34b18d7e-643b-4561-b437-c22d5a879253.mp4

In the second video, we could again see that algorithm bounces back and forth between the 'red path' around the edge and the 'white snake path'. Again the algorithm always looks for the node with the lowest f_score at each iteration. The high red costs along the edges resulted in a final shortest path that goes around the snake.

Video: Costly nodes 2

https://user-images.githubusercontent.com/91271318/137501831-a6c9c066-89df-40b5-9317-325fc6754b6e.mp4

#### Portals
Portals could be added by hovering the mouse over a node and tapping key 'p'. This turns a node into a portal. Portals of the same type could be connected. Essentially, what this does is neighbors adjacent to each portal would have direct access to neighbours of portals of the same type. By clicking on an existing portal one one type again using 'p', it changes the type of that portal to the alternative. This way only portals of the same type could be connected.



