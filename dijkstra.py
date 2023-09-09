
import time
import sys

def dijkstra(graph, start_node):
    # we keep visitation count, thus convert the count to (1-frequency)
    start = time.time()
    unvisited_nodes = list(graph.keys())

    # We'll use this dict to save the cost of visiting each node and update it as we move along the graph
    shortest_path = {}

    # We'll use this dict to save the shortest known path to a node found so far
    previous_nodes = {}

    # We'll use max_value to initialize the "infinity" value of the unvisited nodes
    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    # However, we initialize the starting node's value with 0
    shortest_path[start_node] = 0

    algo_steps = 0
    # The algorithm executes until we visit all nodes
    while unvisited_nodes:
        # The code block below finds the node with the lowest score
        current_min_node = None
        for node in unvisited_nodes:  # Iterate over the nodes
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        # The code block below retrieves the current node's neighbors and updates their distances
        neighbors = graph[current_min_node]
        for neighbor in neighbors:
            algo_steps += 1
            #print('neighbors', neighbors)
            #print('current min node', current_min_node)
            tentative_value = shortest_path[current_min_node] + 1#graph[current_min_node][neighbor]
            if neighbor in shortest_path and tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node

        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    end = time.time() - start
    return previous_nodes, shortest_path, [algo_steps, end]



def backtrack(paths, start, goal):
    p = [goal]
    n = goal

    while True:
        n = paths[n]
        p.append(n)
        if n == start:
            break

    p = list(reversed(p))

    return p



