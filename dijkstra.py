
import time
import sys
import heapq

def dijkstra(graph, start_node):
    # we keep visitation count, thus convert the count to (1-frequency)
    start = time.time()
    nodes = list(graph.keys())
    visited = {}

    # We'll use this dict to save the cost of visiting each node and update it as we move along the graph
    shortest_path = {}

    shortest_path_heap = []

    # We'll use this dict to save the shortest known path to a node found so far
    previous_nodes = {}

    # We'll use max_value to initialize the "infinity" value of the unvisited nodes
    max_value = sys.maxsize
    for node in nodes:
        shortest_path[node] = max_value

        heapq.heappush(shortest_path_heap, (max_value, node))

    # However, we initialize the starting node's value with 0
    #shortest_path_heap.remove((max_value, start_node))
    shortest_path[start_node] = 0
    heapq.heappush(shortest_path_heap, (0, start_node))

    t_min = 0
    t_neighb = 0

    algo_steps = 0
    # The algorithm executes until we visit all nodes
    while len(shortest_path_heap) > 0:
        # The code block below finds the node with the lowest score
        t0 = time.time()

        cm_tuple = heapq.heappop(shortest_path_heap)
        current_min_node = cm_tuple[1]

        if current_min_node in visited:
            continue
        visited[current_min_node] = True

        #set current_min_node to min value of shortest_path.  

        #for node in unvisited_nodes:  # Iterate over the nodes
        #    if current_min_node == None:
        #        current_min_node = node
        #    elif shortest_path[node] < shortest_path[current_min_node]:
        #        current_min_node = node


        t_min += time.time() - t0

        t0 = time.time()

        if not current_min_node in graph:
            continue

        # The code block below retrieves the current node's neighbors and updates their distances
        neighbors = graph[current_min_node]
        for neighbor in neighbors:
            algo_steps += 1
            #print('neighbors', neighbors)
            #print('current min node', current_min_node)
            tentative_value = shortest_path[current_min_node] + 1#graph[current_min_node][neighbor]
            if neighbor in shortest_path:
                if tentative_value < shortest_path[neighbor]:

                    shortest_path[neighbor] = tentative_value
                    # We also update the best path to the current node
                    previous_nodes[neighbor] = current_min_node

                    heapq.heappush(shortest_path_heap, (tentative_value, neighbor))

        # After visiting its neighbors, we mark the node as "visited"
        #print('current_min_node', current_min_node)
        #print(len(unvisited_nodes), len(shortest_path_heap))
        #unvisited_nodes.remove(current_min_node)

        t_neighb += time.time() - t0

    end = time.time() - start
    #print('time to find min', t_min)
    #print('time to process neighbors', t_neighb)
    #print('end time', end)
    #raise Exception()
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



